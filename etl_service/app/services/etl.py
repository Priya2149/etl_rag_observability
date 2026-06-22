import time
import pandas as pd
from app.utils.anomaly import detect_anomalies, calculate_quality_score
from app.services.profiler import profile_dataset


def process_data(file_path: str):
    start_time = time.perf_counter()

    df = pd.read_csv(file_path)

    original_rows = len(df)
    original_columns = len(df.columns)
    original_missing = df.isnull().sum().to_dict()
    duplicate_rows = int(df.duplicated().sum())

    anomalies = detect_anomalies(df)
    profile = profile_dataset(df)
    quality_score = calculate_quality_score(df)

    df = df.drop_duplicates()
    df = df.fillna("UNKNOWN")

    processing_time_ms = int((time.perf_counter() - start_time) * 1000)

    summary = {
        "total_rows": len(df),
        "total_columns": original_columns,
        "original_rows": original_rows,
        "missing_values_before_fill": original_missing,
        "duplicate_rows_removed": duplicate_rows,
    }

    return {
        "summary": summary,
        "anomalies": anomalies,
        "profile": profile,
        "quality_score": quality_score,
        "processing_time_ms": processing_time_ms,
    }