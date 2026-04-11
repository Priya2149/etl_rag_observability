import pandas as pd
import streamlit as st
from services.rag_api import (
    upload_rag_file,
    ask_rag_question,
    get_rag_documents,
    get_rag_runs,
    get_rag_run_details,
)
from utils.ui_helpers import (
    init_theme,
    inject_global_styles,
    theme_toggle_button,
    page_header,
    section_title,
    status_badge,
    risk_badge,
    show_key_value,
    answer_box,
    nav_item,
)

st.set_page_config(page_title="RAG Monitoring", layout="wide", page_icon=":material/smart_toy:")

init_theme()
inject_global_styles()
theme_toggle_button("top-right")

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;">
            <span class="material-icons-round" style="color:var(--primary);font-size:1.4rem">smart_toy</span>
            <span style="font-size:1rem;font-weight:700;color:var(--text);">RAG Monitor</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    nav_item("Upload knowledge", "upload_file")
    nav_item("Ask question", "chat")
    nav_item("Documents", "library_books")
    nav_item("Run history", "history")

page_header(
    "smart_toy",
    "RAG Monitoring",
    "Upload knowledge files, run retrieval queries, and inspect answer quality, source context, and risk signals.",
)

section_title("Upload knowledge file", "Upload a TXT document into the vector store", icon="upload_file")
st.markdown("<div class='upload-zone'>", unsafe_allow_html=True)
uc1, uc2 = st.columns([1.5, 1])

with uc1:
    uploaded_file = st.file_uploader("Drop a TXT file here or browse", type=["txt"], key="rag_upload")
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

with uc2:
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    if uploaded_file is not None and st.button("Upload document", use_container_width=True, key="rag_upload_btn"):
        with st.spinner("Uploading and ingesting document..."):
            st.session_state["rag_last_upload"] = upload_rag_file(uploaded_file)
        st.success("Document uploaded successfully.")

st.markdown("</div>", unsafe_allow_html=True)

if "rag_last_upload" in st.session_state:
    section_title("Upload result", "Metadata from the last ingested document", icon="receipt_long")
    result = st.session_state["rag_last_upload"]

    if isinstance(result, dict):
        cols = st.columns(min(4, max(1, len(result))))
        for idx, (k, v) in enumerate(result.items()):
            with cols[idx % len(cols)]:
                show_key_value(str(k).replace("_", " ").title(), v)
    else:
        st.json(result)

st.divider()

section_title("Ask a question", "Run retrieval and inspect evaluation signals", icon="chat")
st.markdown("<div class='surface-card'>", unsafe_allow_html=True)
qc1, qc2 = st.columns([4, 1])

with qc1:
    query = st.text_input(
        "Your question",
        placeholder="Ask something about your uploaded knowledge...",
        label_visibility="collapsed",
    )

with qc2:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    ask_clicked = st.button("Ask RAG", use_container_width=True, key="rag_ask")

st.markdown("</div>", unsafe_allow_html=True)

if ask_clicked:
    if query.strip():
        with st.spinner("Querying RAG service..."):
            st.session_state["rag_last_query"] = ask_rag_question(query)
        st.success("Query completed.")
    else:
        st.warning("Please enter a question before submitting.")

if "rag_last_query" in st.session_state:
    result = st.session_state["rag_last_query"]

    section_title("Query result", "Retrieval output with risk and evaluation signals", icon="find_in_page")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Run ID", result.get("run_id", "—"))
    with m2:
        st.metric("Retrieved count", result.get("retrieved_count", "—"))
    with m3:
        st.metric("Best distance", result.get("best_distance", "—"))

    bc1, bc2 = st.columns([1, 2])
    with bc1:
        risk_badge(result.get("risk_level"))
    with bc2:
        show_key_value("Evaluation status", result.get("evaluation_status", "—"))

    risk_level = (result.get("risk_level") or "").lower()
    if risk_level == "high":
        st.error("High-risk response detected. Review retrieved chunks and evaluation output carefully.")
    elif risk_level == "medium":
        st.warning("Medium-risk response detected. Manual review may be helpful.")
    elif risk_level:
        st.success("Low-risk response detected.")

    section_title("Answer", "Generated response from retrieval", icon="forum")
    answer_box(result.get("answer", ""))

    section_title("Warning flags", "Risk signals from the evaluator", icon="flag")
    warning_flags = result.get("warning_flags")
    if warning_flags:
        for flag in warning_flags:
            st.markdown(
                f"""
                <div class="flag-chip">
                    <span class="material-icons-round" style="font-size:0.95rem">report_problem</span>
                    {str(flag)}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No warning flags.")

    section_title("Source files", "Documents used in this retrieval", icon="folder_open")
    source_files = result.get("source_files")
    if source_files:
        if isinstance(source_files, list):
            st.dataframe(pd.DataFrame({"source_file": source_files}), use_container_width=True, hide_index=True)
        else:
            st.json(source_files)
    else:
        st.info("No source files found.")

    section_title("Retrieved chunks", "Vector store results with distance scores", icon="layers")
    if result.get("retrieved_chunks"):
        for idx, chunk in enumerate(result["retrieved_chunks"], 1):
            title = f"Chunk {idx:02d}"
            if isinstance(chunk, dict) and "distance" in chunk:
                title += f" · dist: {chunk['distance']}"
            with st.expander(title):
                if isinstance(chunk, dict):
                    st.markdown("**Content**")
                    st.write(chunk.get("content", ""))
                    st.markdown("**Metadata**")
                    metadata = chunk.get("metadata", {})
                    if metadata and isinstance(metadata, dict):
                        st.dataframe(
                            pd.DataFrame([{"key": k, "value": v} for k, v in metadata.items()]),
                            use_container_width=True,
                            hide_index=True,
                        )
                    elif metadata:
                        st.write(metadata)
                    if "distance" in chunk:
                        show_key_value("Distance", chunk["distance"])
                else:
                    st.write(chunk)
    else:
        st.info("No chunks retrieved.")

st.divider()

section_title("Uploaded RAG documents", "Documents currently available in the vector store", icon="library_books")
documents = get_rag_documents()
if documents:
    st.dataframe(pd.DataFrame(documents), use_container_width=True, hide_index=True)
else:
    st.info("No uploaded documents yet.")

st.divider()

section_title("RAG run history", "Review past executions and inspect detailed results", icon="history")
hc1, hc2 = st.columns([1, 4])

with hc1:
    if st.button("Refresh runs", use_container_width=True, key="rag_refresh"):
        st.session_state["rag_runs"] = get_rag_runs()

rag_runs = st.session_state.get("rag_runs", get_rag_runs())

if rag_runs:
    st.dataframe(pd.DataFrame(rag_runs), use_container_width=True, hide_index=True)

    sc1, sc2 = st.columns([2, 1])
    with sc1:
        run_ids = [run["id"] for run in rag_runs]
        selected_run_id = st.selectbox("Select RAG run", run_ids)
    with sc2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("View details", use_container_width=True, key="rag_view"):
            st.session_state["rag_selected_run"] = get_rag_run_details(selected_run_id)

if "rag_selected_run" in st.session_state:
    details = st.session_state["rag_selected_run"]

    st.divider()
    section_title(f"RAG run details · {details.get('id', '—')}", "Detailed view of one retrieval run", icon="analytics")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Run ID", details.get("id", "—"))
    with m2:
        st.metric("Retrieved count", details.get("retrieved_count", "—"))
    with m3:
        st.metric("Best distance", details.get("best_distance", "—"))

    b1, b2, b3 = st.columns([1, 1, 2])
    with b1:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        status_badge(details.get("status"))
    with b2:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        risk_badge(details.get("risk_level"))
    with b3:
        show_key_value("Evaluation status", details.get("evaluation_status", "—"))

    section_title("Answer", "", icon="forum")
    answer_box(details.get("answer", ""))

    section_title("Warning flags", "", icon="flag")
    if details.get("warning_flags"):
        for flag in details["warning_flags"]:
            st.markdown(
                f"""
                <div class="flag-chip">
                    <span class="material-icons-round" style="font-size:0.95rem">report_problem</span>
                    {str(flag)}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No warnings.")

    section_title("Source files", "", icon="folder_open")
    source_files = details.get("source_files", [])
    if source_files:
        if isinstance(source_files, list):
            st.dataframe(pd.DataFrame({"source_file": source_files}), use_container_width=True, hide_index=True)
        else:
            st.json(source_files)
    else:
        st.info("No source files.")

    section_title("Retrieved chunks", "", icon="layers")
    chunks = details.get("retrieved_chunks", [])
    if chunks:
        for idx, chunk in enumerate(chunks, 1):
            title = f"Chunk {idx:02d}"
            if isinstance(chunk, dict) and "distance" in chunk:
                title += f" · dist: {chunk['distance']}"
            with st.expander(title):
                if isinstance(chunk, dict):
                    st.markdown("**Content**")
                    st.write(chunk.get("content", ""))
                    metadata = chunk.get("metadata", {})
                    if metadata and isinstance(metadata, dict):
                        st.dataframe(
                            pd.DataFrame([{"key": k, "value": v} for k, v in metadata.items()]),
                            use_container_width=True,
                            hide_index=True,
                        )
                    elif metadata:
                        st.write(metadata)
                else:
                    st.write(chunk)
    else:
        st.info("No retrieved chunks.")