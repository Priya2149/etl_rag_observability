import requests
from app.config import ETL_BASE_URL, RAG_BASE_URL, REQUEST_TIMEOUT


def get_etl_run_details(run_id: int):
    response = requests.get(
        f"{ETL_BASE_URL}/etl/runs/{run_id}",
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def ask_rag_service(question: str):
    response = requests.post(
        f"{RAG_BASE_URL}/rag/ask",
        json={"query": question},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()