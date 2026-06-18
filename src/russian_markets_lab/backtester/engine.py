"""Simple vectorized backtesting engine."""

from __future__ import annotations

import pandas as pd

from russian_markets_lab.backtester.costs import calculate_turnover
from russian_markets_lab.backtester.metrics import metrics_summary
from russian_markets_lab.backtester.portfolio import (
    equity_curve_from_returns,
    normalize_weights,
)


def run_vectorized_backtest(
    prices: pd.DataFrame,
    signals: pd.DataFrame,
    commission_bps: float = 5.0,
    slippage_bps: float = 10.0,
    long_short: bool = True,
) -> dict[str, object]:
    """Run a daily vectorized backtest with simple turnover-based costs."""

    price_returns = prices.pct_change().fillna(0)
    weights = normalize_weights(
        signals.reindex(prices.index).fillna(0), long_short=long_short
    )
    lagged_weights = weights.shift(1).fillna(0)
    gross_returns = (lagged_weights * price_returns).sum(axis=1)
    turnover = calculate_turnover(weights)
    cost_returns = turnover * (commission_bps + slippage_bps) / 10_000
    net_returns = gross_returns - cost_returns
    equity = equity_curve_from_returns(net_returns)
    summary = metrics_summary(net_returns, equity)
    summary["turnover"] = float(turnover.mean())
    summary["exposure"] = float((weights.abs().sum(axis=1) > 0).mean())
    return {
        "returns": net_returns,
        "gross_returns": gross_returns,
        "weights": weights,
        "turnover": turnover,
        "equity_curve": equity,
        "metrics": summary,
    }


def walk_forward_splits(
    data: pd.DataFrame,
    train_window: int,
    test_window: int,
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Create walk-forward train/test splits."""

    splits: list[tuple[pd.DataFrame, pd.DataFrame]] = []
    start = 0
    while start + train_window + test_window <= len(data):
        train = data.iloc[start : start + train_window].copy()
        test = data.iloc[
            start + train_window : start + train_window + test_window
        ].copy()
        splits.append((train, test))
        start += test_window
    return splits
