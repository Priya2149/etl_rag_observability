from agent_service.app.services.report_agent import build_report, build_recommendation


def test_build_recommendation_high_risk():
    result = build_recommendation({"risk_level": "high"})

    assert "Review" in result


def test_build_recommendation_medium_risk():
    result = build_recommendation({"risk_level": "medium"})

    assert "caution" in result.lower()


def test_build_recommendation_low_risk():
    result = build_recommendation({"risk_level": "low"})

    assert "safe" in result.lower()


def test_build_report_contains_all_sections():
    planner_result = {"plan": ["etl_validation", "rag_retrieval"]}
    etl_result = {"quality_score": 95}
    rag_result = {"chunks_used": 2}
    evaluation_result = {"risk_level": "low"}

    report = build_report(
        planner_result=planner_result,
        etl_result=etl_result,
        rag_result=rag_result,
        evaluation_result=evaluation_result,
    )

    assert "summary" in report
    assert "planner" in report
    assert "etl" in report
    assert "rag" in report
    assert "evaluation" in report
    assert "recommendation" in report