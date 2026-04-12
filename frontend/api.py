import requests

ETL_BASE_URL = "http://etl_service:8000"
RAG_BASE_URL = "http://rag_service:8000"
OBS_BASE_URL = "http://observability_service:8000"


# ----------------------
# ETL APIs
# ----------------------
def upload_csv(file):
    files = {"file": (file.name, file.getvalue(), "text/csv")}
    response = requests.post(f"{ETL_BASE_URL}/etl/upload", files=files)
    return response.json()


def get_etl_runs():
    response = requests.get(f"{ETL_BASE_URL}/etl/runs")
    return response.json()


def get_etl_run_details(run_id):
    response = requests.get(f"{ETL_BASE_URL}/etl/runs/{run_id}")
    return response.json()


# ----------------------
# RAG APIs
# ----------------------
def upload_document(file):
    files = {"file": (file.name, file.getvalue(), "text/plain")}
    response = requests.post(f"{RAG_BASE_URL}/rag/upload", files=files)
    return response.json()


def ask_rag(query):
    response = requests.post(
        f"{RAG_BASE_URL}/rag/ask",
        json={"query": query}
    )
    return response.json()


def get_rag_documents():
    response = requests.get(f"{RAG_BASE_URL}/rag/documents")
    return response.json()


def get_rag_runs():
    response = requests.get(f"{RAG_BASE_URL}/rag/runs")
    return response.json()


def get_rag_run_details(run_id):
    response = requests.get(f"{RAG_BASE_URL}/rag/runs/{run_id}")
    return response.json()


# ----------------------
# Observability APIs
# ----------------------
def get_overview():
    response = requests.get(f"{OBS_BASE_URL}/observability/overview")
    return response.json()


def get_etl_summary():
    response = requests.get(f"{OBS_BASE_URL}/observability/etl-summary")
    return response.json()


def get_rag_summary():
    response = requests.get(f"{OBS_BASE_URL}/observability/rag-summary")
    return response.json()


def get_recent_failures():
    response = requests.get(f"{OBS_BASE_URL}/observability/recent-failures")
    return response.json()