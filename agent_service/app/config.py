import os

ETL_BASE_URL = os.getenv("ETL_BASE_URL", "http://etl_service:8000")
RAG_BASE_URL = os.getenv("RAG_BASE_URL", "http://rag_service:8000")
REQUEST_TIMEOUT = float(os.getenv("SERVICE_TIMEOUT_SECONDS", "60"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))

AGENT_MAX_TOOL_ITERATIONS = max(1, int(os.getenv("AGENT_MAX_TOOL_ITERATIONS", "1")))
AGENT_MAX_TOOL_CALLS = max(1, int(os.getenv("AGENT_MAX_TOOL_CALLS", "4")))
AGENT_RECURSION_LIMIT = max(6, int(os.getenv("AGENT_RECURSION_LIMIT", "12")))
