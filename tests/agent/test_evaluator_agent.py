from agent_service.app.services.evaluator_agent import run_evaluator


def test_high_risk_when_etl_quality_is_low():
    etl_result = {
        "quality_score": 50,
        "anomalies": None,
    }
    rag_result = {
        "chunks_used": 2,
        "risk_level": "low",
    }

    result = run_evaluator(etl_result, rag_result)

    assert result["risk_level"] == "high"
    assert result["evaluation_status"] == "needs_review"
    assert "low_etl_quality_score" in result["warnings"]


def test_medium_risk_when_etl_has_anomalies():
    etl_result = {
        "quality_score": 95,
        "anomalies": {"status": ["Only one unique value"]},
    }
    rag_result = {
        "chunks_used": 2,
        "risk_level": "low",
    }

    result = run_evaluator(etl_result, rag_result)

    assert result["risk_level"] == "medium"
    assert result["evaluation_status"] == "warning"
    assert "etl_anomalies_detected" in result["warnings"]


def test_high_risk_when_rag_uses_no_chunks():
    etl_result = {
        "quality_score": 95,
        "anomalies": None,
    }
    rag_result = {
        "chunks_used": 0,
        "risk_level": "high",
    }

    result = run_evaluator(etl_result, rag_result)

    assert result["risk_level"] == "high"
    assert "rag_no_chunks_used" in result["warnings"]


def test_low_risk_when_etl_and_rag_are_clean():
    etl_result = {
        "quality_score": 98,
        "anomalies": None,
    }
    rag_result = {
        "chunks_used": 2,
        "risk_level": "low",
    }

    result = run_evaluator(etl_result, rag_result)

    assert result["risk_level"] == "low"
    assert result["evaluation_status"] == "good"
    assert result["warnings"] == []