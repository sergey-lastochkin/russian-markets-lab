"""Dashboard data loading helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from russian_markets_lab.data.io import (
    processed_dataset_path,
    processed_metadata_path,
)
from russian_markets_lab.data.metadata import read_metadata
from russian_markets_lab.paths import PROCESSED_DATA_DIR

STALE_AFTER_DAYS = 7


def load_processed_dataset(
    name: str, processed_dir: Path | None = None
) -> pd.DataFrame:
    """Load a processed parquet dataset by name.

    Return an empty DataFrame if the file is missing or unreadable. Unreadable
    parquet files can happen when pyarrow/fastparquet is not installed; status
    helpers report that case through ``parquet_readable=False``.
    """

    path = processed_dataset_path(name, processed_dir)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def load_metadata(name: str, processed_dir: Path | None = None) -> dict:
    """Load metadata JSON sidecar for a processed dataset. Return empty dict if missing."""

    return read_metadata(processed_metadata_path(name, processed_dir))


def _metadata_age_days(metadata: dict) -> float | None:
    generated_at = metadata.get("generated_at")
    if not generated_at:
        return None
    timestamp = pd.to_datetime(generated_at, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return None
    age = datetime.now(UTC) - timestamp.to_pydatetime()
    return max(age.total_seconds() / 86_400, 0.0)


def _data_mode(exists: bool, metadata: dict, stale: bool) -> str:
    if not exists:
        return "missing"
    if bool(metadata.get("is_demo", False)):
        return "demo"
    if stale:
        return "stale"
    return "cache"


def dataset_status(name: str, processed_dir: Path | None = None) -> dict:
    """Return processed dataset status for dashboards and CLI summaries."""

    base = processed_dir or PROCESSED_DATA_DIR
    parquet_path = processed_dataset_path(name, base)
    metadata_path = processed_metadata_path(name, base)
    metadata = load_metadata(name, base)
    exists = parquet_path.exists()
    parquet_readable = False
    parquet_error: str | None = None
    if exists:
        try:
            df = pd.read_parquet(parquet_path)
            row_count = int(len(df))
            columns = [str(col) for col in df.columns]
            parquet_readable = True
        except Exception:
            row_count = int(metadata.get("row_count", 0) or 0)
            columns = [str(col) for col in metadata.get("columns", [])]
            parquet_error = "Parquet file exists but could not be read. Install pyarrow or fastparquet."
    else:
        row_count = 0
        columns = []
    generated_age_days = _metadata_age_days(metadata)
    stale = bool(
        generated_age_days is not None and generated_age_days > STALE_AFTER_DAYS
    )
    data_mode = _data_mode(exists, metadata, stale)
    return {
        "dataset_name": name.removesuffix(".parquet"),
        "exists": exists,
        "parquet_readable": parquet_readable,
        "data_mode": data_mode,
        "stale": stale,
        "generated_age_days": generated_age_days,
        "row_count": row_count,
        "columns": columns,
        "metadata_exists": metadata_path.exists(),
        "generated_at": metadata.get("generated_at"),
        "source": metadata.get("source"),
        "is_demo": metadata.get("is_demo", False),
        "limitations": metadata.get("limitations", []),
        "parquet_error": parquet_error,
    }


def all_dataset_statuses(names: list[str]) -> pd.DataFrame:
    """Return status table for dashboard sidebar."""

    return pd.DataFrame([dataset_status(name) for name in names])
