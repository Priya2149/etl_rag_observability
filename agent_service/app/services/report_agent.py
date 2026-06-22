def build_report(
    planner_result,
    rag_result,
    evaluation_result
):

    return {
        "workflow_summary": {
            "planner": planner_result,
            "rag": rag_result,
            "evaluation": evaluation_result
        }
    }