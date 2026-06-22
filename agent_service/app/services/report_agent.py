def build_report(planner_result, etl_result, rag_result, evaluation_result):
    return {
        "summary": "Agentic workflow completed after human approval.",
        "planner": planner_result,
        "etl": etl_result,
        "rag": rag_result,
        "evaluation": evaluation_result,
        "recommendation": build_recommendation(evaluation_result),
    }


def build_recommendation(evaluation_result):
    risk = evaluation_result.get("risk_level")

    if risk == "high":
        return "Review the ETL/RAG outputs before using this result downstream."
    if risk == "medium":
        return "Result can be used with caution. Review warning flags."
    return "Result appears safe based on current checks."