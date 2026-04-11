from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_DIR = "app/chroma_store"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def evaluate_retrieval(retrieved_chunks):
    warning_flags = []

    if not retrieved_chunks:
        return {
            "best_distance": None,
            "risk_level": "high",
            "evaluation_status": "no_results",
            "warning_flags": ["No chunks retrieved"]
        }

    best_distance = retrieved_chunks[0]["distance"]

    if len(retrieved_chunks) == 1:
        warning_flags.append("Only one chunk retrieved")

    if best_distance > 1.0:
        risk_level = "high"
        evaluation_status = "low_confidence"
        warning_flags.append("Top match distance is high")
    elif best_distance > 0.6:
        risk_level = "medium"
        evaluation_status = "needs_review"
        warning_flags.append("Top match is moderately relevant")
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
        embedding_function=embedding_model
    )

    docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)

    seen = set()
    retrieved_chunks = []
    source_files = set()

    for doc, score in docs_with_scores:
        content = doc.page_content.strip()

        if content in seen:
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

    evaluation = evaluate_retrieval(retrieved_chunks)

    if not retrieved_chunks:
        return {
            "answer": "No relevant content found.",
            "retrieved_chunks": [],
            "retrieved_count": 0,
            "source_files": [],
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
        "retrieved_count": len(retrieved_chunks),
        "source_files": sorted(list(source_files)),
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