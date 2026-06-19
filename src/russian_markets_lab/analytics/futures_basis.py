"""Futures basis and carry screens."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def calculate_basis(
    spot_price: float,
    futures_price: float,
) -> float:
    """Calculate futures minus spot basis."""

    if spot_price <= 0 or futures_price <= 0:
        return float("nan")
    return float(futures_price - spot_price)


def calculate_basis_pct(
    spot_price: float,
    futures_price: float,
) -> float:
    """Calculate basis as a percentage of spot."""

    basis = calculate_basis(spot_price, futures_price)
    if not np.isfinite(basis) or spot_price <= 0:
        return float("nan")
    return float(basis / spot_price)


def annualized_basis(
    spot_price: float,
    futures_price: float,
    days_to_expiry: int,
) -> float:
    """Annualize futures basis by days to expiry."""

    basis_pct = calculate_basis_pct(spot_price, futures_price)
    if not np.isfinite(basis_pct) or days_to_expiry <= 0:
        return float("nan")
    return float(basis_pct * 365 / days_to_expiry)


def classify_basis_signal(
    annualized_basis_value: float,
    cheap_threshold: float = -0.05,
    rich_threshold: float = 0.05,
) -> str:
    """Classify a basis deviation as cheap, fair, rich, or unknown."""

    if not np.isfinite(annualized_basis_value):
        return "unknown"
    if annualized_basis_value <= cheap_threshold:
        return "cheap"
    if annualized_basis_value >= rich_threshold:
        return "rich"
    return "fair"


def classify_basis_confidence(
    spot_price: float,
    futures_price: float,
    days_to_expiry: int | float,
    volume: float | None = None,
    open_interest: float | None = None,
) -> str:
    """Classify confidence for a basis diagnostic.

    Confidence reflects data completeness and liquidity fields. It is not a
    statement about tradeability or expected performance.
    """

    spot = pd.to_numeric(pd.Series([spot_price]), errors="coerce").iloc[0]
    futures = pd.to_numeric(pd.Series([futures_price]), errors="coerce").iloc[0]
    days = pd.to_numeric(pd.Series([days_to_expiry]), errors="coerce").iloc[0]
    if (
        not np.isfinite(spot)
        or not np.isfinite(futures)
        or not np.isfinite(days)
        or spot <= 0
        or futures <= 0
        or days <= 0
    ):
        return "unknown"

    volume_value = pd.to_numeric(pd.Series([volume]), errors="coerce").iloc[0]
    open_interest_value = pd.to_numeric(
        pd.Series([open_interest]), errors="coerce"
    ).iloc[0]
    has_volume = np.isfinite(volume_value) and volume_value > 0
    has_open_interest = np.isfinite(open_interest_value) and open_interest_value > 0
    if has_volume and has_open_interest:
        return "high"
    if has_volume or has_open_interest:
        return "medium"
    return "low"


def build_futures_basis_table(
    spot_data: pd.DataFrame,
    futures_data: pd.DataFrame,
    mapping: pd.DataFrame,
) -> pd.DataFrame:
    """Build a futures basis monitor table from spot, futures, and mapping data."""

    spot = spot_data.copy()
    futures = futures_data.copy()
    mapping_df = mapping.copy()
    spot.columns = [str(col).lower() for col in spot.columns]
    futures.columns = [str(col).lower() for col in futures.columns]
    mapping_df.columns = [str(col).lower() for col in mapping_df.columns]

    rows: list[dict[str, object]] = []
    today = pd.Timestamp(date.today())
    for _, map_row in mapping_df.iterrows():
        spot_secid = map_row.get("spot_secid")
        futures_secid = map_row.get("futures_secid")
        spot_row = spot[spot["secid"] == spot_secid].tail(1)
        futures_row = futures[futures["secid"] == futures_secid].tail(1)
        if spot_row.empty or futures_row.empty:
            continue

        spot_price = float(
            spot_row.iloc[0].get("last", spot_row.iloc[0].get("close", np.nan))
        )
        futures_price = float(
            futures_row.iloc[0].get(
                "settleprice",
                futures_row.iloc[0].get(
                    "last", futures_row.iloc[0].get("close", np.nan)
                ),
            )
        )
        expiry = map_row.get("expiry", futures_row.iloc[0].get("lasttradedate", np.nan))
        expiry_ts = pd.to_datetime(expiry, errors="coerce")
        days_to_expiry = int((expiry_ts - today).days) if pd.notna(expiry_ts) else -1
        basis = calculate_basis(spot_price, futures_price)
        basis_pct = calculate_basis_pct(spot_price, futures_price)
        annualized = annualized_basis(spot_price, futures_price, days_to_expiry)
        volume = float(futures_row.iloc[0].get("volume", np.nan))
        open_interest = float(
            futures_row.iloc[0].get(
                "open_interest", futures_row.iloc[0].get("openinterest", np.nan)
            )
        )
        confidence = classify_basis_confidence(
            spot_price,
            futures_price,
            days_to_expiry,
            volume,
            open_interest,
        )
        rows.append(
            {
                "underlying": map_row.get("underlying", spot_secid),
                "spot_secid": spot_secid,
                "futures_secid": futures_secid,
                "spot_price": spot_price,
                "futures_price": futures_price,
                "expiry": expiry,
                "days_to_expiry": days_to_expiry,
                "basis": basis,
                "basis_pct": basis_pct,
                "annualized_basis": annualized,
                "volume": volume,
                "open_interest": open_interest,
                "liquidity_filter": confidence in {"high", "medium"},
                "confidence": confidence,
                "signal": (
                    classify_basis_signal(annualized)
                    if confidence in {"high", "medium"}
                    else "unknown"
                ),
            }
        )
    return pd.DataFrame(rows)
