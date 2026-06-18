"""Options chain feature engineering and volatility surface visualization."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from russian_markets_lab.analytics.options_greeks import (
    delta,
    gamma,
    implied_volatility,
    theta,
    vega,
)


def build_option_chain_features(
    options: pd.DataFrame,
    spot_prices: pd.DataFrame,
    risk_free_rate: float = 0.15,
) -> pd.DataFrame:
    """Calculate moneyness, time to expiry, implied volatility, and Greeks."""

    chain = options.copy()
    spots = spot_prices.copy()
    chain.columns = [str(col).lower() for col in chain.columns]
    spots.columns = [str(col).lower() for col in spots.columns]
    if chain.empty:
        return chain
    if "underlying" in chain.columns and "secid" in spots.columns:
        price_col = "last" if "last" in spots.columns else "close"
        chain = chain.merge(
            spots[["secid", price_col]].rename(
                columns={"secid": "underlying", price_col: "spot"}
            ),
            on="underlying",
            how="left",
        )
    elif "spot" not in chain.columns:
        chain["spot"] = np.nan

    today = pd.Timestamp.today().normalize()
    chain["expiration"] = pd.to_datetime(chain.get("expiration"), errors="coerce")
    chain["time_to_expiry"] = (chain["expiration"] - today).dt.days / 365
    chain["strike"] = pd.to_numeric(chain.get("strike"), errors="coerce")
    price_col = "last" if "last" in chain.columns else "settleprice"
    chain["market_price"] = pd.to_numeric(chain.get(price_col), errors="coerce")
    chain["moneyness"] = chain["strike"] / pd.to_numeric(chain["spot"], errors="coerce")

    iv_values: list[float] = []
    deltas: list[float] = []
    gammas: list[float] = []
    vegas: list[float] = []
    thetas: list[float] = []
    for _, row in chain.iterrows():
        iv = implied_volatility(
            float(row.get("market_price", np.nan)),
            float(row.get("spot", np.nan)),
            float(row.get("strike", np.nan)),
            float(row.get("time_to_expiry", np.nan)),
            risk_free_rate,
            str(row.get("option_type", "")),
        )
        iv_values.append(iv)
        deltas.append(
            delta(
                row.get("spot", np.nan),
                row.get("strike", np.nan),
                row.get("time_to_expiry", np.nan),
                risk_free_rate,
                iv,
                str(row.get("option_type", "")),
            )
        )
        gammas.append(
            gamma(
                row.get("spot", np.nan),
                row.get("strike", np.nan),
                row.get("time_to_expiry", np.nan),
                risk_free_rate,
                iv,
            )
        )
        vegas.append(
            vega(
                row.get("spot", np.nan),
                row.get("strike", np.nan),
                row.get("time_to_expiry", np.nan),
                risk_free_rate,
                iv,
            )
        )
        thetas.append(
            theta(
                row.get("spot", np.nan),
                row.get("strike", np.nan),
                row.get("time_to_expiry", np.nan),
                risk_free_rate,
                iv,
                str(row.get("option_type", "")),
            )
        )
    chain["implied_volatility"] = iv_values
    chain["delta"] = deltas
    chain["gamma"] = gammas
    chain["vega"] = vegas
    chain["theta"] = thetas
    return chain


def build_volatility_smile(
    chain: pd.DataFrame,
    expiry: str,
) -> pd.DataFrame:
    """Return a smile slice for one expiry."""

    if chain.empty or "expiration" not in chain.columns:
        return pd.DataFrame()
    out = chain.copy()
    return out[out["expiration"].astype(str).str.startswith(str(expiry))].sort_values(
        "strike"
    )


def build_term_structure(
    chain: pd.DataFrame,
    moneyness_bucket: str = "atm",
) -> pd.DataFrame:
    """Build an implied volatility term structure by moneyness bucket."""

    if chain.empty or "moneyness" not in chain.columns:
        return pd.DataFrame()
    out = chain.copy()
    if moneyness_bucket == "atm":
        out = out[(out["moneyness"] >= 0.95) & (out["moneyness"] <= 1.05)]
    elif moneyness_bucket == "otm":
        out = out[out["moneyness"] > 1.05]
    elif moneyness_bucket == "itm":
        out = out[out["moneyness"] < 0.95]
    return (
        out.groupby("expiration", as_index=False)["implied_volatility"]
        .mean()
        .sort_values("expiration")
    )


def build_surface_grid(
    chain: pd.DataFrame,
) -> pd.DataFrame:
    """Pivot option chain features into an expiry-by-moneyness IV grid."""

    if chain.empty:
        return pd.DataFrame()
    out = chain.copy()
    out["moneyness_bucket"] = pd.cut(
        out["moneyness"],
        bins=[0, 0.8, 0.9, 1.0, 1.1, 1.2, np.inf],
        labels=["<0.8", "0.8-0.9", "0.9-1.0", "1.0-1.1", "1.1-1.2", ">1.2"],
    )
    return out.pivot_table(
        index="expiration",
        columns="moneyness_bucket",
        values="implied_volatility",
        aggfunc="mean",
        observed=False,
    )


def plot_volatility_smile(chain: pd.DataFrame, expiry: str):
    """Plot a volatility smile with Plotly."""

    smile = build_volatility_smile(chain, expiry)
    if smile.empty:
        return go.Figure()
    return px.line(
        smile, x="strike", y="implied_volatility", color="option_type", markers=True
    )


def plot_volatility_surface(chain: pd.DataFrame):
    """Plot an implied volatility surface heatmap with Plotly."""

    grid = build_surface_grid(chain)
    if grid.empty:
        return go.Figure()
    return px.imshow(
        grid, labels={"x": "Moneyness", "y": "Expiry", "color": "Implied Volatility"}
    )
