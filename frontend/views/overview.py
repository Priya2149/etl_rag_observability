from __future__ import annotations

import pandas as pd
import streamlit as st

from api.client import get_overview
from components.charts import bar_chart, line_chart, status_pie_chart
from components.metrics import metric_card
from components.tables import render_table


def render_overview() -> None:
    try:
        overview = get_overview()
    except Exception as e:
        st.error(f"Failed to load overview: {e}")
        return

    system_health = overview["system_health"]
    etl_summary = overview["etl_summary"]
    rag_summary = overview["rag_summary"]

    row1 = st.columns(4)
    with row1[0]:
        metric_card("ETL Total Runs", system_health["etl_total_runs"], "Processed datasets")
    with row1[1]:
        metric_card("ETL Failed Runs", system_health["etl_failed_runs"], "Runs with errors")
    with row1[2]:
        metric_card("RAG Total Queries", system_health["rag_total_queries"], "Query executions")
    with row1[3]:
        metric_card("RAG Failed Queries", system_health["rag_failed_queries"], "Failed responses")

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ETL Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Recent ETL activity, status distribution, and quality trend</div>',
            unsafe_allow_html=True,
        )

        etl_runs = etl_summary.get("recent_runs", [])
        if etl_runs:
            etl_df = pd.DataFrame(etl_runs)

            if "status" in etl_df.columns:
                st.plotly_chart(
                    status_pie_chart(etl_df, "status", "Recent ETL Run Status"),
                    use_container_width=True,
                )

            if "quality_score" in etl_df.columns:
                st.plotly_chart(
                    bar_chart(
                        etl_df,
                        x="id",
                        y="quality_score",
                        title="Recent ETL Quality Scores",
                        x_title="Run ID",
                        y_title="Quality Score",
                    ),
                    use_container_width=True,
                )

            render_table(etl_df)
        else:
            st.info("No ETL run data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">RAG Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Recent retrieval usage, chunks used, and query timing</div>',
            unsafe_allow_html=True,
        )

        rag_runs = rag_summary.get("recent_queries", [])
        if rag_runs:
            rag_df = pd.DataFrame(rag_runs)

            if "chunks_used" in rag_df.columns:
                st.plotly_chart(
                    bar_chart(
                        rag_df,
                        x="id",
                        y="chunks_used",
                        title="Chunks Used per Recent Query",
                        x_title="Run ID",
                        y_title="Chunks Used",
                    ),
                    use_container_width=True,
                )

            if "processing_time_ms" in rag_df.columns:
                st.plotly_chart(
                    line_chart(
                        rag_df,
                        x="id",
                        y="processing_time_ms",
                        title="RAG Query Processing Time",
                        x_title="Run ID",
                        y_title="Time (ms)",
                    ),
                    use_container_width=True,
                )

            render_table(rag_df)
        else:
            st.info("No RAG query data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Failures</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Centralized failure view across ETL and RAG services</div>',
        unsafe_allow_html=True,
    )
    render_table(overview.get("recent_failures", []))
    st.markdown("</div>", unsafe_allow_html=True)