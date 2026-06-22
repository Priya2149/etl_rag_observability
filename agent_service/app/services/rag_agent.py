def run_rag_agent(payload: dict, tool_client):
    question = payload.get("question")

    if not question:
        return {
            "status": "skipped",
            "reason": "No question provided"
        }

    rag_result = tool_client(question)

    retrieval_info = rag_result.get("retrieval_info", {})
    evaluation = rag_result.get("evaluation", {})

    return {
        "status": "completed",
        "query": question,
        "answer": rag_result.get("answer"),
        "chunks_used": retrieval_info.get("chunks_used"),
        "retrieved_count": retrieval_info.get("retrieved_count"),
        "best_distance": retrieval_info.get("best_distance"),
        "sources": retrieval_info.get("sources", []),
        "risk_level": evaluation.get("risk_level"),
        "evaluation_status": evaluation.get("evaluation_status"),
        "warning_flags": evaluation.get("warning_flags", []),
        "processing_time_ms": rag_result.get("processing_time_ms"),
    }