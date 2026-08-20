from rag_service.app.services.answer import build_rag_request, generate_rag_answer
from shared.llm import (
    GroundedAnswer,
    LLMRequest,
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
