"""Transaction cost utilities."""

from __future__ import annotations

import pandas as pd


def apply_commission(
    trades: pd.DataFrame,
    commission_bps: float,
) -> pd.DataFrame:
    """Add commission costs to a trades table."""

    out = trades.copy()
    notional = out.get("notional")
    if notional is None:
        notional = out["quantity"].abs() * out["price"]
        out["notional"] = notional
    out["commission"] = (
        pd.to_numeric(notional, errors="coerce").abs() * commission_bps / 10_000
    )
    return out


def apply_slippage(
    trades: pd.DataFrame,
    slippage_bps: float,
) -> pd.DataFrame:
    """Add slippage-adjusted execution prices and costs."""

    out = trades.copy()
    side = out.get("side", "buy")
    direction = (
        pd.Series(side, index=out.index)
        .astype(str)
        .str.lower()
        .map({"buy": 1, "sell": -1})
        .fillna(1)
    )
    out["execution_price"] = out["price"] * (1 + direction * slippage_bps / 10_000)
    out["slippage"] = (out["execution_price"] - out["price"]).abs() * out[
        "quantity"
    ].abs()
    return out


def calculate_turnover(weights: pd.DataFrame) -> pd.Series:
    """Calculate one-way portfolio turnover from weights."""

    return weights.diff().abs().sum(axis=1).fillna(0) / 2
