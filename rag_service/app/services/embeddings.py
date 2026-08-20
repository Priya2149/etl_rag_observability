from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

from ..config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the local embedding model only when ingestion or retrieval needs it."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
