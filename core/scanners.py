"""
core/scanners.py

Purpose
-------
Pure filtering/bucketing over a list of already-computed analyzer results.
No fetching, no Streamlit — just list/DataFrame operations, so these are
trivially unit-testable.

Inputs
------
results: list[dict]  - output of core.analyzer.analyze_stock(), collected
                        across all stocks for the run.
threshold: float      - % distance cutoff (sidebar slider value)

Outputs
-------
sma10_scanner(results, threshold) -> list[dict]   # within threshold% of SMA10
ema_scanner(results) -> tuple[list[dict], list[dict]]  # (above, below)
bucket_by_signal(results) -> tuple[list, list, list]   # (bullish, neutral, bearish)

How it connects
----------------
app.py calls these once per market after collecting analyzer results, then
passes the lists into ui/tables.py for rendering and services/export_service.py
for Excel export.
"""


def sma10_scanner(results: list[dict], threshold: float) -> list[dict]:
    """Stocks whose Distance % from SMA10 is within `threshold`."""
    return [r for r in results if r["Distance %"] <= threshold]


def ema_scanner(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split results into (above EMA10, below EMA10) — same rule as original app."""
    above = [r for r in results if r["Close"] > r["EMA10"]]
    below = [r for r in results if r["Close"] <= r["EMA10"]]
    return above, below


def ema_scanner_within_threshold(results: list[dict], threshold: float) -> list[dict]:
    """
    Optional extra filter: EMA10 candidates within `threshold`% distance.
    Additive — does not change the above/below split used by the original tabs.
    """
    return [r for r in results if r["EMA Distance %"] <= threshold]


def bucket_by_signal(results: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Split results into (bullish, neutral, bearish) buckets, same grouping as original app."""
    bullish = [r for r in results if r["Signal"] in ("🔥 Strong Bullish", "✅ Bullish")]
    neutral = [r for r in results if r["Signal"] == "➖ Neutral"]
    bearish = [r for r in results if r["Signal"] in ("⚠️ Bearish", "❌ Strong Bearish")]
    return bullish, neutral, bearish


def deduplicate(results: list[dict]) -> list[dict]:
    """Drop duplicate (Stock, Market) pairs, preserving first occurrence (matches original sma_df dedup)."""
    seen = set()
    deduped = []
    for r in results:
        key = (r["Stock"], r["Market"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped
