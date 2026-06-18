"""MOEX options data helpers."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from russian_markets_lab.moex_client.iss_client import MOEXISSClient


def _parse_option_fields(row: pd.Series) -> pd.Series:
    secid = str(row.get("secid", ""))
    shortname = str(row.get("shortname", ""))
    text = f"{secid} {shortname}".upper()

    option_type = np.nan
    if re.search(r"\bC\b|CALL|CE", text):
        option_type = "call"
    elif re.search(r"\bP\b|PUT|PE", text):
        option_type = "put"

    strike = np.nan
    strike_match = re.search(r"(?<!\d)(\d{3,7})(?:\D|$)", text)
    if strike_match:
        strike = float(strike_match.group(1))

    underlying = row.get("assetcode", np.nan)
    if pd.isna(underlying):
        prefix = re.match(r"([A-Z]{2,6})", secid)
        underlying = prefix.group(1) if prefix else np.nan

    expiration = row.get("lasttradedate", row.get("expiration", np.nan))
    return pd.Series(
        {
            "option_type": option_type,
            "strike": strike,
            "underlying": underlying,
            "expiration": expiration,
        }
    )


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if out.empty:
        return out
    parsed = out.apply(_parse_option_fields, axis=1)
    for col in parsed.columns:
        if col not in out.columns:
            out[col] = parsed[col]
        else:
            out[col] = out[col].fillna(parsed[col])
    if "openinterest" in out.columns and "open_interest" not in out.columns:
        out["open_interest"] = out["openinterest"]
    return out


def get_options_contracts(client: MOEXISSClient) -> pd.DataFrame:
    """Load MOEX options contracts."""

    path = "/engines/futures/markets/options/securities.json"
    return _normalize(client.get_all_pages(path, "securities"))


def get_options_marketdata(client: MOEXISSClient) -> pd.DataFrame:
    """Load public MOEX options market data."""

    path = "/engines/futures/markets/options/securities.json"
    return _normalize(client.get_all_pages(path, "marketdata"))


def get_option_chain(
    client: MOEXISSClient,
    underlying: str | None = None,
    expiry: str | None = None,
) -> pd.DataFrame:
    """Load an options chain and optionally filter by underlying and expiry."""

    contracts = get_options_contracts(client)
    marketdata = get_options_marketdata(client)
    if (
        not marketdata.empty
        and "secid" in contracts.columns
        and "secid" in marketdata.columns
    ):
        chain = contracts.merge(
            marketdata,
            on="secid",
            how="left",
            suffixes=("", "_marketdata"),
        )
    else:
        chain = contracts
    chain = _normalize(chain)
    if underlying and "underlying" in chain.columns:
        chain = chain[chain["underlying"].astype(str).str.upper() == underlying.upper()]
    if expiry and "expiration" in chain.columns:
        chain = chain[chain["expiration"].astype(str) == str(expiry)]
    return chain.reset_index(drop=True)
