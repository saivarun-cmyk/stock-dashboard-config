"""
ui/dashboard.py

Purpose
-------
Renders the 6 KPI metric cards at the top of the page. Pure presentation —
takes pre-computed counts in, renders st.metric cards out.

Inputs
------
counts: dict with keys "india", "usa", "sma10", "bullish", "neutral", "bearish"
columns: the 6 st.columns() placeholders created in app.py (so layout stays
         above the tabs, matching the original app's structure)

Outputs
-------
None (renders directly into the provided Streamlit columns).

How it connects
----------------
app.py creates the 6 columns once near the top of the page (so they appear
before the tabs, like the original), then calls render_kpis() with those
columns after the analysis run completes.
"""


def render_kpis(columns, counts: dict) -> None:
    k1, k2, k3, k4, k5, k6 = columns

    with k1:
        k1.metric("🇮🇳 India", counts.get("india", 0))
    with k2:
        k2.metric("🇺🇸 USA", counts.get("usa", 0))
    with k3:
        k3.metric("🎯 SMA10", counts.get("sma10", 0))
    with k4:
        k4.metric("🔥 Bullish", counts.get("bullish", 0))
    with k5:
        k5.metric("➖ Neutral", counts.get("neutral", 0))
    with k6:
        k6.metric("⚠️ Bearish", counts.get("bearish", 0))
