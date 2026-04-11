import streamlit as st

st.set_page_config(
    page_title="Data + AI Reliability Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Data + AI Reliability Platform")
st.markdown(
    """
    A microservices-based platform for:

    - **ETL pipeline profiling and monitoring**
    - **RAG retrieval monitoring**
    - **Run observability and risk analysis**
    """
)

st.info("Use the sidebar to open ETL, RAG, and Dashboard pages.")