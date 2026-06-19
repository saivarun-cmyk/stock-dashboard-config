"""
utils/helpers.py

Purpose
-------
Small, pure, framework-agnostic helpers used across layers: logging setup
and safe numeric conversion. Nothing here imports streamlit, yfinance, or
pandas business logic — keep it that way so it stays trivially testable.

Inputs / Outputs
-----------------
get_logger(name) -> logging.Logger
safe_float(value) -> float | None
any_nan(values: list) -> bool

How it connects
----------------
Every layer (services, core, ui, app.py) calls get_logger(__name__) for
consistent log formatting. core/data_fetcher.py and core/analyzer.py use
safe_float/any_nan to replicate the original app's NaN-guard behavior.
"""

import logging

from config.settings import LOG_LEVEL, LOG_FORMAT

_CONFIGURED = False


def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, "INFO"), format=LOG_FORMAT)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with consistent formatting/level."""
    _configure_root_logger()
    return logging.getLogger(name)


def safe_float(value) -> float | None:
    """Convert a value to float, returning None instead of raising."""
    try:
        result = float(value)
        return None if result != result else result  # filters NaN (NaN != NaN)
    except (TypeError, ValueError):
        return None


def any_nan(values: list) -> bool:
    """True if any element in values is None or NaN."""
    return any(v is None for v in (safe_float(v) for v in values))
