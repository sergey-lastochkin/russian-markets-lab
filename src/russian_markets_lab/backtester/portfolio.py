"""Portfolio construction utilities for research backtests."""

from __future__ import annotations

import pandas as pd


def normalize_weights(signals: pd.DataFrame, long_short: bool = True) -> pd.DataFrame:
    """Convert raw signals into normalized daily portfolio weights."""

    weights = signals.copy().astype(float)
    if not long_short:
        weights = weights.clip(lower=0)
    gross = weights.abs().sum(axis=1).replace(0, pd.NA)
    return weights.div(gross, axis=0).fillna(0)


def equity_curve_from_returns(
    returns: pd.Series, initial_capital: float = 1.0
) -> pd.Series:
    """Build an equity curve from periodic returns."""

    return initial_capital * (1 + returns.fillna(0)).cumprod()


def train_test_split(
    data: pd.DataFrame,
    train_size: float = 0.7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split time-series data into train and test partitions."""

    split = int(len(data) * train_size)
    return data.iloc[:split].copy(), data.iloc[split:].copy()
