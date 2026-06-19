import numpy as np
import pandas as pd

from russian_markets_lab.analytics.liquidity import (
    calculate_amihud_illiquidity,
    calculate_liquidity_score,
    calculate_spread,
    calculate_spread_bps,
    calculate_spread_proxy_bps,
    classify_liquidity_regime,
    detect_volume_spikes,
    explain_liquidity_score_components,
)


def test_spread_calculation() -> None:
    assert calculate_spread(100, 101) == 1
    assert np.isnan(calculate_spread(101, 100))
    assert np.isnan(calculate_spread(0, 100))
    assert np.isnan(calculate_spread(100, 0))


def test_spread_bps() -> None:
    assert round(calculate_spread_bps(99, 101), 2) == 200.00
    assert np.isnan(calculate_spread_bps(100, 99))


def test_spread_proxy_bps() -> None:
    assert calculate_spread_proxy_bps(high=110, low=100) > 0
    assert calculate_spread_proxy_bps(close=105, previous_close=100) > 0
    assert np.isnan(calculate_spread_proxy_bps(high=100, low=110))


def test_amihud_illiquidity_ignores_invalid_value() -> None:
    returns = pd.Series([0.01, -0.02, 0.03])
    value = pd.Series([1000.0, 0.0, np.nan])
    result = calculate_amihud_illiquidity(returns, value)
    assert np.isclose(result, 0.01 / 1000.0)


def test_liquidity_score_output() -> None:
    df = pd.DataFrame(
        {
            "ticker": ["A", "B"],
            "avg_value": [1000, 100],
            "avg_volume": [10, 5],
            "num_trades": [20, 2],
            "spread_bps": [10, 100],
            "realized_volatility": [0.2, 0.5],
        }
    )
    scored = calculate_liquidity_score(df)
    assert "liquidity_score" in scored.columns
    assert "liquidity_regime" in scored.columns
    assert "avg_value_component" in scored.columns
    assert scored.iloc[0]["ticker"] == "A"


def test_liquidity_score_components_output() -> None:
    df = pd.DataFrame(
        {
            "ticker": ["A", "B"],
            "avg_daily_value": [1_000_000, 100_000],
            "avg_volume": [1000, 100],
            "num_trades": [100, 10],
            "spread_bps": [5, 50],
            "realized_volatility": [0.2, 0.5],
            "data_quality_score": [1.0, 0.8],
        }
    )
    components = explain_liquidity_score_components(df)
    assert {
        "avg_value_component",
        "volume_component",
        "trade_count_component",
        "spread_component",
        "volatility_penalty",
        "data_quality_component",
        "liquidity_score",
        "liquidity_regime",
    }.issubset(components.columns)


def test_liquidity_regime_classification() -> None:
    assert classify_liquidity_regime(0.8, 1.0) == "liquid"
    assert classify_liquidity_regime(0.5, 1.0) == "watch"
    assert classify_liquidity_regime(0.2, 1.0) == "illiquid"
    assert classify_liquidity_regime(0.8, 0.2) == "insufficient_data"


def test_volume_spike_detection() -> None:
    candles = pd.DataFrame({"volume": [100] * 20 + [500]})
    spikes = detect_volume_spikes(candles, window=10, z_threshold=2.0)
    assert len(spikes) == 1
    assert spikes.iloc[0]["volume"] == 500
