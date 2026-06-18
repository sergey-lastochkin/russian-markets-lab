"""Liquidity diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_spread(bid: float, ask: float) -> float:
    """Calculate quoted spread."""

    if bid <= 0 or ask <= 0 or ask < bid:
        return float("nan")
    return float(ask - bid)


def calculate_spread_bps(bid: float, ask: float) -> float:
    """Calculate quoted spread in basis points."""

    spread = calculate_spread(bid, ask)
    midpoint = (bid + ask) / 2
    if not np.isfinite(spread) or midpoint <= 0:
        return float("nan")
    return float(spread / midpoint * 10_000)


def calculate_turnover(value: pd.Series) -> float:
    """Calculate total turnover from traded value."""

    return float(pd.to_numeric(value, errors="coerce").fillna(0).sum())


def calculate_amihud_illiquidity(returns: pd.Series, value: pd.Series) -> float:
    """Calculate the Amihud illiquidity proxy."""

    aligned = pd.concat(
        [
            pd.to_numeric(returns, errors="coerce").abs(),
            pd.to_numeric(value, errors="coerce"),
        ],
        axis=1,
    ).dropna()
    aligned = aligned[aligned.iloc[:, 1] > 0]
    if aligned.empty:
        return float("nan")
    return float((aligned.iloc[:, 0] / aligned.iloc[:, 1]).mean())


def calculate_liquidity_score(df: pd.DataFrame) -> pd.DataFrame:
    """Build a rank-based liquidity score from market diagnostics."""

    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if out.empty:
        out["liquidity_score"] = pd.Series(dtype=float)
        return out

    value_col = "avg_value" if "avg_value" in out.columns else "value"
    volume_col = "avg_volume" if "avg_volume" in out.columns else "volume"
    trades_col = "num_trades" if "num_trades" in out.columns else "trades"
    spread_col = "spread_bps" if "spread_bps" in out.columns else "spread"
    vol_col = (
        "realized_volatility" if "realized_volatility" in out.columns else "volatility"
    )

    value_score = pd.to_numeric(out.get(value_col, 0), errors="coerce").rank(pct=True)
    volume_score = pd.to_numeric(out.get(volume_col, 0), errors="coerce").rank(pct=True)
    trades_score = pd.to_numeric(out.get(trades_col, 0), errors="coerce").rank(pct=True)
    spread_score = 1 - pd.to_numeric(out.get(spread_col, np.nan), errors="coerce").rank(
        pct=True
    )
    volatility_penalty = 1 - pd.to_numeric(
        out.get(vol_col, np.nan), errors="coerce"
    ).rank(pct=True)

    out["liquidity_score"] = (
        0.40 * value_score.fillna(0)
        + 0.25 * volume_score.fillna(0)
        + 0.15 * trades_score.fillna(0)
        + 0.10 * spread_score.fillna(0.5)
        + 0.10 * volatility_penalty.fillna(0.5)
    )
    return out.sort_values("liquidity_score", ascending=False).reset_index(drop=True)


def explain_liquidity_score_components(df: pd.DataFrame) -> pd.DataFrame:
    """Return component ranks/contributions used in the liquidity score."""

    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if out.empty:
        return pd.DataFrame()
    value_col = "avg_value" if "avg_value" in out.columns else "value"
    volume_col = "avg_volume" if "avg_volume" in out.columns else "volume"
    trades_col = "num_trades" if "num_trades" in out.columns else "trades"
    spread_col = "spread_bps" if "spread_bps" in out.columns else "spread"
    vol_col = (
        "realized_volatility" if "realized_volatility" in out.columns else "volatility"
    )
    components = pd.DataFrame(index=out.index)
    if "ticker" in out.columns:
        components["ticker"] = out["ticker"]
    components["value_rank"] = pd.to_numeric(
        out.get(value_col, 0), errors="coerce"
    ).rank(pct=True)
    components["volume_rank"] = pd.to_numeric(
        out.get(volume_col, 0), errors="coerce"
    ).rank(pct=True)
    components["trades_rank"] = pd.to_numeric(
        out.get(trades_col, 0), errors="coerce"
    ).rank(pct=True)
    components["spread_rank"] = 1 - pd.to_numeric(
        out.get(spread_col, np.nan), errors="coerce"
    ).rank(pct=True)
    components["volatility_rank"] = 1 - pd.to_numeric(
        out.get(vol_col, np.nan), errors="coerce"
    ).rank(pct=True)
    components["value_contribution"] = 0.40 * components["value_rank"].fillna(0)
    components["volume_contribution"] = 0.25 * components["volume_rank"].fillna(0)
    components["trades_contribution"] = 0.15 * components["trades_rank"].fillna(0)
    components["spread_contribution"] = 0.10 * components["spread_rank"].fillna(0.5)
    components["volatility_contribution"] = 0.10 * components["volatility_rank"].fillna(
        0.5
    )
    return components


def detect_volume_spikes(
    candles: pd.DataFrame,
    window: int = 20,
    z_threshold: float = 2.0,
) -> pd.DataFrame:
    """Detect volume spikes using rolling z-scores."""

    out = candles.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if "volume" not in out.columns:
        return pd.DataFrame()
    volume = pd.to_numeric(out["volume"], errors="coerce")
    mean = volume.rolling(window).mean()
    std = volume.rolling(window).std()
    out["volume_zscore"] = (volume - mean) / std.replace(0, np.nan)
    out["volume_spike"] = out["volume_zscore"] >= z_threshold
    return out[out["volume_spike"].fillna(False)].reset_index(drop=True)


def intraday_liquidity_pattern(
    intraday_candles: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize intraday liquidity by time of day.

    If intraday timestamps are unavailable, an empty DataFrame is returned.
    """

    out = intraday_candles.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if "begin" not in out.columns:
        return pd.DataFrame()
    out["begin"] = pd.to_datetime(out["begin"], errors="coerce")
    out = out.dropna(subset=["begin"])
    if out.empty:
        return pd.DataFrame()
    out["time"] = out["begin"].dt.time.astype(str)
    aggregations = {"volume": "mean", "value": "mean"}
    aggregations = {k: v for k, v in aggregations.items() if k in out.columns}
    if not aggregations:
        return pd.DataFrame()
    return out.groupby("time", as_index=False).agg(aggregations)
