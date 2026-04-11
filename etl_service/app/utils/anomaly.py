import math


def detect_anomalies(df):
    anomalies = {}

    for col in df.columns:
        col_anomalies = []

        missing_count = int(df[col].isnull().sum())
        unique_count = int(df[col].nunique(dropna=True))

        if missing_count > 0:
            col_anomalies.append(f"{missing_count} missing values")

        if len(df) > 0 and missing_count / len(df) > 0.3:
            col_anomalies.append("More than 30% values are missing")

        if unique_count == 1:
            col_anomalies.append("Only one unique value")

        if col_anomalies:
            anomalies[col] = col_anomalies

    return anomalies


def calculate_quality_score(df):
    score = 100

    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = total_rows * total_columns if total_rows > 0 and total_columns > 0 else 0

    if total_cells > 0:
        missing_cells = int(df.isnull().sum().sum())
        if missing_cells > 0:
            missing_ratio = missing_cells / total_cells
            score -= max(1, math.ceil(missing_ratio * 40))

    duplicate_rows = int(df.duplicated().sum())
    if total_rows > 0 and duplicate_rows > 0:
        duplicate_ratio = duplicate_rows / total_rows
        score -= max(1, math.ceil(duplicate_ratio * 30))

    constant_columns = sum(1 for col in df.columns if df[col].nunique(dropna=True) == 1)
    if total_columns > 0 and constant_columns > 0:
        constant_ratio = constant_columns / total_columns
        score -= max(1, math.ceil(constant_ratio * 30))

    return max(score, 0)