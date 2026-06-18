"""Current market data accessors."""

from __future__ import annotations

import numpy as np
import pandas as pd

from russian_markets_lab.moex_client.iss_client import MOEXISSClient


def get_current_marketdata(
    client: MOEXISSClient,
    secid: str,
    engine: str = "stock",
    market: str = "shares",
    board: str = "TQBR",
) -> pd.DataFrame:
    """Load current public market data for one security."""

    path = f"/engines/{engine}/markets/{market}/boards/{board}/securities/{secid}.json"
    df = client.get_table(path, "marketdata")
    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    for col in [
        "bid",
        "offer",
        "last",
        "volume",
        "value",
        "open",
        "high",
        "low",
        "close",
    ]:
        if col not in out.columns:
            out[col] = np.nan
    if "spread" not in out.columns:
        out["spread"] = out["offer"] - out["bid"]
    if "numtrades" in out.columns and "num_trades" not in out.columns:
        out["num_trades"] = out["numtrades"]
    elif "num_trades" not in out.columns:
        out["num_trades"] = np.nan
    if "secid" not in out.columns:
        out["secid"] = secid
    return out
