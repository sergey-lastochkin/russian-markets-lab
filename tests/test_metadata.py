from pathlib import Path

import pandas as pd

from russian_markets_lab.data.metadata import (
    build_metadata,
    read_metadata,
    write_metadata,
)


def test_metadata_creation() -> None:
    df = pd.DataFrame({"a": [1, 2]})
    metadata = build_metadata("dataset", df, "source", is_demo=True)
    assert metadata.row_count == 2
    assert metadata.columns == ["a"]
    assert metadata.is_demo is True


def test_metadata_write_read(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1]})
    metadata = build_metadata("dataset", df, "source")
    path = tmp_path / "dataset.metadata.json"
    write_metadata(metadata, path)
    payload = read_metadata(path)
    assert payload["dataset_name"] == "dataset"
    assert payload["row_count"] == 1
