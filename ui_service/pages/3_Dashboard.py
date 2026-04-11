import pandas as pd
import streamlit as st
from services.etl_api import get_etl_runs, get_etl_run_details
from services.rag_api import get_rag_runs, get_rag_run_details
from utils.ui_helpers import (
    init_theme,
    inject_global_styles,
    theme_toggle_button,
    section_title,
    page_header,
)

st.set_page_config(page_title="Observability Dashboard", layout="wide", page_icon=":material/dashboard:")

init_theme()
inject_global_styles()
theme_toggle_button("top-right")

page_header(
    "dashboard",
    "Observability Dashboard",
    "Unified view of ETL quality, RAG risk, and recent backend activity with a cleaner executive-style dashboard layout.",
)

etl_runs = get_etl_runs()
rag_runs = get_rag_runs()

completed_etl = sum(1 for run in etl_runs if str(run.get("status", "")).lower() == "completed")
high_risk_rag = sum(1 for run in rag_runs if str(run.get("risk_level", "")).lower() == "high")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class='hero-stat'>
            <div class='hero-stat-label'>Total ETL Runs</div>
            <div class='hero-stat-value'>{len(etl_runs)}</div>
            <div class='hero-stat-sub'>All recorded runs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class='hero-stat'>
            <div class='hero-stat-label'>Completed ETL</div>
            <div class='hero-stat-value' style='color:var(--success);'>{completed_etl}</div>
            <div class='hero-stat-sub'>Successful ETL executions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class='hero-stat'>
            <div class='hero-stat-label'>Total RAG Runs</div>
            <div class='hero-stat-value'>{len(rag_runs)}</div>
            <div class='hero-stat-sub'>All retrieval runs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    risk_color = "var(--danger)" if high_risk_rag > 0 else "var(--success)"
    st.markdown(
        f"""
        <div class='hero-stat'>
            <div class='hero-stat-label'>High-Risk RAG</div>
            <div class='hero-stat-value' style='color:{risk_color};'>{high_risk_rag}</div>
            <div class='hero-stat-sub'>Flagged retrieval responses</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

section_title("ETL quality overview", "Track ETL quality scores and job outcomes over time", icon="monitoring")

etl_quality_rows = []
for run in etl_runs:
    run_id = run.get("id")
    try:
        details = get_etl_run_details(run_id)
        etl_quality_rows.append(
            {
                "run_id": run_id,
                "filename": details.get("filename"),
                "quality_score": details.get("quality_score"),
                "status": details.get("status"),
            }
        )
    except Exception:
        pass

if etl_quality_rows:
    etl_quality_df = pd.DataFrame(etl_quality_rows)

    top_left, top_right = st.columns([2.2, 1])

    with top_left:
        st.markdown("<div class='table-card'>", unsafe_allow_html=True)
        st.dataframe(etl_quality_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with top_right:
        avg_quality = etl_quality_df["quality_score"].dropna().mean() if "quality_score" in etl_quality_df.columns else None
        successful_runs = (etl_quality_df["status"].astype(str).str.lower() == "completed").sum() if "status" in etl_quality_df.columns else 0
        avg_display = round(float(avg_quality), 2) if avg_quality is not None and pd.notna(avg_quality) else "N/A"

        st.markdown(
            f"""
            <div class='side-stat-box'>
                <div class='side-stat-label'>Avg Quality Score</div>
                <div class='side-stat-value'>{avg_display}</div>
            </div>
            <div class='side-stat-box'>
                <div class='side-stat-label'>Successful Runs</div>
                <div class='side-stat-value' style='color:var(--success);'>{int(successful_runs)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if avg_quality is not None and pd.notna(avg_quality):
            st.markdown("<div class='health-label'>Quality health</div>", unsafe_allow_html=True)
            st.progress(max(0, min(float(avg_quality), 100)) / 100)

    if "quality_score" in etl_quality_df.columns:
        section_title("Quality score trend", "", icon="show_chart")
        chart_df = etl_quality_df[["run_id", "quality_score"]].dropna().set_index("run_id")
        if not chart_df.empty:
            st.area_chart(chart_df, color="#3b82f6")
        else:
            st.info("No quality score trend data available.")
else:
    st.info("No ETL quality data available.")

st.divider()

section_title("RAG risk overview", "Inspect retrieval quality, risk level, and evaluation outcomes", icon="security")

rag_risk_rows = []
for run in rag_runs:
    run_id = run.get("id")
    try:
        details = get_rag_run_details(run_id)
        rag_risk_rows.append(
            {
                "run_id": run_id,
                "query": details.get("query"),
                "retrieved_count": details.get("retrieved_count"),
                "best_distance": details.get("best_distance"),
                "risk_level": details.get("risk_level"),
                "evaluation_status": details.get("evaluation_status"),
            }
        )
    except Exception:
        pass

if rag_risk_rows:
    rag_risk_df = pd.DataFrame(rag_risk_rows)

    overview_left, overview_right = st.columns([2.2, 1])

    with overview_left:
        st.markdown("<div class='table-card'>", unsafe_allow_html=True)
        st.dataframe(rag_risk_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with overview_right:
        avg_distance = rag_risk_df["best_distance"].dropna().mean() if "best_distance" in rag_risk_df.columns else None
        total_queries = len(rag_risk_df)
        high_risk_count = (rag_risk_df["risk_level"].astype(str).str.lower() == "high").sum() if "risk_level" in rag_risk_df.columns else 0
        avg_dist_display = round(float(avg_distance), 4) if avg_distance is not None and pd.notna(avg_distance) else "N/A"
        hr_color = "var(--danger)" if high_risk_count > 0 else "var(--success)"

        st.markdown(
            f"""
            <div class='side-stat-box'>
                <div class='side-stat-label'>Total Queries</div>
                <div class='side-stat-value'>{total_queries}</div>
            </div>
            <div class='side-stat-box'>
                <div class='side-stat-label'>High-Risk</div>
                <div class='side-stat-value' style='color:{hr_color};'>{int(high_risk_count)}</div>
            </div>
            <div class='side-stat-box'>
                <div class='side-stat-label'>Avg Distance</div>
                <div class='side-stat-value'>{avg_dist_display}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if "risk_level" in rag_risk_df.columns:
            section_title("Risk distribution", "", icon="warning")
            risk_counts = rag_risk_df["risk_level"].fillna("unknown").value_counts()
            st.bar_chart(risk_counts)

    with chart_col2:
        if "evaluation_status" in rag_risk_df.columns:
            section_title("Evaluation status distribution", "", icon="fact_check")
            eval_counts = rag_risk_df["evaluation_status"].fillna("unknown").value_counts()
            st.bar_chart(eval_counts)
else:
    st.info("No RAG risk data available.")

st.divider()

section_title("Recent backend activity", "Quick access to latest ETL and RAG activity", icon="history")

left, right = st.columns(2)

with left:
    st.markdown("<div class='table-card'>", unsafe_allow_html=True)
    section_title("Recent ETL runs", "", icon="storage")
    if etl_runs:
        st.dataframe(pd.DataFrame(etl_runs), use_container_width=True, hide_index=True)
    else:
        st.info("No ETL runs found.")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='table-card'>", unsafe_allow_html=True)
    section_title("Recent RAG runs", "", icon="smart_toy")
    if rag_runs:
        st.dataframe(pd.DataFrame(rag_runs), use_container_width=True, hide_index=True)
    else:
        st.info("No RAG runs found.")
    st.markdown("</div>", unsafe_allow_html=True)