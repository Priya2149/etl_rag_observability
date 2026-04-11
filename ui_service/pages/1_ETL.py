import pandas as pd
import streamlit as st
from services.etl_api import upload_etl_file, get_etl_runs, get_etl_run_details
from utils.ui_helpers import (
    init_theme,
    inject_global_styles,
    theme_toggle_button,
    section_title,
    status_badge,
    show_key_value,
    page_header,
)

st.set_page_config(page_title="ETL Monitoring", layout="wide", page_icon=":material/monitoring:")

init_theme()
inject_global_styles()
theme_toggle_button("top-right")

st.markdown(
    """
    <style>
    .anomaly-item {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.18);
        border-left: 4px solid var(--danger);
        border-radius: 14px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.6rem;
        font-size: 0.86rem;
        color: var(--text-soft);
    }
    .score-label {
        font-size: 0.74rem;
        font-weight: 600;
        color: var(--text-muted);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

page_header(
    "monitoring",
    "ETL Monitoring",
    "Upload datasets, trigger profiling, and review quality, anomalies, and schema health in a polished enterprise-style interface.",
)

section_title("Upload dataset", "Submit a CSV file and start ETL profiling", icon="upload_file")
st.markdown("<div class='upload-zone'>", unsafe_allow_html=True)

left, right = st.columns([1.6, 0.9])

with left:
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="etl_upload")
    if uploaded_file is not None:
        st.markdown(
            f"""
            <div class="file-pill">
                <span class="material-icons-round" style="font-size:0.95rem">description</span>
                {uploaded_file.name}
            </div>
            """,
            unsafe_allow_html=True,
        )

with right:
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
    if uploaded_file is not None and st.button("Upload and profile", use_container_width=True, key="etl_upload_btn"):
        with st.spinner("Uploading and starting ETL processing..."):
            st.session_state["etl_last_upload"] = upload_etl_file(uploaded_file)
        st.success("ETL profiling has been started.")

st.markdown("</div>", unsafe_allow_html=True)

if "etl_last_upload" in st.session_state:
    section_title("Upload result", "Metadata from the latest submitted ETL job", icon="fact_check")
    result = st.session_state["etl_last_upload"]

    if isinstance(result, dict):
        cols = st.columns(min(4, max(1, len(result.keys()))))
        for idx, (key, value) in enumerate(result.items()):
            with cols[idx % len(cols)]:
                show_key_value(str(key).replace("_", " ").title(), value)
    else:
        st.json(result)

st.divider()

section_title("Run history", "Review ETL executions and inspect one run in detail", icon="history")
toolbar_col1, toolbar_col2 = st.columns([1, 4])

with toolbar_col1:
    if st.button("Refresh runs", use_container_width=True, key="etl_refresh"):
        st.session_state["etl_runs"] = get_etl_runs()

etl_runs = st.session_state.get("etl_runs", get_etl_runs())

if etl_runs:
    df = pd.DataFrame(etl_runs)
    st.dataframe(df, use_container_width=True, hide_index=True)

    select_col1, select_col2 = st.columns([2, 1])

    with select_col1:
        run_ids = [run["id"] for run in etl_runs]
        selected_run_id = st.selectbox("Select ETL run", run_ids)

    with select_col2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("View details", use_container_width=True, key="etl_view_details"):
            st.session_state["etl_selected_run"] = get_etl_run_details(selected_run_id)

if "etl_selected_run" in st.session_state:
    details = st.session_state["etl_selected_run"]

    st.divider()
    section_title("Run details", f"Execution record for run ID {details.get('id', '—')}", icon="analytics")

    metric1, metric2, metric3, metric4 = st.columns(4)
    quality_score = details.get("quality_score")

    with metric1:
        st.metric("Run ID", details.get("id", "—"))
    with metric2:
        st.metric("Rows", details.get("total_rows", "—"))
    with metric3:
        st.metric("Columns", details.get("total_columns", "—"))
    with metric4:
        st.metric("Quality score", quality_score if quality_score is not None else "N/A")

    info1, info2 = st.columns([3, 1])

    with info1:
        show_key_value("Filename", details.get("filename", "—"))

    with info2:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        status_badge(details.get("status"))

    if quality_score is not None:
        st.markdown("<div class='score-label'>Quality score indicator</div>", unsafe_allow_html=True)
        st.progress(max(0, min(float(quality_score), 100)) / 100)

    section_title("Anomalies", "Detected data quality issues", icon="report_problem")
    anomalies = details.get("anomalies")

    if anomalies:
        if isinstance(anomalies, list):
            items = [str(a) for a in anomalies]
        elif isinstance(anomalies, dict):
            items = [f"{k}: {v}" for k, v in anomalies.items()]
        else:
            items = [str(anomalies)]

        for item in items:
            st.markdown(
                f"""
                <div class='anomaly-item'>
                    <div style='display:flex;gap:8px;align-items:flex-start;'>
                        <span class='material-icons-round' style='font-size:1rem;color:var(--danger);'>warning</span>
                        <span>{item}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No anomalies detected for this run.")

    profile = details.get("profile")
    if profile:
        st.divider()
        section_title("Profiling summary", "Column, numeric, categorical, and schema analysis", icon="table_chart")

        if profile.get("columns"):
            section_title("Column profile", "Column-level schema overview", icon="view_column")
            st.dataframe(pd.DataFrame(profile["columns"]), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            section_title("Numeric summary", "Distribution and descriptive stats", icon="show_chart")
            numeric_summary = profile.get("numeric_summary")

            if numeric_summary:
                if isinstance(numeric_summary, dict):
                    numeric_rows = []
                    for column_name, summary in numeric_summary.items():
                        if isinstance(summary, dict):
                            row = {"column": column_name, **summary}
                        else:
                            row = {"column": column_name, "value": summary}
                        numeric_rows.append(row)
                    st.dataframe(pd.DataFrame(numeric_rows), use_container_width=True, hide_index=True)
                else:
                    st.json(numeric_summary)
            else:
                st.info("No numeric summary available.")

        with col2:
            section_title("Schema issues", "Type mismatches and structural checks", icon="rule")
            schema_issues = profile.get("schema_issues")

            if schema_issues:
                if isinstance(schema_issues, list):
                    for issue in schema_issues:
                        st.warning(str(issue))
                elif isinstance(schema_issues, dict):
                    schema_rows = [{"issue": k, "details": v} for k, v in schema_issues.items()]
                    st.dataframe(pd.DataFrame(schema_rows), use_container_width=True, hide_index=True)
                else:
                    st.warning(str(schema_issues))
            else:
                st.success("No schema issues found.")

        section_title("Categorical summary", "Category distribution and uniqueness", icon="category")
        categorical_summary = profile.get("categorical_summary")

        if categorical_summary:
            if isinstance(categorical_summary, dict):
                categorical_rows = []
                for column_name, summary in categorical_summary.items():
                    if isinstance(summary, dict):
                        row = {"column": column_name, **summary}
                    else:
                        row = {"column": column_name, "value": summary}
                    categorical_rows.append(row)
                st.dataframe(pd.DataFrame(categorical_rows), use_container_width=True, hide_index=True)
            else:
                st.json(categorical_summary)
        else:
            st.info("No categorical summary available.")
else:
    st.info("No ETL runs found yet.")