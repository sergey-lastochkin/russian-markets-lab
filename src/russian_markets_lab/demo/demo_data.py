"""Illustrative demo data for explicit dashboard demo mode only."""

from __future__ import annotations

import pandas as pd


def load_demo_returns() -> pd.DataFrame:
    """This function returns illustrative demo data only.

    It must not be presented as real market output.
    """

    return pd.DataFrame(
        {
            "DEMO_A": [0.003, -0.004, 0.002, 0.001, -0.002],
            "DEMO_B": [0.001, -0.002, 0.003, -0.001, 0.002],
            "DEMO_C": [-0.001, 0.002, 0.001, -0.003, 0.004],
        }
    )


def load_demo_equity_curve() -> pd.DataFrame:
    """This function returns illustrative demo data only.

    It must not be presented as real market output.
    """

    returns = pd.Series([0.006, -0.003, 0.004, -0.005, 0.002], name="returns")
    equity = (1 + returns).cumprod()
    return pd.DataFrame(
        {
            "equity_curve": equity,
            "drawdown": equity / equity.cummax() - 1,
        }
    )


def load_demo_execution_inputs() -> dict[str, float]:
    """This function returns illustrative demo data only.

    It must not be presented as real market output.
    """

    return {
        "order_value": 1_000_000.0,
        "avg_daily_value": 100_000_000.0,
        "spread_bps": 15.0,
        "volatility": 0.30,
        "commission_bps": 5.0,
    }
