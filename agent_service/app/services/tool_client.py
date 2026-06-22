import requests
from app.config import ETL_BASE_URL, RAG_BASE_URL, REQUEST_TIMEOUT


def get_etl_run_details(run_id: int):
    try:
        response = requests.get(
            f"{ETL_BASE_URL}/etl/runs/{run_id}",
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        raise RuntimeError("ETL service request timed out")

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"ETL service returned error: {str(e)}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"ETL service unavailable: {str(e)}")


def ask_rag_service(question: str):
    try:
        response = requests.post(
            f"{RAG_BASE_URL}/rag/ask",
            json={"query": question},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        raise RuntimeError("RAG service request timed out")

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"RAG service returned error: {str(e)}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"RAG service unavailable: {str(e)}")