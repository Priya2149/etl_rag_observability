from typing import Literal, TypedDict
from uuid import uuid4

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from shared.llm import (
    LLMProvider,
    LLMRequest,
    TokenUsage,
    ToolResultContinuation,
    get_configured_provider,
)
from shared.tools import ToolCall, ToolExecutionResult, ToolRegistry

from ..config import (
    AGENT_MAX_TOOL_CALLS,
    AGENT_MAX_TOOL_ITERATIONS,
    AGENT_RECURSION_LIMIT,
)
from ..schemas import AgentQueryResponse, AgentWorkflowMetadata
from .application_tools import build_application_tool_registry

AgentRoute = Literal["rag", "dataset_schema", "dataset_profile", "pipeline", "general"]

ROUTE_TO_TOOLS: dict[AgentRoute, list[str]] = {
    "rag": ["search_documents"],
    "dataset_schema": ["get_dataset_schema", "get_dataset_profile"],
    "dataset_profile": [
        "get_dataset_profile",
        "get_dataset_schema",
        "get_pipeline_status",
    ],
    "pipeline": ["get_pipeline_status", "get_dataset_profile"],
    "general": [
        "search_documents",
        "get_dataset_schema",
        "get_dataset_profile",
        "get_pipeline_status",
    ],
}

TOOL_SELECTION_INSTRUCTIONS = """Select only the repository tools needed to answer the user.
Use null run_id when the user asks about the latest ETL run. You may select multiple
tools when needed. Do not invent identifiers. If no repository tool is needed, answer
directly. Never request SQL, shell commands, file access, or secrets."""

SYNTHESIS_INSTRUCTIONS = """Answer using only the supplied tool results. Clearly state
when a tool failed or evidence is unavailable. Return only the requested structured
answer and source identifiers. Do not expose internal reasoning or stack traces."""


class AgentAnswerContent(BaseModel):
    answer: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)


class AgenticState(TypedDict, total=False):
    request_id: str
    user_query: str
    selected_route: AgentRoute
    messages: list[dict[str, str]]
    tool_calls: list[ToolCall]
    tool_results: list[ToolExecutionResult]
    retrieved_sources: list[str]
    final_answer: str
    errors: list[str]
    retries: int
    tool_iterations: int
    max_tool_iterations: int
    selection_response_id: str
    provider_request_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


def classify_route(query: str) -> AgentRoute:
    normalized = query.lower()
    if any(
        term in normalized for term in ("document", "indexed", "search", "evidence")
    ):
        return "rag"
    if any(term in normalized for term in ("schema", "column", "field", "data type")):
        return "dataset_schema"
    if any(
        term in normalized
        for term in ("quality", "profile", "anomal", "missing", "duplicate")
    ):
        return "dataset_profile"
    if any(term in normalized for term in ("pipeline", "etl run", "job", "status")):
        return "pipeline"
    return "general"


def _usage_update(state: AgenticState, usage: TokenUsage) -> dict[str, int]:
    return {
        "input_tokens": state.get("input_tokens", 0) + (usage.input_tokens or 0),
        "output_tokens": state.get("output_tokens", 0) + (usage.output_tokens or 0),
        "total_tokens": state.get("total_tokens", 0) + (usage.total_tokens or 0),
    }


def _local_calls(route: AgentRoute, query: str) -> list[ToolCall]:
    arguments = {"run_id": None}
    if route == "rag":
        return [
            ToolCall(
                call_id="local-search",
                name="search_documents",
                arguments={"query": query},
            )
        ]
    if route == "dataset_schema":
        return [
            ToolCall(
                call_id="local-schema", name="get_dataset_schema", arguments=arguments
            )
        ]
    if route == "dataset_profile":
        return [
            ToolCall(
                call_id="local-profile", name="get_dataset_profile", arguments=arguments
            )
        ]
    if route == "pipeline":
        return [
            ToolCall(
                call_id="local-status", name="get_pipeline_status", arguments=arguments
            )
        ]
    return []


def _local_answer(results: list[ToolExecutionResult]) -> str:
    failures = [
        result.error for result in results if not result.success and result.error
    ]
    if failures:
        return "The requested capability could not be completed: " + " ".join(failures)

    parts = []
    for result in results:
        if not result.data:
            continue
        if result.name == "search_documents":
            chunks = result.data.get("retrieved_chunks", [])
            evidence = [chunk.get("content", "") for chunk in chunks[:3]]
            if evidence:
                parts.append("Retrieved evidence:\n" + "\n\n".join(evidence))
                continue
        parts.append(result.data.get("summary", ""))
    return "\n\n".join(part for part in parts if part) or (
        "No repository tool was needed. Local mode does not generate an ungrounded answer."
    )


def build_agentic_workflow(provider: LLMProvider, registry: ToolRegistry):
    def route_node(state: AgenticState) -> AgenticState:
        route = classify_route(state["user_query"])
        return {
            "selected_route": route,
            "messages": [{"role": "user", "content": state["user_query"]}],
        }

    def provider_path(_: AgenticState) -> str:
        return "openai" if provider.capabilities.tool_calling else "local"

    def select_tools_node(state: AgenticState) -> AgenticState:
        route = state["selected_route"]
        request = LLMRequest(
            input=state["user_query"],
            instructions=TOOL_SELECTION_INSTRUCTIONS,
            tools=registry.definitions(ROUTE_TO_TOOLS[route]),
            tool_choice="auto",
        )
        try:
            selection = provider.select_tools(request)
        except Exception:  # noqa: BLE001
            return {
                "tool_calls": [],
                "errors": [*state.get("errors", []), "LLM tool selection failed."],
            }
        return {
            "tool_calls": selection.tool_calls,
            "selection_response_id": selection.request_id,
            "provider_request_id": selection.request_id,
            "messages": [
                *state.get("messages", []),
                {"role": "assistant", "content": selection.output},
            ],
            **_usage_update(state, selection.usage),
        }

    def select_local_node(state: AgenticState) -> AgenticState:
        return {
            "tool_calls": _local_calls(state["selected_route"], state["user_query"])
        }

    def selected_path(state: AgenticState) -> str:
        return "execute" if state.get("tool_calls") else "no_tool"

    def execute_tools_node(state: AgenticState) -> AgenticState:
        if state.get("tool_iterations", 0) >= state["max_tool_iterations"]:
            return {
                "tool_calls": [],
                "errors": [*state.get("errors", []), "Tool iteration limit reached."],
            }

        calls = state.get("tool_calls", [])
        bounded_calls = calls[:AGENT_MAX_TOOL_CALLS]
        errors = list(state.get("errors", []))
        if len(calls) > len(bounded_calls):
            errors.append("Tool call limit reached; extra calls were not executed.")
        results = [registry.execute(call) for call in bounded_calls]
        errors.extend(result.error for result in results if result.error)
        sources = list(
            dict.fromkeys(source for result in results for source in result.sources)
        )
        return {
            "tool_results": results,
            "retrieved_sources": sources,
            "tool_iterations": state.get("tool_iterations", 0) + 1,
            "retries": sum(result.retries for result in results),
            "errors": errors,
        }

    def synthesize_node(state: AgenticState) -> AgenticState:
        results = state.get("tool_results", [])
        if not provider.capabilities.tool_calling:
            return {"final_answer": _local_answer(results)}
        if not results:
            selection_text = ""
            if state.get("messages"):
                selection_text = state["messages"][-1].get("content", "")
            return {"final_answer": selection_text or _local_answer(results)}

        request = LLMRequest(
            input=state["user_query"],
            instructions=SYNTHESIS_INSTRUCTIONS,
            sources=state.get("retrieved_sources", []),
        )
        continuation = ToolResultContinuation(
            previous_response_id=state["selection_response_id"],
            results=results,
        )
        try:
            generation = provider.generate_structured_with_tool_results(
                request, continuation, AgentAnswerContent
            )
        except Exception:  # noqa: BLE001
            return {
                "final_answer": _local_answer(results),
                "errors": [*state.get("errors", []), "LLM synthesis failed."],
            }

        allowed_sources = set(state.get("retrieved_sources", []))
        sources = [
            source for source in generation.output.sources if source in allowed_sources
        ]
        return {
            "final_answer": generation.output.answer,
            "retrieved_sources": sources,
            "provider_request_id": generation.request_id,
            **_usage_update(state, generation.usage),
        }

    def validate_node(state: AgenticState) -> AgenticState:
        answer = state.get("final_answer", "").strip()
        if answer:
            return {"final_answer": answer}
        return {
            "final_answer": "The workflow completed without an answer.",
            "errors": [*state.get("errors", []), "Final answer validation failed."],
        }

    graph = StateGraph(AgenticState)
    graph.add_node("route", route_node)
    graph.add_node("select_tools", select_tools_node)
    graph.add_node("select_local", select_local_node)
    graph.add_node("execute_tools", execute_tools_node)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("validate", validate_node)
    graph.set_entry_point("route")
    graph.add_conditional_edges(
        "route", provider_path, {"openai": "select_tools", "local": "select_local"}
    )
    graph.add_conditional_edges(
        "select_tools",
        selected_path,
        {"execute": "execute_tools", "no_tool": "synthesize"},
    )
    graph.add_conditional_edges(
        "select_local",
        selected_path,
        {"execute": "execute_tools", "no_tool": "synthesize"},
    )
    graph.add_edge("execute_tools", "synthesize")
    graph.add_edge("synthesize", "validate")
    graph.add_edge("validate", END)
    return graph.compile()


def run_agentic_query(
    query: str,
    *,
    provider: LLMProvider | None = None,
    registry: ToolRegistry | None = None,
    request_id: str | None = None,
) -> AgentQueryResponse:
    provider = provider or get_configured_provider()
    registry = registry or build_application_tool_registry()
    workflow = build_agentic_workflow(provider, registry)
    initial_state: AgenticState = {
        "request_id": request_id or str(uuid4()),
        "user_query": query,
        "tool_calls": [],
        "tool_results": [],
        "retrieved_sources": [],
        "errors": [],
        "retries": 0,
        "tool_iterations": 0,
        "max_tool_iterations": max(0, AGENT_MAX_TOOL_ITERATIONS),
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }
    state = workflow.invoke(
        initial_state, config={"recursion_limit": AGENT_RECURSION_LIMIT}
    )
    results = state.get("tool_results", [])
    return AgentQueryResponse(
        answer=state["final_answer"],
        sources=state.get("retrieved_sources", []),
        tools_used=[result.name for result in results],
        request_id=state["request_id"],
        provider=provider.name,
        model=provider.model,
        workflow=AgentWorkflowMetadata(
            selected_route=state["selected_route"],
            tool_call_count=len(results),
            tool_execution_duration_ms=sum(result.duration_ms for result in results),
            tool_iterations=state.get("tool_iterations", 0),
            retries=state.get("retries", 0),
            errors=state.get("errors", []),
            usage={
                "input_tokens": state.get("input_tokens", 0),
                "output_tokens": state.get("output_tokens", 0),
                "total_tokens": state.get("total_tokens", 0),
            },
        ),
    )
