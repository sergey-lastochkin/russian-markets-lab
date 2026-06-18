"""Raw MOEX table cache helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from russian_markets_lab.data.metadata import (
    build_metadata,
    read_metadata,
    write_metadata,
)
from russian_markets_lab.paths import RAW_DATA_DIR


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def cache_raw_table(
    df: pd.DataFrame,
    dataset_name: str,
    source: str,
    endpoint: str,
    params: dict | None = None,
) -> Path:
    """Save raw MOEX table as parquet plus metadata."""

    target_dir = RAW_DATA_DIR / dataset_name
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = _timestamp()
    parquet_path = target_dir / f"{stamp}.parquet"
    df.to_parquet(parquet_path, index=False)
    metadata = build_metadata(
        dataset_name=dataset_name,
        df=df,
        source=source,
        endpoints=[endpoint],
        parameters={"params": params or {}},
        limitations=[
            "Raw public MOEX ISS table cached as received after column normalization.",
            "Public endpoint can be delayed, sparse, unavailable, or revised.",
        ],
        data_delay_note="MOEX ISS public/delayed data.",
    )
    write_metadata(metadata, target_dir / f"{stamp}.metadata.json")
    return parquet_path


def load_latest_raw_table(dataset_name: str) -> pd.DataFrame:
    """Load the latest cached raw table for a dataset if available."""

    target_dir = RAW_DATA_DIR / dataset_name
    files = sorted(target_dir.glob("*.parquet"))
    if not files:
        return pd.DataFrame()
    return pd.read_parquet(files[-1])


def list_raw_snapshots(dataset_name: str) -> pd.DataFrame:
    """List available raw snapshots and their metadata."""

    target_dir = RAW_DATA_DIR / dataset_name
    rows: list[dict[str, Any]] = []
    for parquet_path in sorted(target_dir.glob("*.parquet")):
        metadata = read_metadata(parquet_path.with_suffix(".metadata.json"))
        rows.append(
            {
                "dataset_name": dataset_name,
                "path": str(parquet_path),
                "generated_at": metadata.get("generated_at"),
                "source": metadata.get("source"),
                "row_count": metadata.get("row_count"),
                "columns": metadata.get("columns", []),
                "endpoints": metadata.get("endpoints", []),
            }
        )
    return pd.DataFrame(rows)
