from __future__ import annotations

import streamlit as st

from api.client import (
    ask_rag,
    get_rag_documents,
    get_rag_run_details,
    get_rag_runs,
    upload_document,
)
from components.rag_answer import show_rag_answer
from components.tables import render_table


def render_rag() -> None:
    top_left, top_right = st.columns([0.95, 1.05])

    with top_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Upload Text Document</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Ingest a text document into the vector store for retrieval</div>',
            unsafe_allow_html=True,
        )

        uploaded_doc = st.file_uploader("Choose a .txt file", type=["txt"], key="rag_doc_upload")

        if uploaded_doc is not None:
            if st.button("Ingest Document", key="rag_ingest_button"):
                try:
                    result = upload_document(uploaded_doc)
                    st.success("Document uploaded successfully.")
                    st.json(result)
                except Exception as e:
                    st.error(f"Document upload failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    with top_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Ask a Question</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Query the RAG pipeline and inspect retrieved context</div>',
            unsafe_allow_html=True,
        )

        query = st.text_area(
            "Enter your question",
            height=110,
            placeholder="Example: What is RAG?",
            key="rag_query_input",
        )

        if st.button("Ask RAG", key="rag_ask_button"):
            if query.strip():
                try:
                    result = ask_rag(query)
                    st.success("Query processed successfully.")
                    show_rag_answer(result)
                except Exception as e:
                    st.error(f"Query failed: {e}")
            else:
                st.warning("Please enter a query.")

        st.markdown("</div>", unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">RAG Documents</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Documents currently available to the retrieval service</div>',
            unsafe_allow_html=True,
        )
        try:
            docs = get_rag_documents()
            render_table(docs)
        except Exception as e:
            st.error(f"Failed to fetch documents: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">RAG Runs</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Review recent query runs and inspect answer details</div>',
            unsafe_allow_html=True,
        )

        try:
            rag_runs = get_rag_runs()
            render_table(rag_runs)

            if rag_runs:
                run_ids = [run["id"] for run in rag_runs]
                selected_run_id = st.selectbox("Select RAG Run ID", run_ids, key="rag_run_select")

                if st.button("View RAG Run Details", key="rag_details_button"):
                    details = get_rag_run_details(selected_run_id)
                    show_rag_answer(details)

        except Exception as e:
            st.error(f"Failed to fetch RAG runs: {e}")

        st.markdown("</div>", unsafe_allow_html=True)