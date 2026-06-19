# Stock Analysis Suite V2

A modular Streamlit dashboard for screening Indian and US stocks using
SMA10/20/50, EMA10, RSI14, and 20-day breakout levels, with a scoring
system that buckets stocks into Strong Bullish → Strong Bearish.

## 1. Architecture

```
config/   -> static configuration (stocks, thresholds, cache TTL)
core/     -> pure business logic (indicators, scoring, scanning) — no Streamlit
services/ -> I/O boundaries (Yahoo Finance, Excel export, notifications)
ui/       -> Streamlit rendering only — no business logic
app.py    -> orchestrates the above into the running page
```

**Dependency rule:** `config → core → services → ui → app.py`. Nothing in
`core/` imports Streamlit; nothing in `services/` imports `ui/`. This keeps
the math testable in isolation and means a future API or CLI version could
reuse `core/` and `services/` unchanged.

```
app.py
 ├─ ui/sidebar.py, ui/dashboard.py, ui/tables.py, ui/charts.py
 └─ core/analyzer.py
      ├─ core/data_fetcher.py
      │    └─ services/yahoo_service.py  (cached yfinance calls)
      ├─ core/indicators.py
      └─ core/signals.py
 core/scanners.py        (consumes analyzer results)
 services/export_service.py
 services/notification_service.py
 config/stocks_config.py (drives the run loop)
 config/settings.py      (all tunables)
```

## 2. Installation

```bash
cd stock_analysis_suite
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Running the app

```bash
streamlit run app.py
```

## 4. How to add a stock

Edit **`config/stocks_config.py`** only — no other file needs to change.

```python
INDIAN_STOCKS = {
    ...
    "Wipro": {"symbol": "WIPRO.NS", "sector": "IT"},
}

USA_STOCKS = {
    ...
    "NFLX": {"symbol": "NFLX", "sector": "Technology"},
}
```

- `symbol` must be a valid Yahoo Finance ticker. Indian NSE stocks need the
  `.NS` suffix; the NIFTY index uses `^NSEI`. US tickers are used as-is.
- `sector` is informational only (shown in the tables/export).

## 5. How to modify scanner thresholds

- **Default slider values / ranges:** edit `config/settings.py`:
  ```python
  DEFAULT_SMA_THRESHOLD = 2
  DEFAULT_EMA_THRESHOLD = 2
  SMA_THRESHOLD_RANGE = (0.5, 5.0, 0.5)   # (min, max, step)
  EMA_THRESHOLD_RANGE = (0.5, 5.0, 0.5)
  ```
- **Cache duration** (how long fetched data is reused before re-downloading):
  ```python
  CACHE_TIME = 300  # seconds
  ```
- **Yahoo Finance fetch window:**
  ```python
  YAHOO_PERIOD = "6mo"
  YAHOO_INTERVAL = "1d"
  ```
- **Scoring thresholds** (RSI bands, score cutoffs for each signal label) also
  live in `config/settings.py`, near the bottom.

The user adjusts the *actual* threshold used for a given run from the
sidebar sliders at runtime — `settings.py` only controls the defaults and
slider bounds.

## 6. Module reference

| File | What it does |
|---|---|
| `config/settings.py` | All tunable constants (cache, thresholds, periods, RSI bands). |
| `config/stocks_config.py` | The stock universe — edit this to add/remove tickers. |
| `core/indicators.py` | SMA/EMA/RSI/20-day-high-low math. Pure pandas. |
| `core/data_fetcher.py` | Ticker building, cleaning, date-row selection. |
| `core/signals.py` | Scoring conditions + bullish/bearish label mapping. |
| `core/analyzer.py` | Orchestrates one stock's full analysis into a result dict. |
| `core/scanners.py` | SMA10 proximity scan, EMA10 above/below split, signal buckets. |
| `services/yahoo_service.py` | Cached, error-safe yfinance wrapper. |
| `services/export_service.py` | DataFrame → Excel bytes. |
| `services/notification_service.py` | Notification interface (Telegram/WhatsApp ready). |
| `ui/sidebar.py` | All input controls. |
| `ui/dashboard.py` | KPI metric cards. |
| `ui/tables.py` | Table rendering + download buttons. |
| `ui/charts.py` | Optional signal-distribution bar chart. |
| `app.py` | Wires everything together; the only file run directly. |

## 7. Notes on behavior preservation

Every calculation (SMA windows, EMA span, Wilder RSI formula, 20-day
breakout, the 5-condition score, and the signal label thresholds) is a
direct port of the original single-file app — same formulas, same column
names, same tab structure, same Excel export behavior. The only additions
are: a Market filter and EMA10 threshold slider in the sidebar (additive,
default "All" preserves original behavior), a "Sector" column, and an
optional signal-distribution chart.

## 8. Extending notifications

`services/notification_service.send_notification()` currently only logs.
To add Telegram: implement the `channel == "telegram"` branch with a call
to the Telegram Bot API, and call `send_notification(msg, channel="telegram")`
from `app.py`. No other file needs to change.
