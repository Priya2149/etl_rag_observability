import requests

from ..config import ETL_BASE_URL, RAG_BASE_URL, REQUEST_TIMEOUT


class ServiceToolError(RuntimeError):
    pass


def _json(response, service_name: str):
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        if response.status_code == 404:
            raise ServiceToolError(f"{service_name} resource was not found.") from exc
        raise ServiceToolError(f"{service_name} returned an error.") from exc


def get_etl_runs():
    try:
        response = requests.get(
            f"{ETL_BASE_URL}/etl/runs",
            timeout=REQUEST_TIMEOUT,
        )
        return _json(response, "ETL service")
    except requests.exceptions.Timeout as exc:
        raise ServiceToolError("ETL service request timed out.") from exc
    except requests.exceptions.RequestException as exc:
        raise ServiceToolError("ETL service is unavailable.") from exc


def get_etl_run_details(run_id: int):
    try:
        response = requests.get(
            f"{ETL_BASE_URL}/etl/runs/{run_id}",
            timeout=REQUEST_TIMEOUT,
        )
        return _json(response, "ETL run")

    except requests.exceptions.Timeout as exc:
        raise ServiceToolError("ETL service request timed out.") from exc
    except requests.exceptions.RequestException as exc:
        raise ServiceToolError("ETL service is unavailable.") from exc


def ask_rag_service(question: str):
    try:
        response = requests.post(
            f"{RAG_BASE_URL}/rag/ask",
            json={"query": question},
            timeout=REQUEST_TIMEOUT,
        )
        return _json(response, "RAG service")

    except requests.exceptions.Timeout as exc:
        raise ServiceToolError("RAG service request timed out.") from exc
    except requests.exceptions.RequestException as exc:
        raise ServiceToolError("RAG service is unavailable.") from exc


def search_rag_documents(query: str):
    try:
        response = requests.post(
            f"{RAG_BASE_URL}/rag/search",
            json={"query": query},
            timeout=REQUEST_TIMEOUT,
        )
        return _json(response, "RAG service")
    except requests.exceptions.Timeout as exc:
        raise ServiceToolError("RAG service request timed out.") from exc
    except requests.exceptions.RequestException as exc:
        raise ServiceToolError("RAG service is unavailable.") from exc
