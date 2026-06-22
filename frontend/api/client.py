from __future__ import annotations

from typing import Any
import requests

from config.settings import ETL_BASE_URL, RAG_BASE_URL, OBS_BASE_URL


TIMEOUT_SECONDS = 60

AGENT_BASE_URL = "http://agent_service:8000"


def create_agent_workflow(dataset_id=None, question=None):
    payload = {
        "dataset_id": dataset_id,
        "question": question,
    }

    response = requests.post(
        f"{AGENT_BASE_URL}/agent/workflow",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def get_agent_workflow(workflow_id: int):
    response = requests.get(
        f"{AGENT_BASE_URL}/agent/workflow/{workflow_id}",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def approve_agent_workflow(workflow_id: int):
    response = requests.post(
        f"{AGENT_BASE_URL}/agent/workflow/{workflow_id}/approve",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)

def _handle_response(response: requests.Response) -> Any:
    response.raise_for_status()
    return response.json()


# ---------------- ETL ----------------
def upload_csv(file) -> Any:
    files = {"file": (file.name, file.getvalue(), "text/csv")}
    response = requests.post(
        f"{ETL_BASE_URL}/etl/upload",
        files=files,
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def get_etl_runs() -> Any:
    response = requests.get(f"{ETL_BASE_URL}/etl/runs", timeout=TIMEOUT_SECONDS)
    return _handle_response(response)


def get_etl_run_details(run_id: int) -> Any:
    response = requests.get(
        f"{ETL_BASE_URL}/etl/runs/{run_id}",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


# ---------------- RAG ----------------
def upload_document(file) -> Any:
    files = {"file": (file.name, file.getvalue(), "text/plain")}
    response = requests.post(
        f"{RAG_BASE_URL}/rag/upload",
        files=files,
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def ask_rag(query: str) -> Any:
    response = requests.post(
        f"{RAG_BASE_URL}/rag/ask",
        json={"query": query},
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def get_rag_documents() -> Any:
    response = requests.get(f"{RAG_BASE_URL}/rag/documents", timeout=TIMEOUT_SECONDS)
    return _handle_response(response)


def get_rag_runs() -> Any:
    response = requests.get(f"{RAG_BASE_URL}/rag/runs", timeout=TIMEOUT_SECONDS)
    return _handle_response(response)


def get_rag_run_details(run_id: int) -> Any:
    response = requests.get(
        f"{RAG_BASE_URL}/rag/runs/{run_id}",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


# ---------------- Observability ----------------
def get_overview() -> Any:
    response = requests.get(
        f"{OBS_BASE_URL}/observability/overview",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def get_etl_summary() -> Any:
    response = requests.get(
        f"{OBS_BASE_URL}/observability/etl-summary",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def get_rag_summary() -> Any:
    response = requests.get(
        f"{OBS_BASE_URL}/observability/rag-summary",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def get_recent_failures() -> Any:
    response = requests.get(
        f"{OBS_BASE_URL}/observability/recent-failures",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)

def list_agent_workflows():
    response = requests.get(
        f"{AGENT_BASE_URL}/agent/workflows",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def reject_agent_workflow(workflow_id: int):
    response = requests.post(
        f"{AGENT_BASE_URL}/agent/workflow/{workflow_id}/reject",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)


def retry_agent_workflow(workflow_id: int):
    response = requests.post(
        f"{AGENT_BASE_URL}/agent/workflow/{workflow_id}/retry",
        timeout=TIMEOUT_SECONDS,
    )
    return _handle_response(response)