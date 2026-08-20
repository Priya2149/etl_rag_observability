import os


ETL_BASE_URL = os.getenv("ETL_BASE_URL", "http://etl_service:8000")
RAG_BASE_URL = os.getenv("RAG_BASE_URL", "http://rag_service:8000")
OBS_BASE_URL = os.getenv("OBS_BASE_URL", "http://observability_service:8000")
AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "http://agent_service:8000")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("SERVICE_TIMEOUT_SECONDS", "60"))

APP_TITLE = "Data + AI Reliability Platform"
APP_SUBTITLE = "Monitor ETL and RAG workflows from a unified dashboard"
