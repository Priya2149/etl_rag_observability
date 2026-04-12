from __future__ import annotations

import pandas as pd
import streamlit as st


def render_table(data, use_container_width: bool = True) -> None:
    if isinstance(data, list):
        if not data:
            st.info("No data available.")
            return
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=use_container_width, hide_index=True)