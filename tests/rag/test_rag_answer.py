import asyncio
import importlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import ModuleType

import pytest

from rag_service.app.services.answer import build_rag_request, generate_rag_answer
from shared.llm import (
    GroundedAnswer,
    LLMRequest,
    LLMStreamEvent,
    ProviderCapabilities,
    StructuredLLMResult,
    TokenUsage,
)
from shared.llm.local import LocalRetrievalProvider
from shared.llm.provider import LLMProvider


def retrieval_result():
    return {
        "answer": "original",
        "retrieved_chunks": [
            {
                "content": "The deployment uses CPU embeddings.",
                "metadata": {"source": "architecture.txt"},
                "distance": 0.2,
            }
        ],
        "retrieved_count": 1,
        "chunks_used": 1,
        "source_files": ["architecture.txt"],
        "best_distance": 0.2,
        "risk_level": "low",
        "evaluation_status": "good",
        "warning_flags": [],
    }


class FakeStructuredProvider(LLMProvider):
    name = "fake"
    model = "fake-model"
    capabilities = ProviderCapabilities()

    def generate(self, request):
        raise NotImplementedError

    def generate_structured(self, request, response_model):
        output = response_model(
            answer="A typed grounded answer.",
            sources=["architecture.txt", "invented.txt"],
        )
        return StructuredLLMResult(
            output=output,
            request_id="fake-request",
            provider=self.name,
            model=self.model,
            usage=TokenUsage(input_tokens=8, output_tokens=4, total_tokens=12),
        )

    def stream(self, request):
        return iter(())


@pytest.fixture
def rag_routes_module(monkeypatch):
    existing_app_modules = {
        name for name in sys.modules if name == "app" or name.startswith("app.")
    }
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "rag_service"))

    ingest_module = ModuleType("app.services.ingest")
    ingest_module.ingest_document = lambda _path: {}
    ingest_module.save_uploaded_file = lambda _file: ""
    retrieve_module = ModuleType("app.services.retrieve")
    retrieve_module.query_documents = lambda _query: retrieval_result()
    monkeypatch.setitem(sys.modules, "app.services.ingest", ingest_module)
    monkeypatch.setitem(sys.modules, "app.services.retrieve", retrieve_module)

    module = importlib.import_module("app.routes.rag")
    yield module

    added_modules = {
        name
        for name in sys.modules
        if (name == "app" or name.startswith("app."))
        and name not in existing_app_modules
    }
    for module_name in added_modules:
        sys.modules.pop(module_name, None)


def test_rag_request_contains_question_context_and_sources():
    request = build_rag_request("How are embeddings run?", retrieval_result())

    assert isinstance(request, LLMRequest)
    assert "How are embeddings run?" in request.input
    assert "The deployment uses CPU embeddings." in request.input
    assert request.sources == ["architecture.txt"]


def test_structured_rag_answer_rejects_invented_sources():
    result = generate_rag_answer(
        "How are embeddings run?",
        retrieval_result(),
        provider=FakeStructuredProvider(),
    )

    assert isinstance(result.output, GroundedAnswer)
    assert result.output.answer == "A typed grounded answer."
    assert result.output.sources == ["architecture.txt"]
    assert result.usage.total_tokens == 12


def test_local_provider_preserves_existing_rag_answer_behavior():
    result = generate_rag_answer(
        "How are embeddings run?",
        retrieval_result(),
        provider=LocalRetrievalProvider(name="none"),
    )

    assert result.output.answer == (
        "Answer based on retrieved content:\n"
        "The deployment uses CPU embeddings."
    )
    assert result.output.sources == ["architecture.txt"]
    assert result.provider == "none"
    assert result.usage.total_tokens == 0


def test_streaming_endpoint_emits_ordered_sse_events(
    monkeypatch, rag_routes_module
):
    async def consume(response):
        return [chunk async for chunk in response.body_iterator]

    class StreamingProvider:
        name = "fake"
        model = "fake-model"

        def stream(self, _request):
            yield LLMStreamEvent(
                type="delta", delta="CPU ", provider=self.name, model=self.model
            )
            yield LLMStreamEvent(
                type="delta", delta="embeddings", provider=self.name, model=self.model
            )
            yield LLMStreamEvent(
                type="completed",
                request_id="stream-request",
                provider=self.name,
                model=self.model,
                usage=TokenUsage(input_tokens=4, output_tokens=2, total_tokens=6),
            )

    rag_routes = rag_routes_module
    monkeypatch.setattr(rag_routes, "get_configured_provider", StreamingProvider)
    monkeypatch.setattr(rag_routes, "query_documents", lambda _query: retrieval_result())

    response = rag_routes.ask_question_stream(
        rag_routes.QueryRequest(query="How are embeddings run?")
    )
    with ThreadPoolExecutor(max_workers=1) as executor:
        chunks = executor.submit(asyncio.run, consume(response)).result()
    response_text = "".join(
        chunk.decode() if isinstance(chunk, bytes) else chunk for chunk in chunks
    )

    events = []
    for block in response_text.strip().split("\n\n"):
        lines = block.splitlines()
        events.append((lines[0].removeprefix("event: "), json.loads(lines[1][6:])))

    assert response.media_type == "text/event-stream"
    assert [event for event, _payload in events] == [
        "metadata",
        "delta",
        "delta",
        "completed",
    ]
    assert [payload["text"] for event, payload in events if event == "delta"] == [
        "CPU ",
        "embeddings",
    ]
    assert events[-1][1]["request_id"] == "stream-request"
    assert events[-1][1]["usage"]["total_tokens"] == 6
