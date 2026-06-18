"""Volatility analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_returns(prices: pd.Series, log: bool = True) -> pd.Series:
    """Calculate simple or log returns from a price series."""

    clean = pd.to_numeric(prices, errors="coerce").dropna()
    returns = np.log(clean / clean.shift(1)) if log else clean.pct_change()
    return returns.replace([np.inf, -np.inf], np.nan).dropna()


def realized_volatility(
    prices: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized realized volatility."""

    returns = calculate_returns(prices)
    if returns.empty:
        return float("nan")
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def rolling_volatility(
    prices: pd.Series,
    window: int = 20,
    periods_per_year: int = 252,
) -> pd.Series:
    """Calculate rolling annualized volatility."""

    returns = calculate_returns(prices)
    return returns.rolling(window).std() * np.sqrt(periods_per_year)


def parkinson_volatility(
    high: pd.Series,
    low: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized Parkinson high-low volatility estimator."""

    high_values = pd.to_numeric(high, errors="coerce")
    low_values = pd.to_numeric(low, errors="coerce")
    valid = (high_values > 0) & (low_values > 0)
    if not valid.any():
        return float("nan")
    log_hl = np.log(high_values[valid] / low_values[valid])
    variance = (log_hl**2).mean() / (4 * np.log(2))
    return float(np.sqrt(variance * periods_per_year))
