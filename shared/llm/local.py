from collections.abc import Iterator
from typing import TypeVar
from uuid import uuid4

from pydantic import BaseModel

from .models import (
    LLMRequest,
    LLMResult,
    LLMStreamEvent,
    ProviderCapabilities,
    StructuredLLMResult,
    TokenUsage,
)
from .provider import LLMProvider

StructuredOutputT = TypeVar("StructuredOutputT", bound=BaseModel)


class LocalRetrievalProvider(LLMProvider):
    """Zero-cost provider that preserves the original retrieval-only answer path."""

    capabilities = ProviderCapabilities(tool_calling=False)

    def __init__(self, name: str = "local"):
        self.name = name
        self.model = "retrieval-only"

    def _answer(self, request: LLMRequest) -> str:
        if not request.context:
            return "No relevant content found."
        return f"Answer based on retrieved content:\n{request.context[0]}"

    def generate(self, request: LLMRequest) -> LLMResult:
        return LLMResult(
            output=self._answer(request),
            request_id=f"{self.name}-{uuid4()}",
            provider=self.name,
            model=self.model,
            usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        )

    def generate_structured(
        self,
        request: LLMRequest,
        response_model: type[StructuredOutputT],
    ) -> StructuredLLMResult[StructuredOutputT]:
        output = response_model.model_validate(
            {"answer": self._answer(request), "sources": request.sources}
        )
        return StructuredLLMResult(
            output=output,
            request_id=f"{self.name}-{uuid4()}",
            provider=self.name,
            model=self.model,
            usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        )

    def stream(self, request: LLMRequest) -> Iterator[LLMStreamEvent]:
        request_id = f"{self.name}-{uuid4()}"
        answer = self._answer(request)

        for word in answer.splitlines(keepends=True):
            yield LLMStreamEvent(
                type="delta",
                delta=word,
                provider=self.name,
                model=self.model,
            )

        yield LLMStreamEvent(
            type="completed",
            request_id=request_id,
            provider=self.name,
            model=self.model,
            usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        )
