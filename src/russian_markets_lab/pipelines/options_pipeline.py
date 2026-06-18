"""Options surface feature pipeline."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.options_greeks import (
    delta,
    gamma,
    implied_volatility,
    theta,
    vega,
)
from russian_markets_lab.data.cache import cache_raw_table, load_latest_raw_table
from russian_markets_lab.data.io import write_processed_dataset
from russian_markets_lab.moex_client import MOEXISSClient, MOEXISSClientError

OPTIONS_ENDPOINT = "/engines/futures/markets/options/securities.json"
OPTIONS_COLUMNS = [
    "secid",
    "shortname",
    "option_type",
    "strike",
    "expiration",
    "underlying",
    "last",
    "settleprice",
    "market_price",
    "volume",
    "open_interest",
    "spot",
    "moneyness",
    "time_to_expiry",
    "implied_volatility",
    "delta",
    "gamma",
    "vega",
    "theta",
]


def _load_options_tables(
    client: MOEXISSClient, use_cache: bool
) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        securities = client.get_all_pages(OPTIONS_ENDPOINT, "securities")
        marketdata = client.get_all_pages(OPTIONS_ENDPOINT, "marketdata")
        if use_cache:
            if not securities.empty:
                cache_raw_table(
                    securities, "forts_options_securities", "MOEX ISS", OPTIONS_ENDPOINT
                )
            if not marketdata.empty:
                cache_raw_table(
                    marketdata, "forts_options_marketdata", "MOEX ISS", OPTIONS_ENDPOINT
                )
    except MOEXISSClientError:
        securities = (
            load_latest_raw_table("forts_options_securities")
            if use_cache
            else pd.DataFrame()
        )
        marketdata = (
            load_latest_raw_table("forts_options_marketdata")
            if use_cache
            else pd.DataFrame()
        )
    for frame in [securities, marketdata]:
        if not frame.empty:
            frame.columns = [str(col).lower() for col in frame.columns]
    return securities, marketdata


def _option_price(row: pd.Series) -> float:
    for col in ["settleprice", "last", "prevsettleprice"]:
        value = pd.to_numeric(row.get(col, np.nan), errors="coerce")
        if pd.notna(value) and value > 0:
            return float(value)
    return float("nan")


def _numeric_column(
    df: pd.DataFrame, column: str, default: float = np.nan
) -> pd.Series:
    """Return a numeric Series even when the source column is missing."""

    if column in df.columns:
        return pd.to_numeric(df[column], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def build_options_features(
    options_securities: pd.DataFrame,
    options_marketdata: pd.DataFrame,
    risk_free_rate: float = 0.15,
    max_contracts: int = 200,
) -> pd.DataFrame:
    """Build option chain features, IV and Greeks where inputs are valid."""

    if options_securities.empty:
        return pd.DataFrame(columns=OPTIONS_COLUMNS)
    securities = options_securities.copy()
    marketdata = options_marketdata.copy()
    options = (
        securities.merge(
            marketdata, on="secid", how="left", suffixes=("", "_marketdata")
        )
        if not marketdata.empty
        else securities
    )
    options["option_type"] = options.get("optiontype", "").map(
        {"C": "call", "P": "put"}
    )
    options["strike"] = pd.to_numeric(options.get("strike"), errors="coerce")
    options["expiration"] = pd.to_datetime(
        options.get("lasttradedate"), errors="coerce"
    )
    options["underlying"] = options.get("underlyingasset", options.get("assetcode"))
    options["spot"] = _numeric_column(options, "underlyingsettleprice")
    options["last"] = _numeric_column(options, "last")
    options["settleprice"] = _numeric_column(options, "settleprice")
    options["volume"] = _numeric_column(options, "voltoday", default=0).fillna(0)
    open_interest = _numeric_column(options, "openposition")
    if open_interest.isna().all():
        open_interest = _numeric_column(options, "prevopenposition", default=0)
    options["open_interest"] = open_interest.fillna(0)
    options["market_price"] = options.apply(_option_price, axis=1)
    today = pd.Timestamp(date.today())
    options["time_to_expiry"] = (options["expiration"] - today).dt.days / 365
    options["moneyness"] = options["strike"] / options["spot"]
    options = options[
        options["option_type"].isin(["call", "put"])
        & (options["strike"] > 0)
        & (options["spot"] > 0)
        & (options["market_price"] > 0)
        & (options["time_to_expiry"] > 0)
        & ((options["volume"] > 0) | (options["open_interest"] > 0))
    ].copy()
    if options.empty:
        return pd.DataFrame(columns=OPTIONS_COLUMNS)
    options["activity_score"] = options["volume"] + options["open_interest"]
    options = options.sort_values("activity_score", ascending=False).head(max_contracts)
    ivs: list[float] = []
    deltas: list[float] = []
    gammas: list[float] = []
    vegas: list[float] = []
    thetas: list[float] = []
    for _, row in options.iterrows():
        iv = implied_volatility(
            float(row["market_price"]),
            float(row["spot"]),
            float(row["strike"]),
            float(row["time_to_expiry"]),
            risk_free_rate,
            str(row["option_type"]),
        )
        ivs.append(iv)
        deltas.append(
            delta(
                row["spot"],
                row["strike"],
                row["time_to_expiry"],
                risk_free_rate,
                iv,
                row["option_type"],
            )
        )
        gammas.append(
            gamma(row["spot"], row["strike"], row["time_to_expiry"], risk_free_rate, iv)
        )
        vegas.append(
            vega(row["spot"], row["strike"], row["time_to_expiry"], risk_free_rate, iv)
        )
        thetas.append(
            theta(
                row["spot"],
                row["strike"],
                row["time_to_expiry"],
                risk_free_rate,
                iv,
                row["option_type"],
            )
        )
    options["implied_volatility"] = ivs
    options["delta"] = deltas
    options["gamma"] = gammas
    options["vega"] = vegas
    options["theta"] = thetas
    return options[OPTIONS_COLUMNS].reset_index(drop=True)


def build_options_snapshot(
    client: MOEXISSClient,
    max_contracts: int = 200,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Build options surface feature snapshot and write processed output."""

    securities, marketdata = _load_options_tables(client, use_cache=use_cache)
    options = build_options_features(
        securities, marketdata, max_contracts=max_contracts
    )
    write_processed_dataset(
        options,
        "options_chain_features",
        source="MOEX ISS public/delayed data",
        endpoints=[OPTIONS_ENDPOINT],
        parameters={"max_contracts": max_contracts},
        limitations=[
            "Black-Scholes assumptions are simplified for Russian rates, dividends and liquidity.",
            "Implied volatility is NaN where inputs are invalid or solver fails.",
        ],
    )
    return options
