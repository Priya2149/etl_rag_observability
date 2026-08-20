from langchain_community.vectorstores import Chroma

from ..config import CHROMA_DIR
from .embeddings import get_embedding_model

def evaluate_retrieval(
    retrieved_chunks=None,
    *,
    retrieved_count=None,
    chunks_used=None,
    best_distance=None,
    duplicate_count=0,
):
    """Evaluate retrieval quality using the metrics stored for each RAG run."""
    if retrieved_chunks is not None:
        retrieved_count = len(retrieved_chunks)
        chunks_used = len(retrieved_chunks)
        distances = [chunk["distance"] for chunk in retrieved_chunks]
        best_distance = min(distances) if distances else None

    retrieved_count = retrieved_count or 0
    chunks_used = chunks_used or 0
    warning_flags = []

    if retrieved_count == 0:
        warning_flags.append("no_chunks_retrieved")
    if chunks_used == 0:
        warning_flags.append("no_chunks_used")
    if duplicate_count > 0:
        warning_flags.append("duplicate_chunks_detected")
    if best_distance is not None and best_distance > 1.0:
        warning_flags.append("low_retrieval_relevance")

    if retrieved_count == 0 or chunks_used == 0 or "low_retrieval_relevance" in warning_flags:
        risk_level = "high"
        evaluation_status = "needs_review"
    elif duplicate_count > 0 or (best_distance is not None and best_distance > 0.6):
        risk_level = "medium"
        evaluation_status = "warning"
    else:
        risk_level = "low"
        evaluation_status = "good"

    return {
        "best_distance": best_distance,
        "risk_level": risk_level,
        "evaluation_status": evaluation_status,
        "warning_flags": warning_flags
    }

def query_documents(query: str, k: int = 3):
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embedding_model()
    )

    docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)

    seen = set()
    retrieved_chunks = []
    source_files = set()
    duplicate_count = 0

    for doc, score in docs_with_scores:
        content = doc.page_content.strip()

        if content in seen:
            duplicate_count += 1
            continue

        seen.add(content)

        source = doc.metadata.get("source")
        if source:
            source_files.add(source)

        retrieved_chunks.append({
            "content": content,
            "metadata": doc.metadata,
            "distance": float(score)
        })

    retrieved_count = len(docs_with_scores)
    chunks_used = len(retrieved_chunks)
    distances = [chunk["distance"] for chunk in retrieved_chunks]
    best_distance = min(distances) if distances else None
    evaluation = evaluate_retrieval(
        retrieved_count=retrieved_count,
        chunks_used=chunks_used,
        best_distance=best_distance,
        duplicate_count=duplicate_count,
    )

    if not retrieved_chunks:
        return {
            "answer": "No relevant content found.",
            "retrieved_chunks": [],
            "retrieved_count": retrieved_count,
            "chunks_used": 0,
            "duplicate_count": duplicate_count,
            "source_files": [],
            "sources": [],
            "best_distance": evaluation["best_distance"],
            "risk_level": evaluation["risk_level"],
            "evaluation_status": evaluation["evaluation_status"],
            "warning_flags": evaluation["warning_flags"]
        }

    best_chunk = retrieved_chunks[0]["content"]

    answer = f"Answer based on retrieved content:\n{best_chunk}"

    return {
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
        "retrieved_count": retrieved_count,
        "chunks_used": chunks_used,
        "duplicate_count": duplicate_count,
        "source_files": sorted(list(source_files)),
        "sources": sorted(list(source_files)),
        "best_distance": evaluation["best_distance"],
        "risk_level": evaluation["risk_level"],
        "evaluation_status": evaluation["evaluation_status"],
        "warning_flags": evaluation["warning_flags"]
    }

def evaluate_rag(query, results):
    if not results:
        return {
            "evaluation_status": "failed",
            "risk_level": "high",
            "warning_flags": ["No context retrieved"]
        }

    best_distance = min(r["distance"] for r in results)

    warning_flags = []

    if best_distance > 1.5:
        warning_flags.append("Low confidence retrieval")

    if len(results) == 1:
        return {
            "evaluation_status": "partial",
            "risk_level": "medium",
            "warning_flags": warning_flags
        }

    return {
        "evaluation_status": "good",
        "risk_level": "low",
        "warning_flags": warning_flags
    }
