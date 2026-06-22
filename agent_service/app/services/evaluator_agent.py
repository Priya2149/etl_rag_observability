def run_evaluator(etl_result: dict, rag_result: dict):
    warnings = []
    risk_level = "low"

    etl_quality = etl_result.get("quality_score")
    rag_risk = rag_result.get("risk_level")
    chunks_used = rag_result.get("chunks_used")

    if etl_quality is not None and etl_quality < 70:
        warnings.append("low_etl_quality_score")
        risk_level = "high"

    if etl_result.get("anomalies"):
        warnings.append("etl_anomalies_detected")
        if risk_level != "high":
            risk_level = "medium"

    if chunks_used == 0:
        warnings.append("rag_no_chunks_used")
        risk_level = "high"

    if rag_risk == "high":
        warnings.append("rag_high_risk")
        risk_level = "high"
    elif rag_risk == "medium" and risk_level == "low":
        warnings.append("rag_medium_risk")
        risk_level = "medium"

    evaluation_status = "good"
    if risk_level == "medium":
        evaluation_status = "warning"
    elif risk_level == "high":
        evaluation_status = "needs_review"

    return {
        "risk_level": risk_level,
        "evaluation_status": evaluation_status,
        "warnings": warnings,
    }