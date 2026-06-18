"""Historical candle accessors."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from russian_markets_lab.moex_client.iss_client import MOEXISSClient


def _normalize_candles(df: pd.DataFrame, secid: str) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).lower() for col in out.columns]
    out["secid"] = secid
    for col in ["begin", "end"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    return out


def get_candles(
    client: MOEXISSClient,
    secid: str,
    engine: str = "stock",
    market: str = "shares",
    board: str = "TQBR",
    from_date: str | None = None,
    till_date: str | None = None,
    interval: int = 24,
) -> pd.DataFrame:
    """Load candles for one security from MOEX ISS."""

    path = (
        f"/engines/{engine}/markets/{market}/boards/{board}/"
        f"securities/{secid}/candles.json"
    )
    params: dict[str, object] = {"interval": interval}
    if from_date:
        params["from"] = from_date
    if till_date:
        params["till"] = till_date
    return _normalize_candles(
        client.get_all_pages(path, "candles", params=params), secid
    )


def save_candles_to_parquet(df: pd.DataFrame, secid: str, path: str) -> None:
    """Save candle data for one security as parquet."""

    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_dir / f"{secid}.parquet", index=False)


def load_candles_from_parquet(secid: str, path: str) -> pd.DataFrame:
    """Load candle data for one security from parquet."""

    file_path = Path(path) / f"{secid}.parquet"
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(file_path)
