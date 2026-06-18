from pathlib import Path

import pandas as pd

from russian_markets_lab.data.cache import (
    cache_raw_table,
    list_raw_snapshots,
    load_latest_raw_table,
)


def test_cache_raw_table_writes_and_loads(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("russian_markets_lab.data.cache.RAW_DATA_DIR", tmp_path)
    df = pd.DataFrame({"a": [1]})
    path = cache_raw_table(df, "raw_dataset", "MOEX ISS", "/endpoint")
    assert path.exists()
    loaded = load_latest_raw_table("raw_dataset")
    assert loaded.equals(df)


def test_list_raw_snapshots(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("russian_markets_lab.data.cache.RAW_DATA_DIR", tmp_path)
    cache_raw_table(pd.DataFrame({"a": [1]}), "raw_dataset", "MOEX ISS", "/endpoint")
    snapshots = list_raw_snapshots("raw_dataset")
    assert len(snapshots) == 1
    assert snapshots.iloc[0]["row_count"] == 1


def test_missing_raw_cache_returns_empty(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("russian_markets_lab.data.cache.RAW_DATA_DIR", tmp_path)
    assert load_latest_raw_table("missing").empty
