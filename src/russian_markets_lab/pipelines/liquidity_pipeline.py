"""Liquidity research pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.liquidity import (
    calculate_liquidity_score,
    calculate_spread_bps,
)
from russian_markets_lab.data.io import write_processed_dataset


def build_liquidity_snapshot(
    universe: pd.DataFrame,
    marketdata: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build liquidity radar dataset from universe and optional marketdata."""

    if universe.empty:
        liquidity = pd.DataFrame(columns=["ticker", "liquidity_score"])
    else:
        liquidity = universe.copy()
        if (
            marketdata is not None
            and not marketdata.empty
            and "secid" in marketdata.columns
        ):
            md = marketdata.rename(columns={"secid": "ticker"})
            extra_cols = [
                col
                for col in ["ticker", "bid", "offer", "spread_bps", "num_trades"]
                if col in md.columns
            ]
            liquidity = liquidity.merge(md[extra_cols], on="ticker", how="left")
        if "avg_daily_value" not in liquidity.columns and "avg_value" in liquidity:
            liquidity["avg_daily_value"] = pd.to_numeric(
                liquidity["avg_value"], errors="coerce"
            )
        if {"bid", "offer"}.issubset(liquidity.columns):
            liquidity["quoted_spread_bps"] = [
                calculate_spread_bps(bid, offer)
                for bid, offer in zip(
                    liquidity["bid"], liquidity["offer"], strict=False
                )
            ]
            quoted = pd.to_numeric(
                liquidity["quoted_spread_bps"], errors="coerce"
            ).notna()
            liquidity.loc[quoted, "spread_bps"] = liquidity.loc[
                quoted, "quoted_spread_bps"
            ]
            liquidity["spread_source"] = np.where(quoted, "quoted", "unavailable")
        elif "spread_bps" in liquidity.columns:
            liquidity["spread_source"] = np.where(
                pd.to_numeric(liquidity["spread_bps"], errors="coerce").notna(),
                "reported",
                "unavailable",
            )
        else:
            liquidity["spread_source"] = "unavailable"
        liquidity["turnover"] = pd.to_numeric(
            liquidity.get("avg_daily_value", liquidity.get("avg_value", np.nan)),
            errors="coerce",
        )
        liquidity = calculate_liquidity_score(liquidity)
    write_processed_dataset(
        liquidity,
        "liquidity_radar",
        source="Processed from MOEX ISS market universe and marketdata",
        endpoints=["TQBR marketdata", "TQBR candles"],
        limitations=[
            "Liquidity score is a first-pass diagnostic, not a perfect liquidity metric.",
            "Quoted spreads are used only when bid/offer fields are available; otherwise spread is reported as unavailable.",
            "Liquidity regimes are relative to the current processed dataset.",
            "Public ISS data may omit full order book depth and broker-specific costs.",
        ],
    )
    return liquidity
