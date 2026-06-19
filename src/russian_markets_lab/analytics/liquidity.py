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


def calculate_spread_proxy_bps(
    high: float | None = None,
    low: float | None = None,
    close: float | None = None,
    previous_close: float | None = None,
) -> float:
    """Estimate a spread proxy in bps when quoted bid/ask are unavailable.

    This is not a quoted spread. It is a fallback range/close-to-close proxy used
    only for diagnostics when public data does not include bid and ask quotes.
    """

    high_value = pd.to_numeric(pd.Series([high]), errors="coerce").iloc[0]
    low_value = pd.to_numeric(pd.Series([low]), errors="coerce").iloc[0]
    close_value = pd.to_numeric(pd.Series([close]), errors="coerce").iloc[0]
    previous_value = pd.to_numeric(pd.Series([previous_close]), errors="coerce").iloc[0]
    if np.isfinite(high_value) and np.isfinite(low_value) and high_value >= low_value:
        midpoint = (high_value + low_value) / 2
        if midpoint > 0:
            return float((high_value - low_value) / midpoint * 10_000)
    if (
        np.isfinite(close_value)
        and np.isfinite(previous_value)
        and close_value > 0
        and previous_value > 0
    ):
        return float(abs(close_value / previous_value - 1) * 10_000)
    return float("nan")


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

    spread_col = "spread_bps" if "spread_bps" in out.columns else "spread"

    components = explain_liquidity_score_components(out)

    for column in [
        "avg_value_component",
        "volume_component",
        "trade_count_component",
        "spread_component",
        "volatility_penalty",
        "data_quality_component",
        "liquidity_score",
        "liquidity_regime",
    ]:
        out[column] = components[column].to_numpy()
    if "spread_source" not in out.columns:
        out["spread_source"] = np.where(
            pd.to_numeric(out.get(spread_col, np.nan), errors="coerce").notna(),
            "quoted_or_reported",
            "unavailable",
        )
    return out.sort_values("liquidity_score", ascending=False).reset_index(drop=True)


def classify_liquidity_regime(
    liquidity_score: float,
    data_quality_score: float | None = None,
) -> str:
    """Classify relative liquidity regime from score and data quality."""

    score = pd.to_numeric(pd.Series([liquidity_score]), errors="coerce").iloc[0]
    quality = pd.to_numeric(pd.Series([data_quality_score]), errors="coerce").iloc[0]
    if not np.isfinite(score) or (np.isfinite(quality) and quality < 0.35):
        return "insufficient_data"
    if score >= 0.66:
        return "liquid"
    if score >= 0.35:
        return "watch"
    return "illiquid"


def calculate_data_quality_component(df: pd.DataFrame) -> pd.Series:
    """Estimate data quality from observations and finite core fields."""

    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    index = out.index
    observations = pd.to_numeric(
        out.get("num_observations", pd.Series(np.nan, index=index)), errors="coerce"
    )
    close = pd.to_numeric(
        out.get(
            "last_close",
            out.get("close", out.get("last", pd.Series(np.nan, index=index))),
        ),
        errors="coerce",
    )
    value_col = "avg_daily_value" if "avg_daily_value" in out.columns else "avg_value"
    value = pd.to_numeric(
        out.get(value_col, out.get("value", pd.Series(np.nan, index=index))),
        errors="coerce",
    )
    volatility = pd.to_numeric(
        out.get(
            "realized_volatility",
            out.get("volatility", pd.Series(np.nan, index=index)),
        ),
        errors="coerce",
    )
    observation_score = (observations.clip(lower=0, upper=100) / 100).fillna(0.5)
    finite_volatility = pd.Series(np.isfinite(volatility), index=index).astype(float)
    finite_score = (
        close.gt(0).astype(float) + value.gt(0).astype(float) + finite_volatility
    ) / 3
    return (0.45 * observation_score + 0.55 * finite_score).clip(0, 1)


def explain_liquidity_score_components(df: pd.DataFrame) -> pd.DataFrame:
    """Return component ranks/contributions used in the liquidity score."""

    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if out.empty:
        return pd.DataFrame()
    value_col = (
        "avg_daily_value"
        if "avg_daily_value" in out.columns
        else ("avg_value" if "avg_value" in out.columns else "value")
    )
    volume_col = "avg_volume" if "avg_volume" in out.columns else "volume"
    trades_col = "num_trades" if "num_trades" in out.columns else "trades"
    spread_col = "spread_bps" if "spread_bps" in out.columns else "spread"
    vol_col = (
        "realized_volatility" if "realized_volatility" in out.columns else "volatility"
    )
    components = pd.DataFrame(index=out.index)
    if "ticker" in out.columns:
        components["ticker"] = out["ticker"]
    elif "secid" in out.columns:
        components["secid"] = out["secid"]
    value_rank = pd.to_numeric(out.get(value_col, 0), errors="coerce").rank(pct=True)
    volume_rank = pd.to_numeric(out.get(volume_col, 0), errors="coerce").rank(pct=True)
    trades_rank = pd.to_numeric(out.get(trades_col, 0), errors="coerce").rank(pct=True)
    spread_rank = 1 - pd.to_numeric(out.get(spread_col, np.nan), errors="coerce").rank(
        pct=True
    )
    volatility_rank = 1 - pd.to_numeric(out.get(vol_col, np.nan), errors="coerce").rank(
        pct=True
    )
    data_quality = (
        pd.to_numeric(out["data_quality_score"], errors="coerce").clip(0, 1)
        if "data_quality_score" in out.columns
        else calculate_data_quality_component(out)
    )
    components["avg_value_component"] = 0.35 * value_rank.fillna(0)
    components["volume_component"] = 0.20 * volume_rank.fillna(0)
    components["trade_count_component"] = 0.15 * trades_rank.fillna(0)
    components["spread_component"] = 0.10 * spread_rank.fillna(0.5)
    components["volatility_penalty"] = 0.10 * volatility_rank.fillna(0.5)
    components["data_quality_component"] = 0.10 * data_quality.fillna(0.5)
    components["liquidity_score"] = components[
        [
            "avg_value_component",
            "volume_component",
            "trade_count_component",
            "spread_component",
            "volatility_penalty",
            "data_quality_component",
        ]
    ].sum(axis=1)
    quality_for_regime = (
        pd.to_numeric(out["data_quality_score"], errors="coerce")
        if "data_quality_score" in out.columns
        else data_quality
    )
    components["liquidity_regime"] = [
        classify_liquidity_regime(score, quality)
        for score, quality in zip(
            components["liquidity_score"], quality_for_regime, strict=False
        )
    ]
    if "liquidity_score" in out.columns:
        components["source_liquidity_score"] = pd.to_numeric(
            out["liquidity_score"], errors="coerce"
        )
    return components.reset_index(drop=True)


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
