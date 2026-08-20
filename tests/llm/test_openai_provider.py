from types import SimpleNamespace

import pytest

import shared.llm.openai_provider as openai_provider_module
from shared.llm import (
    GroundedAnswer,
    LLMProviderError,
    LLMRateLimitError,
    LLMRequest,
    LLMSettings,
)
from shared.llm.openai_provider import OpenAIProvider


class ProviderStatusError(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"provider status {status_code}")
        self.status_code = status_code


class FakeResponses:
    def __init__(self, *, parse_results=None, create_result=None, streams=None):
        self.parse_results = list(parse_results or [])
        self.create_result = create_result
        self.streams = list(streams or [])
        self.parse_calls = []
        self.create_calls = []
        self.stream_calls = []

    def parse(self, **kwargs):
        self.parse_calls.append(kwargs)
        result = self.parse_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def create(self, **kwargs):
        self.create_calls.append(kwargs)
        return self.create_result

    def stream(self, **kwargs):
        self.stream_calls.append(kwargs)
        result = self.streams.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class FakeStream:
    def __init__(self, events, response):
        self.events = events
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def __iter__(self):
        return iter(self.events)

    def get_final_response(self):
        return self.response


def settings(**overrides):
    values = {
        "provider": "openai",
        "openai_api_key": "test-key",
        "openai_model": "test-model",
        "timeout_seconds": 7,
        "max_retries": 2,
        "retry_base_seconds": 0.1,
    }
    values.update(overrides)
    return LLMSettings(**values)


def parsed_response(output=None):
    return SimpleNamespace(
        id="resp_123",
        model="test-model-2026-01-01",
        output_parsed=output or GroundedAnswer(
            answer="Grounded response", sources=["guide.txt"]
        ),
        usage=SimpleNamespace(
            input_tokens=12,
            output_tokens=5,
            total_tokens=17,
        ),
    )


def test_openai_structured_request_and_token_metadata():
    responses = FakeResponses(parse_results=[parsed_response()])
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses)
    )
    request = LLMRequest(
        input="Question and context",
        instructions="Use only context",
        sources=["guide.txt"],
    )

    result = provider.generate_structured(request, GroundedAnswer)

    assert responses.parse_calls == [
        {
            "model": "test-model",
            "input": "Question and context",
            "instructions": "Use only context",
            "text_format": GroundedAnswer,
        }
    ]
    assert result.output.answer == "Grounded response"
    assert result.request_id == "resp_123"
    assert result.provider == "openai"
    assert result.model == "test-model-2026-01-01"
    assert result.usage.model_dump() == {
        "input_tokens": 12,
        "output_tokens": 5,
        "total_tokens": 17,
    }


def test_openai_client_uses_configured_timeout_and_central_retries(monkeypatch):
    captured = {}

    def fake_openai(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(responses=FakeResponses())

    monkeypatch.setattr(openai_provider_module, "OpenAI", fake_openai)

    OpenAIProvider(settings(timeout_seconds=9))

    assert captured == {
        "api_key": "test-key",
        "timeout": 9,
        "max_retries": 0,
    }


def test_standard_generation_passes_future_tool_configuration():
    response = SimpleNamespace(
        id="resp_standard",
        model="test-model",
        output_text="Normal response",
        usage=None,
    )
    responses = FakeResponses(create_result=response)
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses)
    )
    request = LLMRequest(
        input="Call when needed",
        tools=[{"type": "function", "name": "lookup"}],
        tool_choice="auto",
    )

    result = provider.generate(request)

    assert responses.create_calls[0]["tools"] == request.tools
    assert responses.create_calls[0]["tool_choice"] == "auto"
    assert result.output == "Normal response"


def test_transient_timeout_is_retried_with_exponential_backoff():
    responses = FakeResponses(
        parse_results=[ProviderStatusError(408), parsed_response()]
    )
    delays = []
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses), sleep=delays.append
    )

    provider.generate_structured(LLMRequest(input="retry me"), GroundedAnswer)

    assert len(responses.parse_calls) == 2
    assert delays == [0.1]


def test_rate_limit_uses_bounded_retries_and_clear_error():
    responses = FakeResponses(
        parse_results=[
            ProviderStatusError(429),
            ProviderStatusError(429),
            ProviderStatusError(429),
        ]
    )
    delays = []
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses), sleep=delays.append
    )

    with pytest.raises(LLMRateLimitError, match="bounded retries"):
        provider.generate_structured(LLMRequest(input="limited"), GroundedAnswer)

    assert len(responses.parse_calls) == 3
    assert delays == [0.1, 0.2]


def test_permanent_authentication_error_is_not_retried():
    responses = FakeResponses(parse_results=[ProviderStatusError(401)])
    delays = []
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses), sleep=delays.append
    )

    with pytest.raises(LLMProviderError, match="status 401"):
        provider.generate_structured(LLMRequest(input="do not retry"), GroundedAnswer)

    assert len(responses.parse_calls) == 1
    assert delays == []


def test_invalid_structured_output_fails_validation():
    response = parsed_response(output=SimpleNamespace(sources=[]))
    responses = FakeResponses(parse_results=[response])
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses)
    )

    with pytest.raises(LLMProviderError, match="required schema"):
        provider.generate_structured(LLMRequest(input="validate"), GroundedAnswer)


def test_streaming_emits_deltas_and_final_usage():
    final_response = SimpleNamespace(
        id="resp_stream",
        model="test-model",
        usage={"input_tokens": 4, "output_tokens": 2, "total_tokens": 6},
    )
    stream = FakeStream(
        events=[
            SimpleNamespace(type="response.created"),
            SimpleNamespace(type="response.output_text.delta", delta="Hello "),
            SimpleNamespace(type="response.output_text.delta", delta="world"),
        ],
        response=final_response,
    )
    responses = FakeResponses(streams=[stream])
    provider = OpenAIProvider(
        settings(), client=SimpleNamespace(responses=responses)
    )

    events = list(provider.stream(LLMRequest(input="stream")))

    assert [event.delta for event in events[:-1]] == ["Hello ", "world"]
    assert events[-1].type == "completed"
    assert events[-1].request_id == "resp_stream"
    assert events[-1].usage.total_tokens == 6
