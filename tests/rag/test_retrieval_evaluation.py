from rag_service.app.services.retrieve import evaluate_retrieval


def test_high_risk_when_no_chunks_retrieved():
    result = evaluate_retrieval(
        retrieved_count=0,
        chunks_used=0,
        best_distance=None,
        duplicate_count=0,
    )

    assert result["risk_level"] == "high"
    assert result["evaluation_status"] == "needs_review"
    assert "no_chunks_retrieved" in result["warning_flags"]


def test_high_risk_when_no_chunks_used():
    result = evaluate_retrieval(
        retrieved_count=2,
        chunks_used=0,
        best_distance=0.5,
        duplicate_count=0,
    )

    assert result["risk_level"] == "high"
    assert "no_chunks_used" in result["warning_flags"]


def test_medium_risk_when_duplicate_chunks_detected():
    result = evaluate_retrieval(
        retrieved_count=3,
        chunks_used=2,
        best_distance=0.5,
        duplicate_count=1,
    )

    assert result["risk_level"] == "medium"
    assert result["evaluation_status"] == "warning"
    assert "duplicate_chunks_detected" in result["warning_flags"]


def test_high_risk_when_best_distance_is_high():
    result = evaluate_retrieval(
        retrieved_count=3,
        chunks_used=2,
        best_distance=1.5,
        duplicate_count=0,
    )

    assert result["risk_level"] == "high"
    assert "low_retrieval_relevance" in result["warning_flags"]


def test_good_when_retrieval_is_clean():
    result = evaluate_retrieval(
        retrieved_count=3,
        chunks_used=3,
        best_distance=0.4,
        duplicate_count=0,
    )

    assert result["risk_level"] == "low"
    assert result["evaluation_status"] == "good"
    assert result["warning_flags"] == []