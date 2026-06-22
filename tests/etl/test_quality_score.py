import pandas as pd

from etl_service.app.utils.anomaly import calculate_quality_score, detect_anomalies


def test_quality_score_clean_data_returns_100():
    df = pd.DataFrame({
        "name": ["Priya", "Ava", "Mia"],
        "age": [24, 25, 26],
    })

    score = calculate_quality_score(df)

    assert score == 100


def test_quality_score_drops_for_missing_values():
    df = pd.DataFrame({
        "name": ["Priya", None, "Mia"],
        "age": [24, 25, None],
    })

    score = calculate_quality_score(df)

    assert score < 100


def test_quality_score_drops_for_duplicate_rows():
    df = pd.DataFrame({
        "name": ["Priya", "Priya", "Mia"],
        "age": [24, 24, 26],
    })

    score = calculate_quality_score(df)

    assert score < 100


def test_detect_anomalies_finds_missing_values():
    df = pd.DataFrame({
        "name": ["Priya", None, "Mia"],
        "status": ["Pass", "Pass", "Pass"],
    })

    anomalies = detect_anomalies(df)

    assert "name" in anomalies
    assert "status" in anomalies
    assert "Only one unique value" in anomalies["status"]