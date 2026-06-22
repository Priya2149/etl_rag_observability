def run_planner(payload: dict):

    return {
        "plan": [
            "etl_validation",
            "rag_retrieval",
            "evaluation",
            "human_review",
            "report_generation"
        ]
    }