"""Execution cost and fill simulation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_slippage_bps(
    order_value: float,
    avg_daily_value: float,
    spread_bps: float,
    participation_rate: float,
) -> float:
    """Estimate slippage in basis points from spread and participation."""

    if order_value <= 0 or avg_daily_value <= 0:
        return float("nan")
    participation = max(participation_rate, order_value / avg_daily_value)
    return float(max(spread_bps / 2, 0) + 25 * np.sqrt(participation))


def estimate_market_impact(
    order_value: float,
    avg_daily_value: float,
    volatility: float,
) -> float:
    """Estimate market impact in basis points with a square-root model."""

    if order_value <= 0 or avg_daily_value <= 0 or volatility < 0:
        return float("nan")
    return float(volatility * np.sqrt(order_value / avg_daily_value) * 10_000)


def simulate_market_order(
    order_size: float,
    price: float,
    spread_bps: float,
    commission_bps: float,
) -> dict:
    """Simulate a market order cost."""

    notional = order_size * price
    slippage = notional * spread_bps / 2 / 10_000
    commission = notional * commission_bps / 10_000
    return {
        "execution_style": "market",
        "notional": notional,
        "slippage": slippage,
        "commission": commission,
        "total_cost": slippage + commission,
        "fill_rate": 1.0,
    }


def simulate_limit_order(
    order_size: float,
    price: float,
    fill_probability: float,
    commission_bps: float,
) -> dict:
    """Simulate a passive limit order with fill risk."""

    notional = order_size * price
    fill_rate = float(np.clip(fill_probability, 0, 1))
    commission = notional * fill_rate * commission_bps / 10_000
    return {
        "execution_style": "limit",
        "notional": notional,
        "slippage": 0.0,
        "commission": commission,
        "total_cost": commission,
        "fill_rate": fill_rate,
    }


def simulate_twap(
    order_value: float,
    slices: int,
    avg_daily_value: float,
    spread_bps: float,
    volatility: float,
    commission_bps: float,
) -> pd.DataFrame:
    """Simulate a TWAP schedule."""

    if slices <= 0:
        return pd.DataFrame()
    slice_value = order_value / slices
    rows = []
    for idx in range(slices):
        impact = estimate_market_impact(slice_value, avg_daily_value, volatility)
        slippage = estimate_slippage_bps(
            slice_value, avg_daily_value, spread_bps, slice_value / avg_daily_value
        )
        total = slippage + impact + commission_bps
        rows.append(
            {
                "slice": idx + 1,
                "order_value": slice_value,
                "slippage_bps": slippage,
                "market_impact_bps": impact,
                "commission_bps": commission_bps,
                "total_cost_bps": total,
            }
        )
    return pd.DataFrame(rows)


def simulate_vwap(
    order_value: float,
    volume_profile: pd.DataFrame,
    spread_bps: float,
    volatility: float,
    commission_bps: float,
) -> pd.DataFrame:
    """Simulate a VWAP schedule using a supplied volume profile."""

    profile = volume_profile.copy()
    if profile.empty:
        return pd.DataFrame()
    weight_col = "volume_share" if "volume_share" in profile.columns else "weight"
    weights = pd.to_numeric(
        profile.get(weight_col, 1 / len(profile)), errors="coerce"
    ).fillna(0)
    weights = weights / weights.sum()
    profile["order_value"] = order_value * weights
    adv_proxy = max(order_value / 0.1, order_value)
    profile["slippage_bps"] = profile["order_value"].apply(
        lambda value: estimate_slippage_bps(
            value, adv_proxy, spread_bps, value / adv_proxy
        )
    )
    profile["market_impact_bps"] = profile["order_value"].apply(
        lambda value: estimate_market_impact(value, adv_proxy, volatility)
    )
    profile["commission_bps"] = commission_bps
    profile["total_cost_bps"] = (
        profile["slippage_bps"]
        + profile["market_impact_bps"]
        + profile["commission_bps"]
    )
    return profile.reset_index(drop=True)


def compare_execution_styles(
    order_value: float,
    avg_daily_value: float,
    spread_bps: float,
    volatility: float,
    commission_bps: float,
    fill_probability: float = 0.6,
) -> pd.DataFrame:
    """Compare market, limit, TWAP, and VWAP execution styles."""

    market_slippage = estimate_slippage_bps(
        order_value, avg_daily_value, spread_bps, order_value / avg_daily_value
    )
    market_impact = estimate_market_impact(order_value, avg_daily_value, volatility)
    twap = simulate_twap(
        order_value, 5, avg_daily_value, spread_bps, volatility, commission_bps
    )
    vwap_profile = pd.DataFrame({"volume_share": [0.15, 0.20, 0.30, 0.20, 0.15]})
    vwap = simulate_vwap(
        order_value, vwap_profile, spread_bps, volatility, commission_bps
    )
    rows = [
        {
            "execution_style": "market",
            "avg_slippage_bps": market_slippage,
            "commission_bps": commission_bps,
            "market_impact_bps": market_impact,
            "total_cost_bps": market_slippage + market_impact + commission_bps,
            "fill_rate": 1.0,
            "execution_risk": "low fill risk, higher immediacy cost",
        },
        {
            "execution_style": "limit",
            "avg_slippage_bps": 0.0,
            "commission_bps": commission_bps,
            "market_impact_bps": 0.0,
            "total_cost_bps": commission_bps,
            "fill_rate": float(np.clip(fill_probability, 0, 1)),
            "execution_risk": "fill uncertainty",
        },
        {
            "execution_style": "twap",
            "avg_slippage_bps": (
                float(twap["slippage_bps"].mean()) if not twap.empty else np.nan
            ),
            "commission_bps": commission_bps,
            "market_impact_bps": (
                float(twap["market_impact_bps"].mean()) if not twap.empty else np.nan
            ),
            "total_cost_bps": (
                float(twap["total_cost_bps"].mean()) if not twap.empty else np.nan
            ),
            "fill_rate": 1.0,
            "execution_risk": "schedule risk",
        },
        {
            "execution_style": "vwap",
            "avg_slippage_bps": (
                float(vwap["slippage_bps"].mean()) if not vwap.empty else np.nan
            ),
            "commission_bps": commission_bps,
            "market_impact_bps": (
                float(vwap["market_impact_bps"].mean()) if not vwap.empty else np.nan
            ),
            "total_cost_bps": (
                float(vwap["total_cost_bps"].mean()) if not vwap.empty else np.nan
            ),
            "fill_rate": 1.0,
            "execution_risk": "volume profile risk",
        },
    ]
    return pd.DataFrame(rows)


def explain_execution_assumptions() -> pd.DataFrame:
    """Return execution model assumptions used by the simulator."""

    return pd.DataFrame(
        [
            {
                "assumption": "spread_crossing",
                "description": "Market orders pay approximately half-spread before impact.",
            },
            {
                "assumption": "market_impact",
                "description": "Impact uses a square-root participation proxy scaled by volatility.",
            },
            {
                "assumption": "limit_fill_rate",
                "description": "Limit order fill rate is an input assumption, not an execution guarantee.",
            },
            {
                "assumption": "twap_vwap",
                "description": "Schedules are simplified cost diagnostics and do not model full intraday order book dynamics.",
            },
        ]
    )
