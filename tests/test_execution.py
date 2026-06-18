from russian_markets_lab.analytics.execution import (
    compare_execution_styles,
    simulate_limit_order,
    simulate_market_order,
    simulate_twap,
)


def test_market_order_cost() -> None:
    result = simulate_market_order(100, 10, 20, 5)
    assert result["total_cost"] > 0
    assert result["fill_rate"] == 1.0


def test_limit_order_fill_logic() -> None:
    result = simulate_limit_order(100, 10, 1.2, 5)
    assert result["fill_rate"] == 1.0


def test_twap_output_shape() -> None:
    twap = simulate_twap(1_000_000, 5, 100_000_000, 10, 0.2, 5)
    assert twap.shape[0] == 5


def test_execution_comparison_table() -> None:
    comparison = compare_execution_styles(1_000_000, 100_000_000, 10, 0.2, 5)
    assert set(comparison["execution_style"]) == {"market", "limit", "twap", "vwap"}
    assert "total_cost_bps" in comparison.columns
