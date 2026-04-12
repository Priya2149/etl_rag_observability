from __future__ import annotations

import streamlit as st

from api.client import get_etl_run_details, get_etl_runs, upload_csv
from components.metrics import metric_card
from components.tables import render_table


def render_etl() -> None:
    left, right = st.columns([0.95, 1.05])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Upload CSV</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Trigger a new ETL pipeline run for structured data processing</div>',
            unsafe_allow_html=True,
        )

        uploaded_csv = st.file_uploader("Choose a CSV file", type=["csv"], key="etl_csv_upload")

        if uploaded_csv is not None:
            if st.button("Run ETL Pipeline", key="etl_run_button"):
                try:
                    result = upload_csv(uploaded_csv)
                    st.success("CSV uploaded successfully.")
                    st.json(result)
                except Exception as e:
                    st.error(f"Upload failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ETL Runs</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Inspect recent pipeline runs, status, and detailed profiling results</div>',
            unsafe_allow_html=True,
        )

        try:
            etl_runs = get_etl_runs()
            render_table(etl_runs)

            if etl_runs:
                run_ids = [run["id"] for run in etl_runs]
                selected_run_id = st.selectbox("Select ETL Run ID", run_ids, key="etl_run_select")

                if st.button("View ETL Run Details", key="etl_details_button"):
                    details = get_etl_run_details(selected_run_id)

                    row = st.columns(3)
                    with row[0]:
                        metric_card("Quality Score", details.get("quality_score", "-"), "Overall dataset quality")
                    with row[1]:
                        metric_card("Rows", details.get("total_rows", "-"), "Processed row count")
                    with row[2]:
                        metric_card(
                            "Processing Time (ms)",
                            details.get("processing_time_ms", "-"),
                            "ETL execution time",
                        )

                    st.markdown("#### Run Details")
                    st.json(details)

        except Exception as e:
            st.error(f"Failed to fetch ETL runs: {e}")

        st.markdown("</div>", unsafe_allow_html=True)