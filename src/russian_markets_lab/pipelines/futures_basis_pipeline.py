"""Futures basis monitoring pipeline."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from russian_markets_lab.analytics.futures_basis import (
    annualized_basis,
    calculate_basis,
    calculate_basis_pct,
    classify_basis_confidence,
    classify_basis_signal,
)
from russian_markets_lab.data.cache import cache_raw_table, load_latest_raw_table
from russian_markets_lab.data.io import write_processed_dataset
from russian_markets_lab.moex_client import MOEXISSClient, MOEXISSClientError

FUTURES_ENDPOINT = "/engines/futures/markets/forts/securities.json"
FUTURES_BASIS_COLUMNS = [
    "underlying",
    "spot_secid",
    "futures_secid",
    "spot_price",
    "futures_price",
    "expiry",
    "days_to_expiry",
    "basis",
    "basis_pct",
    "annualized_basis",
    "volume",
    "open_interest",
    "liquidity_filter",
    "confidence",
    "signal",
]


def _load_futures_tables(
    client: MOEXISSClient, use_cache: bool
) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        securities = client.get_all_pages(FUTURES_ENDPOINT, "securities")
        marketdata = client.get_all_pages(FUTURES_ENDPOINT, "marketdata")
        if use_cache:
            if not securities.empty:
                cache_raw_table(
                    securities, "forts_futures_securities", "MOEX ISS", FUTURES_ENDPOINT
                )
            if not marketdata.empty:
                cache_raw_table(
                    marketdata, "forts_futures_marketdata", "MOEX ISS", FUTURES_ENDPOINT
                )
    except MOEXISSClientError:
        securities = (
            load_latest_raw_table("forts_futures_securities")
            if use_cache
            else pd.DataFrame()
        )
        marketdata = (
            load_latest_raw_table("forts_futures_marketdata")
            if use_cache
            else pd.DataFrame()
        )
    for frame in [securities, marketdata]:
        if not frame.empty:
            frame.columns = [str(col).lower() for col in frame.columns]
    return securities, marketdata


def build_futures_basis_table(
    spot_universe: pd.DataFrame,
    futures_securities: pd.DataFrame,
    futures_marketdata: pd.DataFrame,
) -> pd.DataFrame:
    """Build spot-vs-futures basis table where underlying mapping is possible."""

    if spot_universe.empty or futures_securities.empty or futures_marketdata.empty:
        return pd.DataFrame(columns=FUTURES_BASIS_COLUMNS)
    spot = spot_universe.copy()
    spot_id_col = "ticker" if "ticker" in spot.columns else "secid"
    futures = futures_securities.merge(
        futures_marketdata,
        on="secid",
        how="left",
        suffixes=("", "_marketdata"),
    )
    futures = futures[
        futures["assetcode"].astype(str).isin(set(spot[spot_id_col].astype(str)))
    ].copy()
    if futures.empty:
        return pd.DataFrame(columns=FUTURES_BASIS_COLUMNS)
    futures["expiry"] = pd.to_datetime(futures.get("lasttradedate"), errors="coerce")
    futures["volume"] = pd.to_numeric(futures.get("voltoday"), errors="coerce").fillna(
        0
    )
    futures["open_interest"] = pd.to_numeric(
        futures.get("openposition", futures.get("prevopenposition")),
        errors="coerce",
    ).fillna(0)
    futures["lot_volume"] = (
        pd.to_numeric(futures.get("lotvolume", 1), errors="coerce")
        .replace(0, np.nan)
        .fillna(1)
    )
    futures["raw_futures_price"] = pd.to_numeric(
        futures.get("settleprice", futures.get("last")), errors="coerce"
    )
    if "last" in futures.columns:
        missing = futures["raw_futures_price"].isna() | (
            futures["raw_futures_price"] <= 0
        )
        futures.loc[missing, "raw_futures_price"] = pd.to_numeric(
            futures.loc[missing, "last"], errors="coerce"
        )
    today = pd.Timestamp(date.today())
    futures["days_to_expiry"] = (futures["expiry"] - today).dt.days
    futures = futures[
        (futures["days_to_expiry"] > 0) & (futures["raw_futures_price"] > 0)
    ]
    rows: list[dict[str, object]] = []
    for underlying, group in futures.sort_values(
        ["expiry", "volume"], ascending=[True, False]
    ).groupby("assetcode"):
        spot_row = spot[spot[spot_id_col].astype(str) == str(underlying)]
        if spot_row.empty:
            continue
        spot_price = float(
            pd.to_numeric(spot_row.iloc[0].get("last_close", np.nan), errors="coerce")
        )
        if not np.isfinite(spot_price) or spot_price <= 0:
            continue
        contract = group.iloc[0]
        futures_price = float(contract["raw_futures_price"]) / float(
            contract["lot_volume"]
        )
        annualized = annualized_basis(
            spot_price, futures_price, int(contract["days_to_expiry"])
        )
        confidence = classify_basis_confidence(
            spot_price,
            futures_price,
            int(contract["days_to_expiry"]),
            float(contract["volume"]),
            float(contract["open_interest"]),
        )
        liquid = confidence in {"high", "medium"}
        rows.append(
            {
                "underlying": underlying,
                "spot_secid": underlying,
                "futures_secid": contract["secid"],
                "spot_price": spot_price,
                "futures_price": futures_price,
                "expiry": contract["expiry"].date().isoformat(),
                "days_to_expiry": int(contract["days_to_expiry"]),
                "basis": calculate_basis(spot_price, futures_price),
                "basis_pct": calculate_basis_pct(spot_price, futures_price),
                "annualized_basis": annualized,
                "volume": float(contract["volume"]),
                "open_interest": float(contract["open_interest"]),
                "liquidity_filter": liquid,
                "confidence": confidence,
                "signal": classify_basis_signal(annualized) if liquid else "unknown",
            }
        )
    if not rows:
        return pd.DataFrame(columns=FUTURES_BASIS_COLUMNS)
    return pd.DataFrame(rows, columns=FUTURES_BASIS_COLUMNS).sort_values(
        "volume", ascending=False
    )


def build_futures_basis_snapshot(
    client: MOEXISSClient,
    universe: pd.DataFrame,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Build futures basis snapshot and write processed output."""

    futures_securities, futures_marketdata = _load_futures_tables(
        client, use_cache=use_cache
    )
    basis = build_futures_basis_table(universe, futures_securities, futures_marketdata)
    write_processed_dataset(
        basis,
        "futures_basis",
        source="MOEX ISS public/delayed data",
        endpoints=[FUTURES_ENDPOINT, "TQBR universe spot prices"],
        limitations=[
            "Basis is computed only where FORTS ASSETCODE maps to a TQBR spot ticker.",
            "Futures prices are normalized by LOTVOLUME when available.",
            "This is a rich/fair/cheap diagnostic, not an arbitrage signal.",
        ],
    )
    return basis
