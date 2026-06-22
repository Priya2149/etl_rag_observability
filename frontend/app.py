from __future__ import annotations

import streamlit as st

from config.settings import APP_SUBTITLE, APP_TITLE
from views.etl import render_etl
from views.failures import render_failures
from views.overview import render_overview
from views.rag import render_rag
from styles.theme import apply_theme
from views.agents import render_agent_workflows

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)

apply_theme()

st.markdown(
    f"""
    <div class="app-hero">
        <div class="app-hero-title">{APP_TITLE}</div>
        <div class="app-hero-subtitle">{APP_SUBTITLE}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "Navigation",
    ["Overview", "ETL", "RAG", "Failures", "Agents"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Platform Dashboard")
st.sidebar.caption("ETL • RAG • Observability")

if menu == "Overview":
    render_overview()
elif menu == "ETL":
    render_etl()
elif menu == "RAG":
    render_rag()
elif menu == "Failures":
    render_failures()
elif menu == "Agents":
    render_agent_workflows()