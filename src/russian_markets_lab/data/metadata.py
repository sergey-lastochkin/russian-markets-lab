"""Dataset metadata sidecars for processed and raw research datasets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class DatasetMetadata:
    """Serializable metadata for a research dataset."""

    dataset_name: str
    source: str
    generated_at: str
    row_count: int
    columns: list[str]
    endpoints: list[str]
    parameters: dict[str, Any]
    limitations: list[str]
    is_demo: bool = False
    data_delay_note: str | None = None


def build_metadata(
    dataset_name: str,
    df: pd.DataFrame,
    source: str,
    endpoints: list[str] | None = None,
    parameters: dict | None = None,
    limitations: list[str] | None = None,
    is_demo: bool = False,
    data_delay_note: str | None = None,
) -> DatasetMetadata:
    """Build a metadata record for a DataFrame."""

    return DatasetMetadata(
        dataset_name=dataset_name,
        source=source,
        generated_at=datetime.now(UTC).isoformat(),
        row_count=int(len(df)),
        columns=[str(col) for col in df.columns],
        endpoints=endpoints or [],
        parameters=dict(parameters or {}),
        limitations=list(limitations or []),
        is_demo=is_demo,
        data_delay_note=data_delay_note,
    )


def write_metadata(metadata: DatasetMetadata, path: Path) -> None:
    """Write metadata JSON sidecar."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(metadata), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_metadata(path: Path) -> dict:
    """Read metadata JSON sidecar. Return empty dict if missing or invalid."""

    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}
