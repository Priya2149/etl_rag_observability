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
    evaluation = result.get("evaluation", {})

    row1 = st.columns(4)
    with row1[0]:
        st.metric("Chunks Used", retrieval_info.get("chunks_used", result.get("chunks_used", 0)))
    with row1[1]:
        st.metric("Retrieved Count", retrieval_info.get("retrieved_count", result.get("retrieved_count", 0)))
    with row1[2]:
        st.metric("Best Distance", retrieval_info.get("best_distance", result.get("best_distance", "-")))
    with row1[3]:
        st.metric("Processing Time (ms)", result.get("processing_time_ms", 0))

    row2 = st.columns(2)
    with row2[0]:
        st.markdown(f"**Risk Level:** {evaluation.get('risk_level', result.get('risk_level', '-'))}")
    with row2[1]:
        st.markdown(f"**Evaluation Status:** {evaluation.get('evaluation_status', result.get('evaluation_status', '-'))}")

    warning_flags = evaluation.get("warning_flags", result.get("warning_flags", []))
    st.markdown("#### Warning Flags")
    if warning_flags:
        for flag in warning_flags:
            st.warning(flag)
    else:
        st.success("No warning flags detected.")

    st.markdown("#### Sources")
    _render_sources(retrieval_info.get("sources", result.get("sources", [])))

    chunks = result.get("retrieved_chunks", [])
    if chunks:
        st.markdown("#### Retrieved Chunks")
        for idx, chunk in enumerate(chunks, start=1):
            label = f"Chunk {idx}"
            score = chunk.get("score")
            if score is not None:
                label += f" • score={round(score, 4)}"

            with st.expander(label, expanded=(idx == 1)):
                st.write(chunk.get("content", ""))
                st.caption(f"Metadata: {chunk.get('metadata', {})}")