from __future__ import annotations

import pandas as pd
import streamlit as st

from api.client import get_overview
from components.charts import bar_chart, line_chart, should_render_chart, status_pie_chart
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
    recent_failures = overview.get("recent_failures", [])

    row1 = st.columns(4)
    with row1[0]:
        metric_card("ETL Total Runs", system_health["etl_total_runs"], "Processed datasets")
    with row1[1]:
        metric_card("ETL Health Score", system_health["etl_health_score"], "Overall ETL reliability")
    with row1[2]:
        metric_card("RAG Total Queries", system_health["rag_total_queries"], "Query executions")
    with row1[3]:
        metric_card("RAG Health Score", system_health["rag_health_score"], "Overall retrieval reliability")

    row2 = st.columns(3)
    with row2[0]:
        metric_card("ETL Failed Runs", system_health["etl_failed_runs"], "Runs with errors")
    with row2[1]:
        metric_card("RAG Failed Queries", system_health["rag_failed_queries"], "Failed responses")
    with row2[2]:
        metric_card("RAG High Risk", system_health["rag_high_risk_queries"], "Queries needing review")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Attention Required</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Quick signals that need review before they become production issues</div>',
        unsafe_allow_html=True,
    )

    attention = st.columns(3)
    with attention[0]:
        if system_health["etl_failed_runs"] > 0:
            st.error(f"{system_health['etl_failed_runs']} ETL run(s) failed")
        else:
            st.success("No ETL failures")

    with attention[1]:
        if system_health["rag_high_risk_queries"] > 0:
            st.warning(f"{system_health['rag_high_risk_queries']} RAG query/queries marked high risk")
        else:
            st.success("No high-risk RAG queries")

    with attention[2]:
        if recent_failures:
            st.warning(f"{len(recent_failures)} recent issue(s) in failure feed")
        else:
            st.success("No recent failures")

    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ETL Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Status, quality trend, and processing trend for recent ETL runs</div>',
            unsafe_allow_html=True,
        )

        etl_runs = etl_summary.get("recent_runs", [])
        etl_trends = etl_summary.get("trends", [])

        if etl_runs:
            etl_df = pd.DataFrame(etl_runs)
            if "status" in etl_df.columns:
                st.plotly_chart(
                    status_pie_chart(etl_df, "status", "Recent ETL Run Status"),
                    use_container_width=True,
                )
            render_table(etl_df)
        else:
            st.info("No ETL runs available yet.")

        if etl_trends:
            trends_df = pd.DataFrame(etl_trends)

            if should_render_chart(trends_df, "quality_score"):
                st.plotly_chart(
                    line_chart(
                        trends_df,
                        x="id",
                        y="quality_score",
                        title="ETL Quality Score Trend",
                        x_title="Run ID",
                        y_title="Quality Score",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("Need more ETL quality data to show trend.")

            if should_render_chart(trends_df, "processing_time_ms"):
                st.plotly_chart(
                    line_chart(
                        trends_df,
                        x="id",
                        y="processing_time_ms",
                        title="ETL Processing Time Trend",
                        x_title="Run ID",
                        y_title="Time (ms)",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("Processing time trend will appear once ETL timing data is available.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">RAG Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Query reliability, retrieval depth, and timing trends</div>',
            unsafe_allow_html=True,
        )

        rag_runs = rag_summary.get("recent_queries", [])
        rag_trends = rag_summary.get("trends", [])

        if rag_runs:
            rag_df = pd.DataFrame(rag_runs)
            render_table(rag_df)
        else:
            st.info("No RAG queries available yet.")

        if rag_trends:
            trends_df = pd.DataFrame(rag_trends)

            if should_render_chart(trends_df, "chunks_used"):
                st.plotly_chart(
                    bar_chart(
                        trends_df,
                        x="id",
                        y="chunks_used",
                        title="Chunks Used per Query",
                        x_title="Run ID",
                        y_title="Chunks Used",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("Chunk usage chart will appear after query metrics are available.")

            if should_render_chart(trends_df, "processing_time_ms"):
                st.plotly_chart(
                    line_chart(
                        trends_df,
                        x="id",
                        y="processing_time_ms",
                        title="RAG Processing Time Trend",
                        x_title="Run ID",
                        y_title="Time (ms)",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("Processing time trend will appear once RAG timing data is available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Failures</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Centralized failure and high-risk event view across services</div>',
        unsafe_allow_html=True,
    )
    if recent_failures:
        render_table(recent_failures)
    else:
        st.success("No recent failures found.")
    st.markdown("</div>", unsafe_allow_html=True)