from __future__ import annotations

import streamlit as st

from utils.formatters import trim_source_name


def _render_sources(sources: list[str]) -> None:
    if not sources:
        st.info("No source files found.")
        return

    html = "".join(
        [f'<span class="source-chip">{trim_source_name(src)}</span>' for src in sources]
    )
    st.markdown(html, unsafe_allow_html=True)


def show_rag_answer(result: dict) -> None:
    st.markdown("#### Answer")
    st.markdown(
        f"""
        <div class="answer-box">
            {result.get("answer", "No answer available.")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    retrieval_info = result.get("retrieval_info", {})
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Chunks Used", retrieval_info.get("chunks_used", 0))

    with col2:
        st.metric("Processing Time (ms)", result.get("processing_time_ms", 0))

    st.markdown("#### Sources")
    _render_sources(retrieval_info.get("sources", []))

    chunks = result.get("retrieved_chunks", [])
    if chunks:
        st.markdown("#### Retrieved Chunks")
        for idx, chunk in enumerate(chunks, start=1):
            with st.expander(f"Chunk {idx}", expanded=(idx == 1)):
                st.write(chunk.get("content", ""))
                st.caption(f"Metadata: {chunk.get('metadata', {})}")