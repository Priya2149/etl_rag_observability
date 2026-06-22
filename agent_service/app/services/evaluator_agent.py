def run_evaluator(rag_result: dict):

    risk_level = "low"

    warnings = []

    chunks_used = rag_result.get(
        "chunks_used",
        0
    )

    if chunks_used == 0:
        risk_level = "high"

        warnings.append(
            "no_chunks_used"
        )

    return {
        "risk_level": risk_level,
        "warnings": warnings
    }