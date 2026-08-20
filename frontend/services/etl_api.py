import requests

from config.settings import ETL_BASE_URL as ETL_SERVICE_URL


ETL_BASE_URL = f"{ETL_SERVICE_URL}/etl"


def upload_etl_file(uploaded_file):
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
    }
    response = requests.post(f"{ETL_BASE_URL}/upload", files=files)
    response.raise_for_status()
    return response.json()


def get_etl_runs():
    response = requests.get(f"{ETL_BASE_URL}/runs")
    response.raise_for_status()
    return response.json()


def get_etl_run_details(run_id: int):
    response = requests.get(f"{ETL_BASE_URL}/runs/{run_id}")
    response.raise_for_status()
    return response.json()
