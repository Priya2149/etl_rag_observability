import pandas as pd

from etl_service.app.services.profiler import profile_dataset, infer_column_type


def test_infer_column_type_integer():
    series = pd.Series([1, 2, 3])

    result = infer_column_type(series)

    assert result == "integer"


def test_infer_column_type_string():
    series = pd.Series(["High", "Medium", "Low"])

    result = infer_column_type(series)

    assert result == "string"


def test_profile_dataset_returns_column_profile():
    df = pd.DataFrame({
        "priority": ["High", "Medium", "High"],
        "score": [90, 80, 85],
    })

    profile = profile_dataset(df)

    assert "columns" in profile
    assert "numeric_summary" in profile
    assert "categorical_summary" in profile
    assert len(profile["columns"]) == 2
    assert "score" in profile["numeric_summary"]
    assert "priority" in profile["categorical_summary"]


def test_profile_dataset_detects_high_missing_column():
    df = pd.DataFrame({
        "name": ["A", None, None, None],
        "status": ["Pass", "Fail", "Pass", "Pass"],
    })

    profile = profile_dataset(df)

    assert any("more than 30% missing" in issue for issue in profile["schema_issues"])