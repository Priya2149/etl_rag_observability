import os


CHROMA_DIR = os.getenv("CHROMA_DIR", "app/chroma_store")
RAG_UPLOAD_DIR = os.getenv("RAG_UPLOAD_DIR", "app/uploads")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# These settings prepare the service for a future provider integration. They are
# intentionally unused until an LLM-backed RAG implementation is added.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
