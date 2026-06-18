"""MOEX futures data helpers."""

from __future__ import annotations

import pandas as pd

from russian_markets_lab.moex_client.candles import get_candles
from russian_markets_lab.moex_client.iss_client import MOEXISSClient


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    rename = {"openinterest": "open_interest", "lasttradedate": "lasttradedate"}
    for source, target in rename.items():
        if source in out.columns and target not in out.columns:
            out[target] = out[source]
    return out


def get_futures_contracts(client: MOEXISSClient) -> pd.DataFrame:
    """Load MOEX futures contracts."""

    path = "/engines/futures/markets/forts/securities.json"
    return _normalize(client.get_all_pages(path, "securities"))


def get_futures_marketdata(client: MOEXISSClient) -> pd.DataFrame:
    """Load public futures market data."""

    path = "/engines/futures/markets/forts/securities.json"
    return _normalize(client.get_all_pages(path, "marketdata"))


def get_futures_candles(
    client: MOEXISSClient,
    secid: str,
    from_date: str | None = None,
    till_date: str | None = None,
    interval: int = 24,
) -> pd.DataFrame:
    """Load futures candles from the FORTS market."""

    return get_candles(
        client,
        secid=secid,
        engine="futures",
        market="forts",
        board="RFUD",
        from_date=from_date,
        till_date=till_date,
        interval=interval,
    )
