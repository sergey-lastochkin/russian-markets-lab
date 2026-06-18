"""Best-effort public order book helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.moex_client.iss_client import MOEXISSClient, MOEXISSClientError


def get_orderbook(
    client: MOEXISSClient,
    secid: str,
    engine: str = "stock",
    market: str = "shares",
    board: str = "TQBR",
) -> pd.DataFrame:
    """Return public order book data when available.

    Full depth is generally not available through delayed public MOEX ISS endpoints.
    In that case this function returns an empty DataFrame.
    """

    path = (
        f"/engines/{engine}/markets/{market}/boards/{board}/"
        f"securities/{secid}/orderbook.json"
    )
    try:
        out = client.get_table(path, "orderbook")
    except MOEXISSClientError:
        return pd.DataFrame()
    out.columns = [str(col).lower() for col in out.columns]
    return out


def calculate_orderbook_imbalance(orderbook: pd.DataFrame) -> float:
    """Calculate top-level bid/ask imbalance from an order book."""

    if orderbook.empty:
        return float("nan")
    lower = orderbook.copy()
    lower.columns = [str(col).lower() for col in lower.columns]
    if {"bid_quantity", "ask_quantity"}.issubset(lower.columns):
        bid_size = lower["bid_quantity"].sum()
        ask_size = lower["ask_quantity"].sum()
    elif {"buysell", "quantity"}.issubset(lower.columns):
        side = lower["buysell"].astype(str).str.upper()
        bid_size = lower.loc[side.isin(["B", "BUY", "BID"]), "quantity"].sum()
        ask_size = lower.loc[side.isin(["S", "SELL", "ASK"]), "quantity"].sum()
    else:
        return float("nan")
    total = bid_size + ask_size
    if total <= 0 or not np.isfinite(total):
        return float("nan")
    return float((bid_size - ask_size) / total)
