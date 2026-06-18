"""Processed dataset IO with metadata sidecars."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from russian_markets_lab.data.metadata import (
    build_metadata,
    read_metadata,
    write_metadata,
)
from russian_markets_lab.paths import PROCESSED_DATA_DIR

DATA_DELAY_NOTE = (
    "MOEX ISS public/delayed data. Availability and delay depend on the endpoint."
)


def processed_dataset_path(
    dataset_name: str, processed_dir: Path | None = None
) -> Path:
    """Return processed parquet path for a dataset name."""

    base = processed_dir or PROCESSED_DATA_DIR
    filename = (
        dataset_name if dataset_name.endswith(".parquet") else f"{dataset_name}.parquet"
    )
    return base / filename


def processed_metadata_path(
    dataset_name: str, processed_dir: Path | None = None
) -> Path:
    """Return processed metadata sidecar path for a dataset name."""

    base = processed_dir or PROCESSED_DATA_DIR
    stem = dataset_name.removesuffix(".parquet")
    return base / f"{stem}.metadata.json"


def write_processed_dataset(
    df: pd.DataFrame,
    dataset_name: str,
    source: str,
    endpoints: list[str] | None = None,
    parameters: dict | None = None,
    limitations: list[str] | None = None,
    is_demo: bool = False,
) -> None:
    """Write parquet and metadata sidecar."""

    parquet_path = processed_dataset_path(dataset_name)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    metadata = build_metadata(
        dataset_name=dataset_name.removesuffix(".parquet"),
        df=df,
        source=source,
        endpoints=endpoints,
        parameters=parameters,
        limitations=limitations,
        is_demo=is_demo,
        data_delay_note=DATA_DELAY_NOTE,
    )
    write_metadata(metadata, processed_metadata_path(dataset_name))


def read_processed_dataset(dataset_name: str) -> pd.DataFrame:
    """Read processed parquet dataset.

    Return an empty DataFrame when the file is missing or cannot be read. The
    unreadable-file path is intentionally non-fatal so dashboards and reports can
    keep running when the local environment lacks a parquet engine such as
    pyarrow or fastparquet.
    """

    path = processed_dataset_path(dataset_name)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def read_processed_metadata(dataset_name: str) -> dict:
    """Read processed metadata sidecar. Return empty dict if missing."""

    return read_metadata(processed_metadata_path(dataset_name))
