import pandas as pd

from russian_markets_lab.pipelines.futures_basis_pipeline import (
    build_futures_basis_table,
)
from russian_markets_lab.pipelines.liquidity_pipeline import build_liquidity_snapshot
from russian_markets_lab.pipelines.options_pipeline import build_options_features


def test_liquidity_pipeline_handles_empty(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("russian_markets_lab.data.io.PROCESSED_DATA_DIR", tmp_path)
    result = build_liquidity_snapshot(pd.DataFrame())
    assert result.empty
    assert "liquidity_score" in result.columns


def test_futures_basis_returns_empty_schema_if_mapping_fails() -> None:
    spot = pd.DataFrame({"ticker": ["AAA"], "last_close": [100.0]})
    fut_sec = pd.DataFrame({"secid": ["FUT"], "assetcode": ["BBB"]})
    fut_md = pd.DataFrame({"secid": ["FUT"]})
    result = build_futures_basis_table(spot, fut_sec, fut_md)
    assert result.empty
    assert "annualized_basis" in result.columns
    assert "confidence" in result.columns


def test_options_pipeline_handles_invalid_contracts() -> None:
    sec = pd.DataFrame(
        {
            "secid": ["OPT"],
            "optiontype": ["C"],
            "strike": [0],
            "lasttradedate": ["2026-12-01"],
            "underlyingsettleprice": [100],
            "prevsettleprice": [1],
        }
    )
    result = build_options_features(sec, pd.DataFrame())
    assert result.empty
    assert "implied_volatility" in result.columns
