"""Market universe construction and ranking."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.volatility import realized_volatility
from russian_markets_lab.config import MIN_OBSERVATIONS, TRADABLE_AVG_VALUE_THRESHOLD


def _first_available(
    row: pd.Series, names: list[str], default: object = np.nan
) -> object:
    for name in names:
        if name in row.index and pd.notna(row[name]):
            return row[name]
    return default


def build_market_universe(
    securities: pd.DataFrame,
    candles_by_ticker: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build a market universe table with liquidity and volatility diagnostics."""

    rows: list[dict[str, object]] = []
    securities_lower = securities.copy()
    securities_lower.columns = [str(col).lower() for col in securities_lower.columns]
    by_ticker = (
        securities_lower.set_index("secid", drop=False)
        if "secid" in securities_lower.columns
        else pd.DataFrame()
    )

    for ticker, candles in candles_by_ticker.items():
        c = candles.copy()
        c.columns = [str(col).lower() for col in c.columns]
        meta = (
            by_ticker.loc[ticker]
            if not by_ticker.empty and ticker in by_ticker.index
            else pd.Series(dtype=object)
        )
        value = pd.to_numeric(c.get("value", pd.Series(dtype=float)), errors="coerce")
        volume = pd.to_numeric(c.get("volume", pd.Series(dtype=float)), errors="coerce")
        close = pd.to_numeric(c.get("close", pd.Series(dtype=float)), errors="coerce")
        avg_value = float(value.mean()) if not value.empty else float("nan")
        num_observations = int(close.dropna().shape[0])
        last_close = (
            float(close.dropna().iloc[-1]) if close.dropna().shape[0] else float("nan")
        )
        vol = realized_volatility(close)
        tradable = (
            avg_value > TRADABLE_AVG_VALUE_THRESHOLD
            and num_observations >= MIN_OBSERVATIONS
            and np.isfinite(vol)
            and np.isfinite(last_close)
        )
        rows.append(
            {
                "ticker": ticker,
                "name": _first_available(meta, ["name", "shortname"], ticker),
                "board": _first_available(
                    meta, ["board", "boardid", "primary_boardid"]
                ),
                "market": _first_available(meta, ["market"]),
                "avg_volume": (
                    float(volume.mean()) if not volume.empty else float("nan")
                ),
                "avg_value": avg_value,
                "avg_daily_value": avg_value,
                "median_value": (
                    float(value.median()) if not value.empty else float("nan")
                ),
                "median_daily_value": (
                    float(value.median()) if not value.empty else float("nan")
                ),
                "realized_volatility": vol,
                "num_observations": num_observations,
                "last_close": last_close,
                "tradable_flag": bool(tradable),
                "missing_close_ratio": (
                    float(close.isna().mean()) if not close.empty else 1.0
                ),
                "missing_value_ratio": (
                    float(value.isna().mean()) if not value.empty else 1.0
                ),
            }
        )
    return pd.DataFrame(rows)


def rank_market_universe(universe: pd.DataFrame) -> pd.DataFrame:
    """Add liquidity, volatility, and tradability ranks to a universe table."""

    out = universe.copy()
    if out.empty:
        return out
    out["liquidity_rank"] = out["avg_value"].rank(ascending=False, method="min")
    out["volatility_rank"] = out["realized_volatility"].rank(
        ascending=True, method="min"
    )
    liquidity_score = out["avg_value"].rank(pct=True)
    observation_score = out["num_observations"].rank(pct=True)
    volatility_score = 1 - out["realized_volatility"].rank(pct=True)
    close_quality = 1 - pd.to_numeric(
        out.get("missing_close_ratio", 1), errors="coerce"
    ).fillna(1)
    value_quality = 1 - pd.to_numeric(
        out.get("missing_value_ratio", 1), errors="coerce"
    ).fillna(1)
    observation_quality = (
        pd.to_numeric(out["num_observations"], errors="coerce").fillna(0)
        / MIN_OBSERVATIONS
    ).clip(upper=1)
    finite_volatility = pd.to_numeric(
        out["realized_volatility"], errors="coerce"
    ).apply(np.isfinite)
    out["data_quality_score"] = (
        0.35 * observation_quality
        + 0.25 * close_quality
        + 0.25 * value_quality
        + 0.15 * finite_volatility.astype(float)
    )
    out["tradability_score"] = (
        0.55 * liquidity_score.fillna(0)
        + 0.25 * observation_score.fillna(0)
        + 0.20 * volatility_score.fillna(0)
    )
    bucket_count = min(4, len(out))
    labels = ["low", "medium", "high", "very_high"][-bucket_count:]
    if bucket_count >= 2:
        out["adv_bucket"] = pd.qcut(
            pd.to_numeric(out["avg_value"], errors="coerce").rank(method="first"),
            q=bucket_count,
            labels=labels,
            duplicates="drop",
        ).astype(str)
        out["volatility_bucket"] = pd.qcut(
            pd.to_numeric(out["realized_volatility"], errors="coerce").rank(
                method="first"
            ),
            q=bucket_count,
            labels=labels,
            duplicates="drop",
        ).astype(str)
        out["liquidity_bucket"] = pd.qcut(
            out["tradability_score"].rank(method="first"),
            q=bucket_count,
            labels=labels,
            duplicates="drop",
        ).astype(str)
    else:
        out["adv_bucket"] = "unknown"
        out["volatility_bucket"] = "unknown"
        out["liquidity_bucket"] = "unknown"
    return out.sort_values("tradability_score", ascending=False).reset_index(drop=True)
