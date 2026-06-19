"""
ui/sidebar.py

Purpose
-------
Renders every sidebar control and returns a single plain dict describing
the user's choices. No business logic, no data fetching — app.py decides
what to do with the returned state.

Inputs
------
None (reads defaults from config/settings.py).

Outputs
-------
dict:
{
    "market": "All" | "India" | "USA",
    "option": "Today" | "Yesterday" | "Custom Date",
    "custom_date": date | None,
    "sma_threshold": float,
    "ema_threshold": float,
    "run_analysis": bool,
}

How it connects
----------------
app.py calls render_sidebar() once per script run and uses the returned
dict to decide which stocks to loop over and which thresholds to pass into
core/scanners.py.
"""

import streamlit as st

from config.settings import (
    DEFAULT_SMA_THRESHOLD,
    DEFAULT_EMA_THRESHOLD,
    SMA_THRESHOLD_RANGE,
    EMA_THRESHOLD_RANGE,
)


def render_sidebar() -> dict:
    with st.sidebar:
        st.header("⚙️ Controls")

        market = st.selectbox("Market", ["All", "India", "USA"], index=0)

        option = st.selectbox("Select Date Option", ["Today", "Yesterday", "Custom Date"])

        custom_date = None
        if option == "Custom Date":
            custom_date = st.date_input("Choose Date", format="DD/MM/YYYY")

        st.markdown("---")
        st.subheader("🎯 Scanner Settings")

        sma_min, sma_max, sma_step = SMA_THRESHOLD_RANGE
        sma_threshold = st.slider(
            "SMA10 Distance %",
            min_value=sma_min,
            max_value=sma_max,
            value=float(DEFAULT_SMA_THRESHOLD),
            step=sma_step,
        )

        ema_min, ema_max, ema_step = EMA_THRESHOLD_RANGE
        ema_threshold = st.slider(
            "EMA10 Distance %",
            min_value=ema_min,
            max_value=ema_max,
            value=float(DEFAULT_EMA_THRESHOLD),
            step=ema_step,
        )

        run_analysis = st.button("🚀 Run Analysis", use_container_width=True)

    return {
        "market": market,
        "option": option,
        "custom_date": custom_date,
        "sma_threshold": sma_threshold,
        "ema_threshold": ema_threshold,
        "run_analysis": run_analysis,
    }
