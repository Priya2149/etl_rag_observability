from agent_service.app.services import agentic_workflow
from agent_service.app.services.agentic_workflow import (
    classify_route,
    run_agentic_query,
)
from shared.llm import (
    LLMRequest,
    ProviderCapabilities,
    StructuredLLMResult,
    TokenUsage,
    ToolSelectionResult,
)
from shared.llm.local import LocalRetrievalProvider
from shared.tools import (
    ApplicationTool,
    SearchDocumentsInput,
    SearchDocumentsOutput,
    ToolCall,
    ToolRegistry,
)


def search_registry(handler=None):
    handler = handler or (
        lambda payload: SearchDocumentsOutput(
            query=payload.query,
            retrieved_chunks=[{"content": "CPU-only embeddings", "metadata": {}}],
            sources=["architecture.txt"],
            evaluation={"risk_level": "low"},
            summary="Found CPU-only embedding evidence.",
        )
    )
    return ToolRegistry(
        [
            ApplicationTool(
                name="search_documents",
                description="Search indexed documents.",
                input_model=SearchDocumentsInput,
                output_model=SearchDocumentsOutput,
                handler=handler,
            )
        ]
    )


class FakeOpenAIProvider:
    name = "openai"
    model = "fake-model"
    capabilities = ProviderCapabilities(tool_calling=True)

    def __init__(self, calls, selection_output=""):
        self.calls = calls
        self.selection_output = selection_output
        self.continuations = []

    def select_tools(self, request: LLMRequest):
        self.selection_request = request
        return ToolSelectionResult(
            tool_calls=self.calls,
            output=self.selection_output,
            request_id="resp_select",
            provider=self.name,
            model=self.model,
            usage=TokenUsage(input_tokens=6, output_tokens=2, total_tokens=8),
        )

    def generate_structured_with_tool_results(
        self, request, continuation, response_model
    ):
        self.continuations.append(continuation)
        return StructuredLLMResult(
            output=response_model(
                answer="The documents confirm CPU-only embeddings.",
                sources=["architecture.txt", "invented.txt"],
            ),
            request_id="resp_final",
            provider=self.name,
            model=self.model,
            usage=TokenUsage(input_tokens=8, output_tokens=4, total_tokens=12),
        )


def test_route_selection_uses_meaningful_conditional_categories():
    assert classify_route("Search indexed documents for CPU embeddings") == "rag"
    assert classify_route("What columns are in the latest dataset?") == "dataset_schema"
    assert classify_route("What quality problems were detected?") == "dataset_profile"
    assert classify_route("Is ETL run 4 completed?") == "pipeline"
    assert classify_route("Hello") == "general"


def test_openai_tool_call_round_trip_returns_structured_grounded_response():
    provider = FakeOpenAIProvider(
        [
            ToolCall(
                call_id="call-search",
                name="search_documents",
                arguments={"query": "CPU embeddings"},
            )
        ]
    )

    response = run_agentic_query(
        "Search indexed documents for CPU embeddings",
        provider=provider,
        registry=search_registry(),
        request_id="request-1",
    )

    assert response.answer == "The documents confirm CPU-only embeddings."
    assert response.sources == ["architecture.txt"]
    assert response.tools_used == ["search_documents"]
    assert response.workflow.selected_route == "rag"
    assert response.workflow.tool_call_count == 1
    assert response.workflow.usage["total_tokens"] == 20
    assert provider.continuations[0].previous_response_id == "resp_select"


def test_openai_can_return_multiple_tool_results_in_one_bounded_iteration():
    provider = FakeOpenAIProvider(
        [
            ToolCall(
                call_id="one", name="search_documents", arguments={"query": "one"}
            ),
            ToolCall(
                call_id="two", name="search_documents", arguments={"query": "two"}
            ),
        ]
    )

    response = run_agentic_query(
        "Find document evidence",
        provider=provider,
        registry=search_registry(),
    )

    assert response.workflow.tool_call_count == 2
    assert response.workflow.tool_iterations == 1
    assert len(provider.continuations[0].results) == 2


def test_no_tool_path_skips_execution_and_returns_model_answer():
    provider = FakeOpenAIProvider(
        [], selection_output="No repository lookup is needed."
    )

    response = run_agentic_query(
        "Hello",
        provider=provider,
        registry=search_registry(),
    )

    assert response.answer == "No repository lookup is needed."
    assert response.tools_used == []
    assert response.workflow.tool_iterations == 0
    assert provider.continuations == []


def test_tool_failure_is_returned_without_crashing_the_graph():
    def fail(_):
        raise RuntimeError("secret internal traceback")

    provider = FakeOpenAIProvider(
        [
            ToolCall(
                call_id="failed",
                name="search_documents",
                arguments={"query": "evidence"},
            )
        ]
    )

    response = run_agentic_query(
        "Search documents for evidence",
        provider=provider,
        registry=search_registry(fail),
    )

    assert response.workflow.errors == ["Tool 'search_documents' failed."]
    assert "secret" not in str(response.model_dump())


def test_local_mode_uses_deterministic_tool_path_without_openai():
    response = run_agentic_query(
        "Search indexed documents for embeddings",
        provider=LocalRetrievalProvider(name="none"),
        registry=search_registry(),
    )

    assert "CPU-only embeddings" in response.answer
    assert response.provider == "none"
    assert response.tools_used == ["search_documents"]


def test_zero_iteration_limit_prevents_tool_execution(monkeypatch):
    monkeypatch.setattr(agentic_workflow, "AGENT_MAX_TOOL_ITERATIONS", 0)
    executed = []
    provider = FakeOpenAIProvider(
        [
            ToolCall(
                call_id="bounded",
                name="search_documents",
                arguments={"query": "bounded"},
            )
        ]
    )

    response = run_agentic_query(
        "Search documents for bounded execution",
        provider=provider,
        registry=search_registry(lambda payload: executed.append(payload)),
    )

    assert executed == []
    assert "Tool iteration limit reached." in response.workflow.errors
    assert response.workflow.tool_iterations == 0
