from pathlib import Path

import pandas as pd

from russian_markets_lab.data.io import (
    processed_dataset_path,
    read_processed_dataset,
    read_processed_metadata,
    write_processed_dataset,
)


def test_write_processed_dataset_writes_parquet_and_metadata(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr("russian_markets_lab.data.io.PROCESSED_DATA_DIR", tmp_path)
    df = pd.DataFrame({"a": [1, 2]})
    write_processed_dataset(df, "dataset", "source", limitations=["limitation"])
    assert processed_dataset_path("dataset", tmp_path).exists()
    metadata = read_processed_metadata("dataset")
    assert metadata["row_count"] == 2
    assert metadata["columns"] == ["a"]


def test_read_missing_metadata_returns_empty(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("russian_markets_lab.data.io.PROCESSED_DATA_DIR", tmp_path)
    assert read_processed_metadata("missing") == {}


def test_read_processed_dataset_returns_empty_when_parquet_unreadable(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr("russian_markets_lab.data.io.PROCESSED_DATA_DIR", tmp_path)
    (tmp_path / "dataset.parquet").write_bytes(b"not a readable parquet file")

    def raise_import_error(*args, **kwargs):
        raise ImportError("pyarrow is missing")

    monkeypatch.setattr(
        "russian_markets_lab.data.io.pd.read_parquet",
        raise_import_error,
    )

    assert read_processed_dataset("dataset").empty
