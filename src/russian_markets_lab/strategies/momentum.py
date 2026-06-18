"""Momentum research signal."""

from __future__ import annotations

import pandas as pd


def generate_signals(
    data: pd.DataFrame,
    lookback: int = 63,
    trend_window: int = 200,
    volatility_window: int = 20,
    max_volatility: float = 0.6,
    **kwargs,
) -> pd.DataFrame:
    """Generate momentum signals with trend and volatility filters."""

    del kwargs
    prices = data.copy()
    returns = prices.pct_change(lookback)
    trend = prices > prices.rolling(trend_window).mean()
    volatility = prices.pct_change().rolling(volatility_window).std() * (252**0.5)
    signals = (returns > 0).astype(float)
    signals = signals.where(trend & (volatility < max_volatility), 0.0)
    return signals.fillna(0)
