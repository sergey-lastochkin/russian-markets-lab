"""Mean-reversion research signal."""

from __future__ import annotations

import pandas as pd


def generate_signals(
    data: pd.DataFrame,
    window: int = 20,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.5,
    **kwargs,
) -> pd.DataFrame:
    """Generate z-score mean-reversion signals."""

    del kwargs
    mean = data.rolling(window).mean()
    std = data.rolling(window).std()
    zscore = (data - mean) / std
    signals = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    signals[zscore < -entry_threshold] = 1.0
    signals[zscore > entry_threshold] = -1.0
    signals[zscore.abs() < exit_threshold] = 0.0
    return signals.fillna(0)
