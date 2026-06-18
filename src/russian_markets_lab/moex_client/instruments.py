"""Instrument metadata loaders from MOEX ISS."""

from __future__ import annotations

import pandas as pd

from russian_markets_lab.moex_client.iss_client import MOEXISSClient


def _lower_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    return out


def _normalize_instruments(df: pd.DataFrame) -> pd.DataFrame:
    out = _lower_columns(df)
    rename = {
        "secid": "secid",
        "shortname": "shortname",
        "name": "name",
        "market": "market",
        "primary_boardid": "board",
        "boardid": "board",
        "is_traded": "is_traded",
        "lotsize": "lot_size",
        "faceunit": "currency",
        "currencyid": "currency",
    }
    for source, target in rename.items():
        if source in out.columns and target not in out.columns:
            out[target] = out[source]
    return out


def get_all_securities(client: MOEXISSClient) -> pd.DataFrame:
    """Load all securities known to MOEX ISS."""

    df = client.get_all_pages("/securities.json", "securities")
    return _normalize_instruments(df)


def get_boards(client: MOEXISSClient, engine: str, market: str) -> pd.DataFrame:
    """Load boards for a MOEX engine and market."""

    path = f"/engines/{engine}/markets/{market}/boards.json"
    return _lower_columns(client.get_table(path, "boards"))


def get_board_securities(
    client: MOEXISSClient,
    engine: str,
    market: str,
    board: str,
) -> pd.DataFrame:
    """Load securities listed on one board."""

    path = f"/engines/{engine}/markets/{market}/boards/{board}/securities.json"
    return _normalize_instruments(client.get_all_pages(path, "securities"))


def get_stock_shares(client: MOEXISSClient, board: str = "TQBR") -> pd.DataFrame:
    """Load stock shares from the default main board."""

    return get_board_securities(client, "stock", "shares", board)


def get_bonds(client: MOEXISSClient, board: str = "TQCB") -> pd.DataFrame:
    """Load bonds from the default corporate bond board."""

    return get_board_securities(client, "stock", "bonds", board)
