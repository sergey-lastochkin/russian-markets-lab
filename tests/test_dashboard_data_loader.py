from pathlib import Path

import pandas as pd

from russian_markets_lab.dashboard.data_loader import (
    dataset_status,
    load_metadata,
    load_processed_dataset,
)
from russian_markets_lab.data.metadata import build_metadata, write_metadata


def test_missing_dataset_returns_empty(tmp_path: Path) -> None:
    assert load_processed_dataset("missing", tmp_path).empty
    assert load_metadata("missing", tmp_path) == {}


def test_dataset_status(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1]})
    df.to_parquet(tmp_path / "dataset.parquet", index=False)
    metadata = build_metadata("dataset", df, "source")
    write_metadata(metadata, tmp_path / "dataset.metadata.json")
    status = dataset_status("dataset", tmp_path)
    assert status["exists"] is True
    assert status["metadata_exists"] is True
    assert status["row_count"] == 1


def test_dataset_status_falls_back_to_metadata_when_parquet_unreadable(
    tmp_path: Path, monkeypatch
) -> None:
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    (tmp_path / "dataset.parquet").write_bytes(b"not a readable parquet file")
    metadata = build_metadata("dataset", df, "source")
    write_metadata(metadata, tmp_path / "dataset.metadata.json")

    def raise_import_error(*args, **kwargs):
        raise ImportError("pyarrow is missing")

    monkeypatch.setattr(
        "russian_markets_lab.dashboard.data_loader.pd.read_parquet",
        raise_import_error,
    )

    status = dataset_status("dataset", tmp_path)

    assert status["exists"] is True
    assert status["metadata_exists"] is True
    assert status["parquet_readable"] is False
    assert status["row_count"] == 2
    assert status["columns"] == ["a", "b"]
    assert "pyarrow" in status["parquet_error"]
