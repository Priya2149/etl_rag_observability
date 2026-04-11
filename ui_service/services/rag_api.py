import requests

RAG_BASE_URL = "http://rag_service:8000/rag"


def upload_rag_file(uploaded_file):
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")
    }
    response = requests.post(f"{RAG_BASE_URL}/upload", files=files)
    response.raise_for_status()
    return response.json()


def ask_rag_question(query: str):
    payload = {"query": query}
    response = requests.post(f"{RAG_BASE_URL}/ask", json=payload)
    response.raise_for_status()
    return response.json()


def get_rag_documents():
    response = requests.get(f"{RAG_BASE_URL}/documents")
    response.raise_for_status()
    return response.json()


def get_rag_runs():
    response = requests.get(f"{RAG_BASE_URL}/runs")
    response.raise_for_status()
    return response.json()


def get_rag_run_details(run_id: int):
    response = requests.get(f"{RAG_BASE_URL}/runs/{run_id}")
    response.raise_for_status()
    return response.json()