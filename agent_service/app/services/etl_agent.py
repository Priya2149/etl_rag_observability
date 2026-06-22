def run_etl_agent(payload: dict, tool_client):
    dataset_id = payload.get("dataset_id")

    if not dataset_id:
        return {
            "status": "skipped",
            "reason": "No ETL run ID provided"
        }

    etl_result = tool_client(dataset_id)

    return {
        "status": "completed",
        "etl_run_id": dataset_id,
        "quality_score": etl_result.get("quality_score"),
        "total_rows": etl_result.get("total_rows"),
        "total_columns": etl_result.get("total_columns"),
        "anomalies": etl_result.get("anomalies"),
        "processing_time_ms": etl_result.get("processing_time_ms"),
    }