"""Statistical arbitrage research skeleton."""

from __future__ import annotations

import pandas as pd


def generate_signals(
    data: pd.DataFrame,
    pair: tuple[str, str] | None = None,
    window: int = 60,
    entry_threshold: float = 2.0,
    **kwargs,
) -> pd.DataFrame:
    """Generate pair-spread z-score signals.

    Cointegration testing is intentionally left as a research extension.
    """

    del kwargs
    if pair is None:
        if data.shape[1] < 2:
            return pd.DataFrame(0.0, index=data.index, columns=data.columns)
        pair = (data.columns[0], data.columns[1])
    first, second = pair
    spread = data[first] - data[second]
    zscore = (spread - spread.rolling(window).mean()) / spread.rolling(window).std()
    signals = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    signals.loc[zscore < -entry_threshold, first] = 1.0
    signals.loc[zscore < -entry_threshold, second] = -1.0
    signals.loc[zscore > entry_threshold, first] = -1.0
    signals.loc[zscore > entry_threshold, second] = 1.0
    return signals.fillna(0)
