"""Futures carry research signal."""

from __future__ import annotations

import pandas as pd


def generate_signals(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Convert basis monitor classifications into carry research signals."""

    del kwargs
    out = data.copy()
    if "signal" not in out.columns:
        return pd.DataFrame()
    out["carry_signal"] = (
        out["signal"].map({"cheap": 1.0, "fair": 0.0, "rich": -1.0}).fillna(0.0)
    )
    return out
