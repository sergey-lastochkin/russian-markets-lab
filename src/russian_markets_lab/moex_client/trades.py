"""Recent trades accessors."""

from __future__ import annotations

import pandas as pd

from russian_markets_lab.moex_client.iss_client import MOEXISSClient


def get_trades(
    client: MOEXISSClient,
    secid: str,
    engine: str = "stock",
    market: str = "shares",
    board: str = "TQBR",
) -> pd.DataFrame:
    """Load recent public trades for one security."""

    path = (
        f"/engines/{engine}/markets/{market}/boards/{board}/"
        f"securities/{secid}/trades.json"
    )
    out = client.get_table(path, "trades").copy()
    out.columns = [str(col).lower() for col in out.columns]
    if "secid" not in out.columns:
        out["secid"] = secid
    if "qty" in out.columns and "quantity" not in out.columns:
        out["quantity"] = out["qty"]
    if "tradetime" in out.columns:
        out["tradetime"] = pd.to_datetime(out["tradetime"], errors="coerce")
    return out
