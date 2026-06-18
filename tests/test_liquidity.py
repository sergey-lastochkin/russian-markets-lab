import numpy as np
import pandas as pd

from russian_markets_lab.analytics.liquidity import (
    calculate_liquidity_score,
    calculate_spread,
    calculate_spread_bps,
    detect_volume_spikes,
)


def test_spread_calculation() -> None:
    assert calculate_spread(100, 101) == 1
    assert np.isnan(calculate_spread(101, 100))


def test_spread_bps() -> None:
    assert round(calculate_spread_bps(99, 101), 2) == 200.00


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
    assert scored.iloc[0]["ticker"] == "A"


def test_volume_spike_detection() -> None:
    candles = pd.DataFrame({"volume": [100] * 20 + [500]})
    spikes = detect_volume_spikes(candles, window=10, z_threshold=2.0)
    assert len(spikes) == 1
    assert spikes.iloc[0]["volume"] == 500
