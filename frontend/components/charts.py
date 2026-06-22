from __future__ import annotations

import pandas as pd
import plotly.express as px


def _base_layout(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb",
        margin=dict(l=10, r=10, t=45, b=10),
    )
    return fig


def status_pie_chart(df: pd.DataFrame, status_col: str, title: str):
    counts = df[status_col].fillna("unknown").value_counts().reset_index()
    counts.columns = ["status", "count"]

    fig = px.pie(
        counts,
        names="status",
        values="count",
        title=title,
        hole=0.58,
    )
    return _base_layout(fig)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, x_title: str = "", y_title: str = ""):
    fig = px.bar(df, x=x, y=y, title=title)
    fig.update_layout(xaxis_title=x_title, yaxis_title=y_title)
    return _base_layout(fig)


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, x_title: str = "", y_title: str = ""):
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    fig.update_layout(xaxis_title=x_title, yaxis_title=y_title)
    return _base_layout(fig)


def should_render_chart(df: pd.DataFrame, y_col: str) -> bool:
    if df.empty or y_col not in df.columns:
        return False

    non_null = df[y_col].dropna()
    return len(non_null) > 0