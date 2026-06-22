from __future__ import annotations

import pandas as pd
import streamlit as st

from components.metrics import metric_card
from components.rag_answer import show_rag_answer
from components.tables import render_table
from utils.formatters import format_datetime, safe_number


def render_etl_details(details: dict) -> None:
    st.markdown("### ETL Run Summary")

    row = st.columns(4)
    with row[0]:
        metric_card("Quality Score", safe_number(details.get("quality_score")), "Dataset quality")
    with row[1]:
        metric_card("Rows", safe_number(details.get("total_rows")), "Processed row count")
    with row[2]:
        metric_card("Columns", safe_number(details.get("total_columns")), "Detected columns")
    with row[3]:
        metric_card("Processing Time (ms)", safe_number(details.get("processing_time_ms")), "Execution time")

    st.markdown("### Basic Information")
    info = {
        "Filename": details.get("filename"),
        "Status": details.get("status"),
        "Created At": format_datetime(details.get("created_at")),
        "Updated At": format_datetime(details.get("updated_at")),
    }
    st.json(info)

    anomalies = details.get("anomalies") or {}
    st.markdown("### Anomalies")
    if anomalies:
        for column_name, messages in anomalies.items():
            with st.expander(f"{column_name}", expanded=False):
                for msg in messages:
                    st.warning(msg)
    else:
        st.success("No anomalies detected.")

    profile = details.get("profile") or {}

    schema_issues = profile.get("schema_issues", [])
    st.markdown("### Schema Issues")
    if schema_issues:
        for issue in schema_issues:
            st.warning(issue)
    else:
        st.success("No schema issues found.")

    columns_profile = profile.get("columns", [])
    st.markdown("### Column Profile")
    if columns_profile:
        render_table(pd.DataFrame(columns_profile))
    else:
        st.info("No column profile available.")

    numeric_summary = profile.get("numeric_summary", {})
    st.markdown("### Numeric Summary")
    if numeric_summary:
        numeric_rows = []
        for column, values in numeric_summary.items():
            numeric_rows.append({
                "column": column,
                "min": values.get("min"),
                "max": values.get("max"),
                "mean": values.get("mean"),
                "median": values.get("median"),
            })
        render_table(pd.DataFrame(numeric_rows))
    else:
        st.info("No numeric summary available.")

    categorical_summary = profile.get("categorical_summary", {})
    st.markdown("### Top Categorical Values")
    if categorical_summary:
        for column, values in categorical_summary.items():
            with st.expander(f"{column}", expanded=False):
                rows = [{"value": k, "count": v} for k, v in values.items()]
                render_table(pd.DataFrame(rows))
    else:
        st.info("No categorical summary available.")

    with st.expander("Raw JSON Details", expanded=False):
        st.json(details)


def render_rag_details(details: dict) -> None:
    st.markdown("### RAG Run Summary")

    row = st.columns(4)
    with row[0]:
        metric_card("Chunks Used", safe_number(details.get("chunks_used")), "Final chunks used")
    with row[1]:
        metric_card("Retrieved Count", safe_number(details.get("retrieved_count")), "Raw chunks retrieved")
    with row[2]:
        metric_card("Best Distance", safe_number(details.get("best_distance")), "Retrieval score")
    with row[3]:
        metric_card("Processing Time (ms)", safe_number(details.get("processing_time_ms")), "Query time")

    eval_row = st.columns(3)
    with eval_row[0]:
        metric_card("Risk Level", safe_number(details.get("risk_level")), "Evaluation signal")
    with eval_row[1]:
        metric_card("Evaluation", safe_number(details.get("evaluation_status")), "Quality review")
    with eval_row[2]:
        metric_card("Status", safe_number(details.get("status")), "Run status")

    st.markdown("### Query Info")
    st.json({
        "query": details.get("query"),
        "created_at": format_datetime(details.get("created_at")),
        "error_message": details.get("error_message"),
    })

    # Normalize shape so existing answer renderer still works
    normalized = {
        "answer": details.get("answer"),
        "processing_time_ms": details.get("processing_time_ms"),
        "retrieved_chunks": details.get("retrieved_chunks", []),
        "retrieval_info": {
            "chunks_used": details.get("chunks_used"),
            "retrieved_count": details.get("retrieved_count"),
            "best_distance": details.get("best_distance"),
            "sources": details.get("sources", []),
        },
        "evaluation": {
            "risk_level": details.get("risk_level"),
            "evaluation_status": details.get("evaluation_status"),
            "warning_flags": details.get("warning_flags", []),
        },
    }

    show_rag_answer(normalized)

    with st.expander("Raw JSON Details", expanded=False):
        st.json(details)