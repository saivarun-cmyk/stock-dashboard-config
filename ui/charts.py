"""
ui/charts.py

Purpose
-------
Optional visual additions that don't exist in the original app but are
additive and safe: a simple bar chart of how many stocks fall into each
signal bucket. Does not replace or alter any existing table/tab.

Inputs
------
counts: dict - {"Strong Bullish": n, "Bullish": n, "Neutral": n, "Bearish": n, "Strong Bearish": n}

Outputs
-------
None (renders an st.bar_chart).

How it connects
----------------
app.py may optionally call render_signal_distribution() after the
analysis run. Safe to remove without affecting any other module.
"""

import pandas as pd
import streamlit as st


def render_signal_distribution(counts: dict) -> None:
    if not counts or all(v == 0 for v in counts.values()):
        return

    st.markdown("---")
    st.subheader("📊 Signal Distribution")

    df = pd.DataFrame({"Signal": list(counts.keys()), "Count": list(counts.values())})
    st.bar_chart(df.set_index("Signal"))
