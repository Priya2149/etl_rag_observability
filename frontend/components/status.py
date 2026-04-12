import streamlit as st


def status_badge(status: str) -> None:
    normalized = (status or "").strip().lower()
    css_class = f"status-{normalized}" if normalized else "status-pending"
    label = normalized.capitalize() if normalized else "Unknown"

    st.markdown(
        f'<span class="status-badge {css_class}">{label}</span>',
        unsafe_allow_html=True,
    )