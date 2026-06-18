import pandas as pd

from russian_markets_lab.backtester.costs import (
    apply_commission,
    apply_slippage,
    calculate_turnover,
)


def test_commission_calculation() -> None:
    trades = pd.DataFrame({"quantity": [10], "price": [100]})
    result = apply_commission(trades, 10)
    assert result.iloc[0]["commission"] == 1


def test_slippage_calculation() -> None:
    trades = pd.DataFrame({"quantity": [10], "price": [100], "side": ["buy"]})
    result = apply_slippage(trades, 10)
    assert result.iloc[0]["execution_price"] == 100.1


def test_turnover() -> None:
    weights = pd.DataFrame({"A": [0.0, 0.5, 0.2], "B": [0.0, 0.5, 0.8]})
    turnover = calculate_turnover(weights)
    assert turnover.iloc[1] == 0.5
