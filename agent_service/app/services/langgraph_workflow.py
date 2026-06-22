from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END

from app.services.planner_agent import run_planner
from app.services.etl_agent import run_etl_agent
from app.services.rag_agent import run_rag_agent
from app.services.evaluator_agent import run_evaluator
from app.services.report_agent import build_report
from app.services.tool_client import get_etl_run_details, ask_rag_service


class AgentState(TypedDict, total=False):
    input_payload: dict
    planner_result: dict
    etl_result: dict
    rag_result: dict
    evaluation_result: dict
    final_report: dict
    status: str
    current_step: str
    error_message: Optional[str]


def planner_node(state: AgentState) -> AgentState:
    payload = state.get("input_payload", {})
    state["planner_result"] = run_planner(payload)
    state["current_step"] = "etl_context_fetch"
    return state


def etl_node(state: AgentState) -> AgentState:
    payload = state.get("input_payload", {})
    state["etl_result"] = run_etl_agent(payload, get_etl_run_details)
    state["current_step"] = "rag_retrieval"
    return state


def rag_node(state: AgentState) -> AgentState:
    payload = state.get("input_payload", {})
    state["rag_result"] = run_rag_agent(payload, ask_rag_service)
    state["current_step"] = "evaluation"
    return state


def evaluator_node(state: AgentState) -> AgentState:
    state["evaluation_result"] = run_evaluator(
        state.get("etl_result", {}),
        state.get("rag_result", {}),
    )
    state["status"] = "waiting_for_approval"
    state["current_step"] = "human_review"
    return state


def report_node(state: AgentState) -> AgentState:
    state["final_report"] = build_report(
        planner_result=state.get("planner_result", {}),
        etl_result=state.get("etl_result", {}),
        rag_result=state.get("rag_result", {}),
        evaluation_result=state.get("evaluation_result", {}),
    )
    state["status"] = "completed"
    state["current_step"] = "finished"
    return state


def build_langgraph_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("etl_agent", etl_node)
    graph.add_node("rag_agent", rag_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "etl_agent")
    graph.add_edge("etl_agent", "rag_agent")
    graph.add_edge("rag_agent", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()


def run_langgraph_until_approval(input_payload: dict) -> AgentState:
    workflow = build_langgraph_workflow()

    initial_state: AgentState = {
        "input_payload": input_payload,
        "status": "running",
        "current_step": "planning",
    }

    return workflow.invoke(initial_state)


def run_langgraph_report(state: AgentState) -> AgentState:
    state = report_node(state)
    return state