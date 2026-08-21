import json
from collections.abc import Callable, Iterator
from time import sleep as default_sleep
from typing import Any, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from shared.tools import ToolCall

from .config import LLMSettings
from .errors import LLMConfigurationError, LLMProviderError, LLMRateLimitError
from .models import (
    LLMRequest,
    LLMResult,
    LLMStreamEvent,
    ProviderCapabilities,
    StructuredLLMResult,
    TokenUsage,
    ToolResultContinuation,
    ToolSelectionResult,
)
from .provider import LLMProvider
from .retry import RetryPolicy, call_with_retry, is_transient_error

StructuredOutputT = TypeVar("StructuredOutputT", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    name = "openai"
    capabilities = ProviderCapabilities(tool_calling=True)

    def __init__(
        self,
        settings: LLMSettings,
        *,
        client: Any | None = None,
        sleep: Callable[[float], None] = default_sleep,
    ):
        if not settings.openai_api_key:
            raise LLMConfigurationError(
                "LLM_PROVIDER is 'openai', but OPENAI_API_KEY is not configured."
            )
        if not settings.openai_model:
            raise LLMConfigurationError(
                "LLM_PROVIDER is 'openai', but OPENAI_MODEL is not configured."
            )

        self.model = settings.openai_model
        self._sleep = sleep
        self._retry_policy = RetryPolicy(
            max_retries=settings.max_retries,
            base_delay_seconds=settings.retry_base_seconds,
        )
        self._client = client or OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.timeout_seconds,
            max_retries=0,
        )

    def _request_kwargs(self, request: LLMRequest) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "input": request.input,
        }
        if request.instructions:
            kwargs["instructions"] = request.instructions
        if request.tools:
            kwargs["tools"] = request.tools
        if request.tool_choice is not None:
            kwargs["tool_choice"] = request.tool_choice
        return kwargs

    def _usage(self, response: Any) -> TokenUsage:
        usage = getattr(response, "usage", None)
        if usage is None:
            return TokenUsage()

        def read(name: str) -> int | None:
            if isinstance(usage, dict):
                return usage.get(name)
            return getattr(usage, name, None)

        return TokenUsage(
            input_tokens=read("input_tokens"),
            output_tokens=read("output_tokens"),
            total_tokens=read("total_tokens"),
        )

    def _provider_error(self, exc: Exception) -> LLMProviderError:
        if getattr(exc, "status_code", None) == 429:
            return LLMRateLimitError(
                "OpenAI rate limit exceeded after bounded retries."
            )
        return LLMProviderError(f"OpenAI request failed: {exc}")

    def generate(self, request: LLMRequest) -> LLMResult:
        try:
            response = call_with_retry(
                lambda: self._client.responses.create(**self._request_kwargs(request)),
                self._retry_policy,
                self._sleep,
            )
        except Exception as exc:
            raise self._provider_error(exc) from exc

        return LLMResult(
            output=response.output_text,
            request_id=response.id,
            provider=self.name,
            model=getattr(response, "model", self.model),
            usage=self._usage(response),
        )

    def generate_structured(
        self,
        request: LLMRequest,
        response_model: type[StructuredOutputT],
    ) -> StructuredLLMResult[StructuredOutputT]:
        kwargs = self._request_kwargs(request)
        kwargs["text_format"] = response_model

        try:
            response = call_with_retry(
                lambda: self._client.responses.parse(**kwargs),
                self._retry_policy,
                self._sleep,
            )
            output = response_model.model_validate(response.output_parsed)
        except ValidationError as exc:
            raise LLMProviderError(
                "OpenAI returned a response that did not match the required schema."
            ) from exc
        except Exception as exc:
            raise self._provider_error(exc) from exc

        return StructuredLLMResult(
            output=output,
            request_id=response.id,
            provider=self.name,
            model=getattr(response, "model", self.model),
            usage=self._usage(response),
        )

    def select_tools(self, request: LLMRequest) -> ToolSelectionResult:
        try:
            response = call_with_retry(
                lambda: self._client.responses.create(**self._request_kwargs(request)),
                self._retry_policy,
                self._sleep,
            )
        except Exception as exc:
            raise self._provider_error(exc) from exc

        tool_calls = []
        for item in getattr(response, "output", []):
            item_type = (
                item.get("type")
                if isinstance(item, dict)
                else getattr(item, "type", None)
            )
            if item_type != "function_call":
                continue
            if isinstance(item, dict):
                call_id = item.get("call_id")
                name = item.get("name")
                raw_arguments = item.get("arguments")
            else:
                call_id = item.call_id
                name = item.name
                raw_arguments = item.arguments
            arguments_valid = True
            try:
                arguments = json.loads(raw_arguments)
                if not isinstance(arguments, dict):
                    arguments = {}
                    arguments_valid = False
            except (TypeError, json.JSONDecodeError):
                arguments = {}
                arguments_valid = False
            tool_calls.append(
                ToolCall(
                    call_id=call_id,
                    name=name,
                    arguments=arguments,
                    arguments_valid=arguments_valid,
                )
            )

        return ToolSelectionResult(
            tool_calls=tool_calls,
            output=getattr(response, "output_text", "") or "",
            request_id=response.id,
            provider=self.name,
            model=getattr(response, "model", self.model),
            usage=self._usage(response),
        )

    def generate_structured_with_tool_results(
        self,
        request: LLMRequest,
        continuation: ToolResultContinuation,
        response_model: type[StructuredOutputT],
    ) -> StructuredLLMResult[StructuredOutputT]:
        tool_outputs = [
            {
                "type": "function_call_output",
                "call_id": result.call_id,
                "output": result.model_dump_json(),
            }
            for result in continuation.results
        ]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "input": tool_outputs,
            "previous_response_id": continuation.previous_response_id,
            "text_format": response_model,
        }
        if request.instructions:
            kwargs["instructions"] = request.instructions

        try:
            response = call_with_retry(
                lambda: self._client.responses.parse(**kwargs),
                self._retry_policy,
                self._sleep,
            )
            output = response_model.model_validate(response.output_parsed)
        except ValidationError as exc:
            raise LLMProviderError(
                "OpenAI returned a response that did not match the required schema."
            ) from exc
        except Exception as exc:
            raise self._provider_error(exc) from exc

        return StructuredLLMResult(
            output=output,
            request_id=response.id,
            provider=self.name,
            model=getattr(response, "model", self.model),
            usage=self._usage(response),
        )

    def stream(self, request: LLMRequest) -> Iterator[LLMStreamEvent]:
        retry_number = 0

        while True:
            emitted_text = False
            try:
                with self._client.responses.stream(
                    **self._request_kwargs(request)
                ) as stream:
                    for event in stream:
                        if event.type == "response.output_text.delta":
                            emitted_text = True
                            yield LLMStreamEvent(
                                type="delta",
                                delta=event.delta,
                                provider=self.name,
                                model=self.model,
                            )

                    response = stream.get_final_response()
                    yield LLMStreamEvent(
                        type="completed",
                        request_id=response.id,
                        provider=self.name,
                        model=getattr(response, "model", self.model),
                        usage=self._usage(response),
                    )
                    return
            except Exception as exc:
                can_retry = (
                    not emitted_text
                    and is_transient_error(exc)
                    and retry_number < self._retry_policy.max_retries
                )
                if not can_retry:
                    raise self._provider_error(exc) from exc
                self._sleep(self._retry_policy.delay_for(retry_number))
                retry_number += 1
