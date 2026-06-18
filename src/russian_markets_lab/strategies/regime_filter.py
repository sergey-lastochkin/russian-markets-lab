"""Market regime filters for research workflows."""

from __future__ import annotations

import pandas as pd


def generate_signals(
    data: pd.DataFrame,
    volatility_window: int = 20,
    trend_window: int = 100,
    liquidity_threshold: float | None = None,
    **kwargs,
) -> pd.DataFrame:
    """Classify volatility, trend, and liquidity regimes."""

    del kwargs
    out = pd.DataFrame(index=data.index)
    price_col = "close" if "close" in data.columns else data.columns[0]
    returns = data[price_col].pct_change()
    vol = returns.rolling(volatility_window).std() * (252**0.5)
    trend = data[price_col] / data[price_col].rolling(trend_window).mean() - 1
    out["volatility_regime"] = pd.cut(
        vol, bins=[-1, 0.2, 0.4, 10], labels=["low", "normal", "high"]
    )
    out["trend_regime"] = pd.cut(
        trend, bins=[-10, -0.05, 0.05, 10], labels=["down", "flat", "up"]
    )
    if "value" in data.columns:
        threshold = (
            liquidity_threshold
            if liquidity_threshold is not None
            else data["value"].rolling(60).median()
        )
        out["liquidity_regime"] = (data["value"] >= threshold).map(
            {True: "liquid", False: "thin"}
        )
    else:
        out["liquidity_regime"] = "unknown"
    return out
