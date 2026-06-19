"""
ui/tables.py

Purpose
-------
Renders a results table (with an empty-state warning) inside a given tab,
and optionally a matching download button. Pure presentation — takes a
list[dict] or DataFrame in, renders Streamlit widgets out.

Inputs
------
tab: the st.tabs() context manager to render into
results: list[dict] | pd.DataFrame
empty_message: str shown when results is empty
sort_by: column to sort on (optional)
ascending: sort direction (optional)
height: table height in px (matches original 700px tables)

Outputs
-------
pd.DataFrame - the (possibly sorted) DataFrame that was rendered, so the
caller can also pass it to services/export_service.py for a download
button.

How it connects
----------------
app.py calls render_table() once per tab after running the analysis loop,
using the lists produced by core/scanners.py and core/analyzer.py.
"""

import pandas as pd
import streamlit as st


def to_dataframe(results) -> pd.DataFrame:
    if isinstance(results, pd.DataFrame):
        return results
    return pd.DataFrame(results)


def render_table(tab, title: str, results, empty_message: str = "No Stocks Found",
                  sort_by: str | None = None, ascending: bool = False,
                  height: int = 700) -> pd.DataFrame:
    df = to_dataframe(results)

    if sort_by and not df.empty and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)

    with tab:
        st.subheader(title)
        if df.empty:
            st.warning(empty_message)
        else:
            st.dataframe(df, use_container_width=True, height=height)

    return df


def render_download_button(column, label: str, df: pd.DataFrame, file_name: str,
                            export_fn) -> None:
    """Render a download button only when there is data to export."""
    if df.empty:
        return
    with column:
        st.download_button(
            label=label,
            data=export_fn(df),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def render_summary(bullish_count: int, neutral_count: int, bearish_count: int) -> None:
    st.markdown("---")
    st.subheader("📊 Analysis Summary")

    s1, s2, s3 = st.columns(3)
    with s1:
        st.success(f"🔥 Bullish Stocks : {bullish_count}")
    with s2:
        st.info(f"➖ Neutral Stocks : {neutral_count}")
    with s3:
        st.error(f"⚠️ Bearish Stocks : {bearish_count}")
