import html
import streamlit as st


LIGHT_THEME = {
    "name": "light",
    "app_bg": "#f5f7fb",
    "app_gradient": "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(37,99,235,0.08) 0%, transparent 60%), linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%)",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "surface_soft": "#f1f5f9",
    "sidebar": "#ffffff",
    "border": "rgba(15, 23, 42, 0.10)",
    "border_strong": "rgba(15, 23, 42, 0.16)",
    "text": "#0f172a",
    "text_soft": "#475569",
    "text_muted": "#64748b",
    "primary": "#2563eb",
    "primary_soft": "rgba(37,99,235,0.10)",
    "primary_hover": "rgba(37,99,235,0.16)",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#dc2626",
    "shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
    "shadow_soft": "0 6px 20px rgba(15, 23, 42, 0.06)",
}

DARK_THEME = {
    "name": "dark",
    "app_bg": "#040812",
    "app_gradient": "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(14,165,233,0.07) 0%, transparent 60%), linear-gradient(180deg, #040812 0%, #060d1a 100%)",
    "surface": "#0b1220",
    "surface_alt": "#0f172a",
    "surface_soft": "#060d1a",
    "sidebar": "#07111f",
    "border": "rgba(14,165,233,0.12)",
    "border_strong": "rgba(14,165,233,0.22)",
    "text": "#e2e8f0",
    "text_soft": "#cbd5e1",
    "text_muted": "#64748b",
    "primary": "#38bdf8",
    "primary_soft": "rgba(14,165,233,0.10)",
    "primary_hover": "rgba(14,165,233,0.18)",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "shadow": "0 12px 32px rgba(2, 8, 23, 0.34)",
    "shadow_soft": "0 8px 24px rgba(2, 8, 23, 0.24)",
}


def init_theme(default: str = "dark"):
    if "ui_theme" not in st.session_state:
        st.session_state["ui_theme"] = default if default in {"light", "dark"} else "dark"


def get_theme_tokens():
    init_theme()
    return LIGHT_THEME if st.session_state.get("ui_theme") == "light" else DARK_THEME


def toggle_theme():
    init_theme()
    st.session_state["ui_theme"] = "light" if st.session_state["ui_theme"] == "dark" else "dark"


def theme_toggle_button(position: str = "top-right"):
    init_theme()
    is_light = st.session_state.get("ui_theme") == "light"
    icon = "dark_mode" if is_light else "light_mode"
    help_text = "Switch to dark mode" if is_light else "Switch to light mode"

    if position == "top-right":
        _, col = st.columns([12, 1])
        with col:
            if st.button(f":material/{icon}:", key=f"theme_toggle_{position}", help=help_text, use_container_width=True):
                toggle_theme()
                st.rerun()
    else:
        if st.button(f":material/{icon}:", key=f"theme_toggle_{position}", help=help_text, use_container_width=True):
            toggle_theme()
            st.rerun()


def inject_global_styles():
    t = get_theme_tokens()

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Material+Icons+Round&display=swap');

        :root {{
            --app-bg: {t['app_bg']};
            --app-gradient: {t['app_gradient']};
            --surface: {t['surface']};
            --surface-alt: {t['surface_alt']};
            --surface-soft: {t['surface_soft']};
            --sidebar: {t['sidebar']};
            --border: {t['border']};
            --border-strong: {t['border_strong']};
            --text: {t['text']};
            --text-soft: {t['text_soft']};
            --text-muted: {t['text_muted']};
            --primary: {t['primary']};
            --primary-soft: {t['primary_soft']};
            --primary-hover: {t['primary_hover']};
            --success: {t['success']};
            --warning: {t['warning']};
            --danger: {t['danger']};
            --shadow: {t['shadow']};
            --shadow-soft: {t['shadow_soft']};
            --radius-xl: 22px;
            --radius-lg: 18px;
            --radius-md: 14px;
            --radius-sm: 10px;
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--text);
        }}

        .stApp {{
            background: var(--app-bg);
            background-image: var(--app-gradient);
        }}

        .block-container {{
            padding-top: 1.2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1400px !important;
        }}

        section[data-testid="stSidebar"] {{
            background: var(--sidebar) !important;
            border-right: 1px solid var(--border) !important;
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.1rem !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--text) !important;
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: 1.75rem !important;
            font-weight: 700 !important;
        }}

        .stCaption, [data-testid="stCaptionContainer"] p {{
            color: var(--text-muted) !important;
            font-size: 0.84rem !important;
        }}

        hr {{
            border: none !important;
            border-top: 1px solid var(--border) !important;
            margin: 1.35rem 0 !important;
        }}

        [data-testid="stMetric"] {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            padding: 1rem 1.1rem !important;
            box-shadow: var(--shadow-soft) !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--text-muted) !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
        }}

        [data-testid="stMetricValue"] {{
            font-family: 'JetBrains Mono', monospace !important;
            color: var(--text) !important;
            font-size: 1.7rem !important;
            font-weight: 700 !important;
        }}

        .stButton > button {{
            background: var(--surface) !important;
            border: 1px solid var(--border-strong) !important;
            color: var(--text) !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            min-height: 42px !important;
            transition: all 0.18s ease !important;
            box-shadow: none !important;
        }}

        .stButton > button:hover {{
            border-color: var(--primary) !important;
            background: var(--primary-soft) !important;
            color: var(--primary) !important;
        }}

        .stButton > button:focus {{
            box-shadow: 0 0 0 3px rgba(59,130,246,0.16) !important;
            border-color: var(--primary) !important;
        }}

        [data-testid="stFileUploader"] {{
            border: 1px dashed var(--border-strong) !important;
            border-radius: var(--radius-md) !important;
            background: var(--surface-soft) !important;
            padding: 0.7rem !important;
        }}

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
            font-size: 0.92rem !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
            box-shadow: var(--shadow-soft) !important;
        }}

        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, var(--primary) 0%, #60a5fa 100%) !important;
            border-radius: 999px !important;
        }}

        .stProgress > div > div > div {{
            background: var(--surface-soft) !important;
            border-radius: 999px !important;
        }}

        .stSuccess, .stWarning, .stError, .stInfo {{
            border-radius: 12px !important;
            border-width: 1px !important;
            box-shadow: var(--shadow-soft) !important;
        }}

        .stSuccess {{
            background: rgba(16,185,129,0.10) !important;
            border-color: rgba(16,185,129,0.25) !important;
            color: var(--success) !important;
        }}

        .stWarning {{
            background: rgba(245,158,11,0.10) !important;
            border-color: rgba(245,158,11,0.25) !important;
            color: var(--warning) !important;
        }}

        .stError {{
            background: rgba(239,68,68,0.10) !important;
            border-color: rgba(239,68,68,0.25) !important;
            color: var(--danger) !important;
        }}

        .stInfo {{
            background: rgba(59,130,246,0.10) !important;
            border-color: rgba(59,130,246,0.25) !important;
            color: var(--primary) !important;
        }}

        .streamlit-expanderHeader {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text-soft) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }}

        .streamlit-expanderContent {{
            background: var(--surface-alt) !important;
            border: 1px solid var(--border) !important;
            border-top: none !important;
            border-radius: 0 0 12px 12px !important;
        }}

        .surface-card {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: var(--shadow-soft);
        }}

        .upload-zone {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px dashed var(--border-strong);
            border-radius: 18px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-soft);
        }}

        .file-pill, .flag-chip, .nav-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.5rem 0.8rem;
            border-radius: 999px;
            background: var(--surface-soft);
            border: 1px solid var(--border);
            color: var(--text-soft);
            font-size: 0.82rem;
            font-weight: 500;
            margin: 0.18rem 0.35rem 0.18rem 0;
        }}

        .page-shell-card {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1.25rem;
            box-shadow: var(--shadow);
        }}

        .hero-stat {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1.15rem 1.1rem;
            box-shadow: var(--shadow-soft);
        }}

        .hero-stat-label {{
            font-size: 0.74rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
        }}

        .hero-stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.9rem;
            font-weight: 700;
            color: var(--text);
            line-height: 1.1;
        }}

        .hero-stat-sub {{
            font-size: 0.84rem;
            color: var(--text-muted);
            margin-top: 0.35rem;
        }}

        .table-card {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.9rem;
            box-shadow: var(--shadow-soft);
        }}

        .side-stat-box {{
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: var(--shadow_soft);
        }}

        .side-stat-label {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.3rem;
        }}

        .side-stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--text);
        }}

        .health-label {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.45rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str):
    t = get_theme_tokens()
    status = (status or "").lower()

    config = {
        "completed": {"color": t["success"], "icon": "task_alt", "label": "Completed"},
        "running": {"color": t["primary"], "icon": "autorenew", "label": "Running"},
        "pending": {"color": t["warning"], "icon": "schedule", "label": "Pending"},
        "failed": {"color": t["danger"], "icon": "cancel", "label": "Failed"},
    }

    cfg = config.get(
        status,
        {"color": t["text_muted"], "icon": "help", "label": status.title() or "Unknown"},
    )

    st.markdown(
        f"""
        <div style="
            display:inline-flex;
            align-items:center;
            gap:8px;
            padding:6px 12px;
            border-radius:999px;
            background:{cfg['color']}12;
            border:1px solid {cfg['color']}32;
            color:{cfg['color']};
            font-size:0.78rem;
            font-weight:600;
        ">
            <span class="material-icons-round" style="font-size:1rem">{cfg['icon']}</span>
            <span>{cfg['label']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(risk_level: str):
    t = get_theme_tokens()
    risk_level = (risk_level or "").lower()

    config = {
        "low": {"color": t["success"], "icon": "verified", "label": "Low risk"},
        "medium": {"color": t["warning"], "icon": "warning", "label": "Medium risk"},
        "high": {"color": t["danger"], "icon": "gpp_bad", "label": "High risk"},
    }

    cfg = config.get(
        risk_level,
        {"color": t["text_muted"], "icon": "help", "label": risk_level.title() or "Unknown"},
    )

    st.markdown(
        f"""
        <div style="
            display:inline-flex;
            align-items:center;
            gap:8px;
            padding:6px 12px;
            border-radius:999px;
            background:{cfg['color']}12;
            border:1px solid {cfg['color']}32;
            color:{cfg['color']};
            font-size:0.78rem;
            font-weight:600;
        ">
            <span class="material-icons-round" style="font-size:1rem">{cfg['icon']}</span>
            <span>{cfg['label']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "", icon: str = "dashboard"):
    t = get_theme_tokens()
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)

    st.markdown(
        f"""
        <div style="margin:1.35rem 0 0.85rem 0;">
            <div style="display:flex;align-items:center;gap:10px;color:{t['text']};font-weight:700;font-size:1rem;">
                <span class="material-icons-round" style="font-size:1.15rem;color:{t['primary']};">{icon}</span>
                <span>{safe_title}</span>
            </div>
            {"" if not subtitle else f"<div style='margin-top:0.28rem;font-size:0.88rem;color:{t['text_muted']};'>{safe_subtitle}</div>"}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_key_value(label: str, value):
    t = get_theme_tokens()

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(180deg, {t['surface']} 0%, {t['surface_alt']} 100%);
            padding:0.9rem 1rem;
            border-radius:14px;
            border:1px solid {t['border']};
            margin-bottom:0.65rem;
            box-shadow:{t['shadow_soft']};
        ">
            <div style="
                font-size:0.72rem;
                font-weight:600;
                letter-spacing:0.06em;
                text-transform:uppercase;
                color:{t['text_muted']};
                margin-bottom:0.3rem;
            ">{html.escape(str(label))}</div>
            <div style="
                font-size:0.98rem;
                font-weight:700;
                color:{t['text']};
            ">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def answer_box(content: str):
    t = get_theme_tokens()
    safe_content = html.escape(content or "").replace("\n", "<br>")

    st.markdown(
        f"""
        <div style="
            background:{t['surface']};
            border:1px solid {t['border']};
            border-left:4px solid {t['primary']};
            border-radius:16px;
            padding:1rem 1.1rem;
            line-height:1.7;
            font-size:0.92rem;
            color:{t['text_soft']};
            box-shadow:{t['shadow_soft']};
        ">
            {safe_content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(icon: str, title: str, caption: str):
    t = get_theme_tokens()

    st.markdown(
        f"""
        <div class="page-shell-card" style="margin-bottom:1.25rem;">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;">
                <div style="display:flex;align-items:flex-start;gap:1rem;">
                    <div style="
                        width:52px;
                        height:52px;
                        border-radius:16px;
                        background:{t['primary_soft']};
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        flex-shrink:0;
                    ">
                        <span class="material-icons-round" style="font-size:1.45rem;color:{t['primary']};">{icon}</span>
                    </div>
                    <div>
                        <div style="font-size:1.45rem;font-weight:700;color:{t['text']};letter-spacing:-0.02em;">
                            {html.escape(title)}
                        </div>
                        <div style="margin-top:0.35rem;font-size:0.92rem;color:{t['text_muted']};max-width:880px;">
                            {html.escape(caption)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_item(label: str, icon: str):
    st.markdown(
        f"""
        <div class="nav-chip">
            <span class="material-icons-round" style="font-size:0.95rem">{html.escape(icon)}</span>
            {html.escape(label)}
        </div>
        """,
        unsafe_allow_html=True,
    )