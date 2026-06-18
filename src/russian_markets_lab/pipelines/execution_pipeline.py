"""Execution cost snapshot pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.execution import compare_execution_styles
from russian_markets_lab.data.io import write_processed_dataset


def build_execution_snapshot(
    liquidity: pd.DataFrame,
    default_order_value: float = 1_000_000,
) -> pd.DataFrame:
    """Build execution cost comparison using liquidity-derived assumptions."""

    if liquidity.empty:
        execution = pd.DataFrame(
            columns=[
                "execution_style",
                "avg_slippage_bps",
                "commission_bps",
                "market_impact_bps",
                "total_cost_bps",
                "fill_rate",
                "execution_risk",
            ]
        )
    else:
        row = liquidity.iloc[0]
        adv = float(row.get("avg_value", 250_000_000) or 250_000_000)
        if not np.isfinite(adv) or adv <= 0:
            adv = 250_000_000
        spread_bps = float(row.get("spread_bps", 15.0) or 15.0)
        if not np.isfinite(spread_bps) or spread_bps < 0:
            spread_bps = 15.0
        volatility = float(row.get("realized_volatility", 0.35) or 0.35)
        if not np.isfinite(volatility) or volatility < 0:
            volatility = 0.35
        execution = compare_execution_styles(
            order_value=min(default_order_value, max(adv * 0.02, default_order_value)),
            avg_daily_value=adv,
            spread_bps=spread_bps,
            volatility=volatility,
            commission_bps=5.0,
        )
        execution["total_cost_rub"] = (
            execution["total_cost_bps"] / 10_000 * default_order_value
        )
    write_processed_dataset(
        execution,
        "execution_comparison",
        source="Processed from liquidity snapshot assumptions",
        endpoints=["liquidity_radar processed dataset"],
        parameters={"default_order_value": default_order_value},
        limitations=[
            "Execution model is a simplified diagnostic.",
            "No order book depth, queue position, broker routing or real order placement is modeled.",
        ],
    )
    return execution
