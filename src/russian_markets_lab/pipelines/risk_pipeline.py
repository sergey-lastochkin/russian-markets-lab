"""Portfolio risk snapshot pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.risk import (
    correlation_matrix,
    portfolio_returns,
    risk_summary_table,
    stress_test_portfolio,
)
from russian_markets_lab.data.io import write_processed_dataset


def build_risk_snapshot(
    candles_by_ticker: dict[str, pd.DataFrame],
    universe: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build risk snapshot from real candle returns where available."""

    close_series: dict[str, pd.Series] = {}
    for ticker, candles in candles_by_ticker.items():
        lower = candles.copy()
        lower.columns = [str(col).lower() for col in lower.columns]
        if {"begin", "close"}.issubset(lower.columns):
            close_series[ticker] = pd.to_numeric(
                lower.set_index("begin")["close"], errors="coerce"
            )
    if len(close_series) < 2:
        risk = pd.DataFrame(columns=["section", "metric", "value"])
    else:
        prices = pd.DataFrame(close_series).dropna(how="all")
        returns = prices.pct_change(fill_method=None).dropna(how="all").fillna(0)
        weights = {ticker: 1 / len(returns.columns) for ticker in returns.columns}
        port_ret = portfolio_returns(returns, weights)
        summary = risk_summary_table(port_ret)
        summary.insert(0, "section", "portfolio")
        corr = correlation_matrix(returns)
        corr_summary = pd.DataFrame(
            [
                {
                    "section": "correlation",
                    "metric": "avg_pairwise_correlation",
                    "value": float(
                        corr.where(~np.eye(len(corr), dtype=bool)).stack().mean()
                    ),
                },
                {
                    "section": "correlation",
                    "metric": "asset_count",
                    "value": float(len(corr)),
                },
            ]
        )
        positions = pd.DataFrame(
            {
                "instrument": list(weights),
                "position": list(weights.values()),
                "risk_factor": ["equity"] * len(weights),
            }
        )
        stress = stress_test_portfolio(positions)
        stress_summary = (
            stress.groupby("scenario", as_index=False)["portfolio_pnl_pct"]
            .first()
            .rename(columns={"scenario": "metric", "portfolio_pnl_pct": "value"})
        )
        stress_summary.insert(0, "section", "stress")
        risk = pd.concat([summary, corr_summary, stress_summary], ignore_index=True)
    write_processed_dataset(
        risk,
        "risk_snapshot",
        source="Processed from real MOEX candle returns where available",
        endpoints=["TQBR candles endpoint per selected ticker"],
        limitations=[
            "Risk snapshot uses historical daily returns for selected liquid tickers.",
            "Stress scenarios are simplified diagnostics and not forecasts.",
        ],
    )
    return risk
