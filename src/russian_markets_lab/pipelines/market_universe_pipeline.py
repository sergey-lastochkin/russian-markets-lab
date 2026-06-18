"""Market universe data ingestion and processing pipeline."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.market_universe import (
    build_market_universe,
    rank_market_universe,
)
from russian_markets_lab.data.cache import cache_raw_table, load_latest_raw_table
from russian_markets_lab.data.io import write_processed_dataset
from russian_markets_lab.moex_client import MOEXISSClient, MOEXISSClientError
from russian_markets_lab.moex_client.candles import get_candles
from russian_markets_lab.moex_client.instruments import get_stock_shares

TQBR_SECURITIES_ENDPOINT = "/engines/stock/markets/shares/boards/TQBR/securities.json"


def load_tqbr_marketdata(client: MOEXISSClient, use_cache: bool = True) -> pd.DataFrame:
    """Load and normalize TQBR current market data."""

    try:
        marketdata = client.get_all_pages(TQBR_SECURITIES_ENDPOINT, "marketdata")
        if not marketdata.empty and use_cache:
            cache_raw_table(
                marketdata, "tqbr_marketdata", "MOEX ISS", TQBR_SECURITIES_ENDPOINT
            )
    except MOEXISSClientError:
        marketdata = (
            load_latest_raw_table("tqbr_marketdata") if use_cache else pd.DataFrame()
        )
    if marketdata.empty:
        return marketdata
    out = marketdata.copy()
    out.columns = [str(col).lower() for col in out.columns]
    if "value" in out.columns:
        out["trade_value"] = out["value"]
    if "valtoday" in out.columns:
        out["value"] = out["valtoday"]
    if "voltoday" in out.columns:
        out["volume"] = out["voltoday"]
    if "numtrades" in out.columns:
        out["num_trades"] = out["numtrades"]
    if "offer" in out.columns:
        out["ask"] = out["offer"]
    if {"bid", "ask"}.issubset(out.columns):
        bid = pd.to_numeric(out["bid"], errors="coerce")
        ask = pd.to_numeric(out["ask"], errors="coerce")
        midpoint = (bid + ask) / 2
        out["spread_bps"] = (ask - bid) / midpoint * 10_000
    return out


def load_tqbr_instruments(
    client: MOEXISSClient, use_cache: bool = True
) -> pd.DataFrame:
    """Load and normalize TQBR instruments."""

    try:
        securities = get_stock_shares(client)
        if not securities.empty and use_cache:
            cache_raw_table(
                securities, "tqbr_instruments", "MOEX ISS", TQBR_SECURITIES_ENDPOINT
            )
    except MOEXISSClientError:
        securities = (
            load_latest_raw_table("tqbr_instruments") if use_cache else pd.DataFrame()
        )
    if not securities.empty:
        securities = securities.copy()
        securities.columns = [str(col).lower() for col in securities.columns]
        securities["market"] = "shares"
        if "board" not in securities.columns:
            securities["board"] = "TQBR"
        securities["board"] = securities["board"].fillna("TQBR")
    return securities


def select_top_liquid_tickers(marketdata: pd.DataFrame, limit: int = 30) -> list[str]:
    """Select top tickers by current daily traded value."""

    if marketdata.empty or "secid" not in marketdata.columns:
        return []
    out = marketdata.copy()
    value = pd.to_numeric(out.get("value", 0), errors="coerce").fillna(0)
    out = out.assign(_value=value).sort_values("_value", ascending=False)
    return out["secid"].dropna().astype(str).head(limit).tolist()


def load_candles_for_tickers(
    client: MOEXISSClient,
    tickers: list[str],
    lookback_days: int = 365,
    use_cache: bool = True,
) -> dict[str, pd.DataFrame]:
    """Load daily candles for selected tickers, falling back to raw cache if allowed."""

    from_date = (date.today() - timedelta(days=lookback_days)).isoformat()
    candles_by_ticker: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        cache_name = f"candles_{ticker.lower()}"
        endpoint = f"/engines/stock/markets/shares/boards/TQBR/securities/{ticker}/candles.json"
        try:
            candles = get_candles(client, ticker, from_date=from_date)
            if not candles.empty and use_cache:
                cache_raw_table(
                    candles, cache_name, "MOEX ISS", endpoint, {"from": from_date}
                )
        except MOEXISSClientError:
            candles = load_latest_raw_table(cache_name) if use_cache else pd.DataFrame()
        if not candles.empty:
            candles_by_ticker[ticker] = candles
    return candles_by_ticker


def fallback_universe_from_marketdata(
    securities: pd.DataFrame,
    marketdata: pd.DataFrame,
) -> pd.DataFrame:
    """Build a transparent one-observation universe from real current marketdata."""

    columns = [
        "ticker",
        "name",
        "board",
        "market",
        "avg_volume",
        "avg_value",
        "avg_daily_value",
        "median_value",
        "median_daily_value",
        "realized_volatility",
        "num_observations",
        "last_close",
        "tradable_flag",
    ]
    if marketdata.empty:
        return pd.DataFrame(columns=columns)
    sec = securities.copy()
    md = marketdata.copy()
    if not sec.empty and "secid" in sec.columns:
        md = md.merge(sec[["secid", "shortname"]], on="secid", how="left")
    value = pd.to_numeric(md.get("value", np.nan), errors="coerce")
    return pd.DataFrame(
        {
            "ticker": md["secid"],
            "name": md.get("shortname", md["secid"]),
            "board": "TQBR",
            "market": "shares",
            "avg_volume": pd.to_numeric(md.get("volume", np.nan), errors="coerce"),
            "avg_value": value,
            "avg_daily_value": value,
            "median_value": value,
            "median_daily_value": value,
            "realized_volatility": np.nan,
            "num_observations": 1,
            "last_close": pd.to_numeric(md.get("last", np.nan), errors="coerce"),
            "tradable_flag": False,
        }
    )


def build_market_universe_components(
    client: MOEXISSClient,
    tickers_limit: int = 30,
    lookback_days: int = 365,
    use_cache: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    """Build universe plus source marketdata and candles for downstream pipelines."""

    securities = load_tqbr_instruments(client, use_cache=use_cache)
    marketdata = load_tqbr_marketdata(client, use_cache=use_cache)
    tickers = select_top_liquid_tickers(marketdata, limit=tickers_limit)
    candles_by_ticker = load_candles_for_tickers(
        client, tickers, lookback_days=lookback_days, use_cache=use_cache
    )
    if candles_by_ticker:
        universe = rank_market_universe(
            build_market_universe(securities, candles_by_ticker)
        )
    else:
        universe = rank_market_universe(
            fallback_universe_from_marketdata(securities, marketdata)
        )
    return universe, marketdata, candles_by_ticker


def build_market_universe_snapshot(
    client: MOEXISSClient,
    tickers_limit: int = 30,
    lookback_days: int = 365,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Load TQBR data, build ranked market universe and write processed output."""

    universe, _, _ = build_market_universe_components(
        client,
        tickers_limit=tickers_limit,
        lookback_days=lookback_days,
        use_cache=use_cache,
    )
    write_processed_dataset(
        universe,
        "market_universe",
        source="MOEX ISS public/delayed data",
        endpoints=[
            TQBR_SECURITIES_ENDPOINT,
            "TQBR candles endpoint per selected ticker",
        ],
        parameters={"tickers_limit": tickers_limit, "lookback_days": lookback_days},
        limitations=[
            "Universe is selected from TQBR shares by current traded value.",
            "If candles are unavailable, the fallback universe is explicitly based on current marketdata only and has tradable_flag=False.",
        ],
    )
    return universe
