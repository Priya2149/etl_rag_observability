import os


CHROMA_DIR = os.getenv("CHROMA_DIR", "app/chroma_store")
RAG_UPLOAD_DIR = os.getenv("RAG_UPLOAD_DIR", "app/uploads")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
