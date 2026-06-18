"""Liquidity research pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.liquidity import calculate_liquidity_score
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
                for col in ["ticker", "spread_bps", "num_trades"]
                if col in md.columns
            ]
            liquidity = liquidity.merge(md[extra_cols], on="ticker", how="left")
        liquidity["turnover"] = pd.to_numeric(
            liquidity.get("avg_value", np.nan), errors="coerce"
        )
        liquidity = calculate_liquidity_score(liquidity)
    write_processed_dataset(
        liquidity,
        "liquidity_radar",
        source="Processed from MOEX ISS market universe and marketdata",
        endpoints=["TQBR marketdata", "TQBR candles"],
        limitations=[
            "Liquidity score is a first-pass diagnostic, not a perfect liquidity metric.",
            "Public ISS data may omit full order book depth and broker-specific costs.",
        ],
    )
    return liquidity
