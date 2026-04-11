import pandas as pd

def infer_column_type(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "float"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    return "string"


def profile_dataset(df: pd.DataFrame):
    columns_profile = []
    numeric_summary = {}
    categorical_summary = {}
    schema_issues = []

    total_rows = len(df)

    if df.columns.duplicated().any():
        schema_issues.append("Duplicate column names detected")

    if any(str(col).strip() == "" for col in df.columns):
        schema_issues.append("Empty column names detected")

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isnull().sum())
        missing_percent = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0
        unique_count = int(series.nunique(dropna=True))
        inferred_type = infer_column_type(series)

        column_info = {
            "column_name": col,
            "inferred_type": inferred_type,
            "missing_count": missing_count,
            "missing_percent": missing_percent,
            "unique_count": unique_count,
        }

        if missing_percent > 30:
            schema_issues.append(f"Column '{col}' has more than 30% missing values")

        columns_profile.append(column_info)

        if inferred_type in ["integer", "float"]:
            cleaned = pd.to_numeric(series, errors="coerce").dropna()
            if not cleaned.empty:
                numeric_summary[col] = {
                    "min": float(cleaned.min()),
                    "max": float(cleaned.max()),
                    "mean": float(cleaned.mean()),
                    "median": float(cleaned.median()),
                }

        elif inferred_type == "string":
            top_values = series.astype(str).value_counts(dropna=True).head(5).to_dict()
            categorical_summary[col] = top_values

    return {
        "columns": columns_profile,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "schema_issues": schema_issues,
    }