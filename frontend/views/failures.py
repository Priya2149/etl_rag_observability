from __future__ import annotations

import pandas as pd
import streamlit as st

from api.client import get_recent_failures
from components.charts import bar_chart
from components.tables import render_table


def render_failures() -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Failures</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Centralized error visibility across monitored services</div>',
        unsafe_allow_html=True,
    )

    try:
        failures = get_recent_failures()
        render_table(failures)

        if failures:
            df = pd.DataFrame(failures)
            if "service" in df.columns:
                counts = df["service"].value_counts().reset_index()
                counts.columns = ["service", "count"]

                st.plotly_chart(
                    bar_chart(
                        counts,
                        x="service",
                        y="count",
                        title="Failures by Service",
                        x_title="Service",
                        y_title="Failure Count",
                    ),
                    use_container_width=True,
                )
        else:
            st.success("No recent failures found.")

    except Exception as e:
        st.error(f"Failed to fetch failures: {e}")

    st.markdown("</div>", unsafe_allow_html=True)