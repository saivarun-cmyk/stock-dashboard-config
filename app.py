"""
app.py

Purpose
-------
The thin orchestration layer. Owns page config, CSS, the time header, and
the top-level "run analysis" control flow. It does not contain any
indicator math, scoring logic, or fetch/caching code — those all live in
core/ and services/. This file's job is purely: call sidebar -> loop stocks
from config -> call analyzer -> call scanners -> hand results to ui/.

How it connects
----------------
Imports from every layer (config, core, services, ui) — the only file
allowed to do so. Run with: streamlit run app.py
"""

from datetime import datetime

import pytz
import streamlit as st

from config.settings import PAGE_TITLE, PAGE_ICON, TIMEZONES
from config.stocks_config import INDIAN_STOCKS, USA_STOCKS
from core.analyzer import analyze_stock
from core.scanners import sma10_scanner, ema_scanner, bucket_by_signal, deduplicate
from services.export_service import export_india, export_usa, export_scanner
from services.notification_service import send_notification
from ui.sidebar import render_sidebar
from ui.dashboard import render_kpis
from ui.tables import render_table, render_download_button, render_summary, to_dataframe
from ui.charts import render_signal_distribution

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
<style>
.main {
    background-color: #0E1117;
}
.block-container {
    padding-top: 1rem;
}
.metric-card {
    background-color: #1C2333;
    padding: 15px;
    border-radius: 12px;
}
div[data-testid="stMetric"] {
    background-color: #1C2333;
    border: 1px solid #2F3B52;
    padding: 15px;
    border-radius: 12px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# HEADER
# ==========================================================

st.title(f"🚀 {PAGE_TITLE}")
st.markdown("India + USA Stocks | SMA10 Scanner | Bullish / Neutral / Bearish")

# ==========================================================
# TIME SECTION
# ==========================================================

india_time = datetime.now(pytz.timezone(TIMEZONES["India"]))
usa_time = datetime.now(pytz.timezone(TIMEZONES["USA"]))

c1, c2 = st.columns(2)
with c1:
    st.info(f"🇮🇳 IST Time : {india_time.strftime('%d-%b-%Y %I:%M:%S %p')}")
with c2:
    st.info(f"🇺🇸 New York Time : {usa_time.strftime('%d-%b-%Y %I:%M:%S %p')}")

# ==========================================================
# SIDEBAR
# ==========================================================

state = render_sidebar()

# ==========================================================
# KPI PLACEHOLDERS (created before tabs, like the original layout)
# ==========================================================

kpi_columns = st.columns(6)

# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    [
        "🇮🇳 Indian Stocks",
        "🎯 SMA10 Scanner",
        "📈 EMA10 Above",
        "📉 EMA10 Below",
        "🇺🇸 USA Stocks",
        "🔥 Strong Bullish",
        "➖ Neutral",
        "⚠️ Bearish",
    ]
)

# ==========================================================
# RUN ANALYSIS
# ==========================================================

if state["run_analysis"]:

    run_india = state["market"] in ("All", "India")
    run_usa = state["market"] in ("All", "USA")

    indian_results, usa_results = [], []

    stock_universe = []
    if run_india:
        stock_universe += [("India", name, info) for name, info in INDIAN_STOCKS.items()]
    if run_usa:
        stock_universe += [("USA", name, info) for name, info in USA_STOCKS.items()]

    progress_bar = st.progress(0)
    total = max(len(stock_universe), 1)

    for i, (market_label, name, info) in enumerate(stock_universe, start=1):
        market_key = "INDIA" if market_label == "India" else "USA"
        result = analyze_stock(
            stock_name=name,
            symbol=info["symbol"],
            market=market_key,
            option=state["option"],
            custom_date=state["custom_date"],
            sector=info.get("sector", "N/A"),
        )
        progress_bar.progress(i / total)

        if result is None:
            continue

        if market_label == "India":
            indian_results.append(result)
        else:
            usa_results.append(result)

    all_results = indian_results + usa_results

    # ------------------------------------------------------
    # SCANNERS
    # ------------------------------------------------------
    sma_results = deduplicate(sma10_scanner(all_results, state["sma_threshold"]))
    ema_above_results, ema_below_results = ema_scanner(all_results)
    bullish_results, neutral_results, bearish_results = bucket_by_signal(all_results)

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------
    render_kpis(
        kpi_columns,
        {
            "india": len(indian_results),
            "usa": len(usa_results),
            "sma10": len(sma_results),
            "bullish": len(bullish_results),
            "neutral": len(neutral_results),
            "bearish": len(bearish_results),
        },
    )

    # ------------------------------------------------------
    # TABLES
    # ------------------------------------------------------
    indian_df = render_table(tab1, "🇮🇳 Indian Stocks Analysis", indian_results,
                              sort_by="Score", ascending=False)

    sma_df = render_table(tab2, f"🎯 Stocks Within {state['sma_threshold']}% Of SMA10",
                           sma_results, empty_message="No Stocks Found Near SMA10",
                           sort_by="Distance %", ascending=True)

    ema_above_df = render_table(tab3, "📈 Stocks Above EMA10", ema_above_results)
    ema_below_df = render_table(tab4, "📉 Stocks Below EMA10", ema_below_results)

    usa_df = render_table(tab5, "🇺🇸 USA Stocks Analysis", usa_results,
                           sort_by="Score", ascending=False)

    bullish_df = render_table(tab6, "🔥 Bullish Stocks", bullish_results,
                               empty_message="No Bullish Stocks Found",
                               sort_by="Score", ascending=False)

    neutral_df = render_table(tab7, "➖ Neutral Stocks", neutral_results,
                               empty_message="No Neutral Stocks Found",
                               sort_by="Score", ascending=False)

    bearish_df = render_table(tab8, "⚠️ Bearish Stocks", bearish_results,
                               empty_message="No Bearish Stocks Found",
                               sort_by="Score", ascending=True)

    # ------------------------------------------------------
    # EXCEL DOWNLOADS
    # ------------------------------------------------------
    st.markdown("---")
    st.subheader("📥 Downloads")

    d1, d2, d3 = st.columns(3)
    render_download_button(d1, "📥 India Excel", indian_df, "india_stocks.xlsx", export_india)
    render_download_button(d2, "📥 USA Excel", usa_df, "usa_stocks.xlsx", export_usa)
    render_download_button(d3, "📥 SMA Scanner Excel", sma_df, "sma_scanner.xlsx", export_scanner)

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------
    render_summary(len(bullish_df), len(neutral_df), len(bearish_df))

    # ------------------------------------------------------
    # OPTIONAL CHART
    # ------------------------------------------------------
    render_signal_distribution(
        {
            "Strong Bullish": sum(1 for r in all_results if r["Signal"] == "🔥 Strong Bullish"),
            "Bullish": sum(1 for r in all_results if r["Signal"] == "✅ Bullish"),
            "Neutral": len(neutral_results),
            "Bearish": sum(1 for r in all_results if r["Signal"] == "⚠️ Bearish"),
            "Strong Bearish": sum(1 for r in all_results if r["Signal"] == "❌ Strong Bearish"),
        }
    )

    # ------------------------------------------------------
    # NOTIFICATIONS (placeholder, future Telegram/WhatsApp hook)
    # ------------------------------------------------------
    st.markdown("---")
    st.info("🔔 Telegram Alerts Module Coming Soon")
    send_notification(
        f"Analysis run complete: {len(bullish_results)} bullish, "
        f"{len(neutral_results)} neutral, {len(bearish_results)} bearish."
    )

# ==========================================================
# END
# ==========================================================
