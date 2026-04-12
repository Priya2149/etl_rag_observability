import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #0b1120;
                --panel: #111827;
                --panel-2: #0f172a;
                --text: #e5e7eb;
                --muted: #94a3b8;
                --border: rgba(148, 163, 184, 0.16);
                --accent: #60a5fa;
                --accent-2: #38bdf8;
                --success: #22c55e;
                --warning: #f59e0b;
                --danger: #ef4444;
                --radius: 18px;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(56, 189, 248, 0.07), transparent 28%),
                    radial-gradient(circle at top right, rgba(96, 165, 250, 0.08), transparent 25%),
                    linear-gradient(180deg, #0b1120 0%, #0f172a 100%);
                color: var(--text);
            }

            .block-container {
                max-width: 1350px;
                padding-top: 1.6rem;
                padding-bottom: 2rem;
            }

            h1, h2, h3 {
                color: #f8fafc !important;
                letter-spacing: -0.02em;
            }

            p, li, div, span, label {
                color: var(--text);
            }

            [data-testid="stSidebar"] {
                background: rgba(15, 23, 42, 0.95);
                border-right: 1px solid var(--border);
            }

            .app-hero {
                background: linear-gradient(135deg, rgba(17,24,39,0.95), rgba(15,23,42,0.96));
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 22px 24px;
                margin-bottom: 22px;
                box-shadow: 0 18px 40px rgba(0,0,0,0.22);
            }

            .app-hero-title {
                font-size: 1.9rem;
                font-weight: 700;
                color: #f8fafc;
                margin-bottom: 4px;
            }

            .app-hero-subtitle {
                color: var(--muted);
                font-size: 0.98rem;
                line-height: 1.5;
            }

            .metric-card {
                background: linear-gradient(180deg, rgba(17,24,39,0.96), rgba(15,23,42,0.96));
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 18px 18px 16px 18px;
                box-shadow: 0 14px 32px rgba(0,0,0,0.18);
                min-height: 120px;
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.84rem;
                margin-bottom: 8px;
            }

            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                color: #f8fafc;
                line-height: 1.1;
            }

            .metric-subtitle {
                margin-top: 8px;
                color: var(--muted);
                font-size: 0.84rem;
            }

            .section-card {
                background: linear-gradient(180deg, rgba(17,24,39,0.94), rgba(15,23,42,0.95));
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 20px 20px 16px 20px;
                margin-bottom: 18px;
                box-shadow: 0 14px 28px rgba(0,0,0,0.16);
            }

            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #f8fafc;
                margin-bottom: 4px;
            }

            .section-subtitle {
                color: var(--muted);
                font-size: 0.92rem;
                margin-bottom: 14px;
            }

            .answer-box {
                background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(17,24,39,0.98));
                border: 1px solid rgba(96,165,250,0.20);
                border-left: 5px solid var(--accent);
                border-radius: 18px;
                padding: 18px;
                color: #f8fafc;
                line-height: 1.7;
                font-size: 1rem;
                margin-bottom: 14px;
            }

            .source-chip {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                background: rgba(56, 189, 248, 0.10);
                border: 1px solid rgba(56, 189, 248, 0.18);
                color: #bfdbfe;
                font-size: 0.84rem;
                margin-right: 8px;
                margin-bottom: 8px;
            }

            .status-badge {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 600;
                letter-spacing: 0.01em;
            }

            .status-completed {
                background: rgba(34,197,94,0.12);
                border: 1px solid rgba(34,197,94,0.24);
                color: #86efac;
            }

            .status-processing, .status-running, .status-pending {
                background: rgba(245,158,11,0.12);
                border: 1px solid rgba(245,158,11,0.24);
                color: #fde68a;
            }

            .status-failed {
                background: rgba(239,68,68,0.12);
                border: 1px solid rgba(239,68,68,0.24);
                color: #fca5a5;
            }

            div[data-testid="stDataFrame"] {
                border-radius: 16px;
                overflow: hidden;
                border: 1px solid var(--border);
            }

            .stButton > button {
                width: 100%;
                border-radius: 12px;
                font-weight: 600;
                border: 1px solid rgba(148,163,184,0.18);
                min-height: 42px;
            }

            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
                border-radius: 12px !important;
            }

            .stFileUploader > div {
                border-radius: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )