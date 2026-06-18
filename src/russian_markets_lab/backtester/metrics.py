"""Backtest performance metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.risk import max_drawdown


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Calculate annualized Sharpe ratio."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty or clean.std(ddof=1) == 0:
        return float("nan")
    excess = clean - risk_free_rate / 252
    return float(excess.mean() / clean.std(ddof=1) * np.sqrt(252))


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Calculate annualized Sortino ratio."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    downside = clean[clean < 0]
    if clean.empty or downside.std(ddof=1) == 0:
        return float("nan")
    excess = clean - risk_free_rate / 252
    return float(excess.mean() / downside.std(ddof=1) * np.sqrt(252))


def cagr(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate compound annual growth rate from an equity curve."""

    equity = pd.to_numeric(equity_curve, errors="coerce").dropna()
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return float("nan")
    years = (len(equity) - 1) / periods_per_year
    if years <= 0:
        return float("nan")
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)


def hit_rate(returns: pd.Series) -> float:
    """Calculate share of positive return observations."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float((clean > 0).mean())


def metrics_summary(returns: pd.Series, equity_curve: pd.Series) -> dict[str, float]:
    """Calculate a compact metric summary."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    return {
        "sharpe_ratio": sharpe_ratio(clean),
        "sortino_ratio": sortino_ratio(clean),
        "cagr": cagr(equity_curve),
        "volatility": (
            float(clean.std(ddof=1) * np.sqrt(252)) if not clean.empty else float("nan")
        ),
        "max_drawdown": max_drawdown(equity_curve),
        "hit_rate": hit_rate(clean),
    }
