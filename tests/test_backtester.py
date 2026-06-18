import pandas as pd

from russian_markets_lab.backtester.engine import run_vectorized_backtest
from russian_markets_lab.backtester.portfolio import train_test_split


def test_equity_curve_creation() -> None:
    prices = pd.DataFrame({"A": [100, 101, 102, 101]})
    signals = pd.DataFrame({"A": [1, 1, 1, 1]})
    result = run_vectorized_backtest(prices, signals)
    assert "equity_curve" in result
    assert len(result["equity_curve"]) == len(prices)


def test_metrics_output() -> None:
    prices = pd.DataFrame({"A": [100, 101, 102, 101], "B": [50, 51, 49, 50]})
    signals = pd.DataFrame({"A": [1, 1, 1, 1], "B": [0, 0, 0, 0]})
    result = run_vectorized_backtest(prices, signals, long_short=False)
    assert "sharpe_ratio" in result["metrics"]
    assert "turnover" in result["metrics"]


def test_train_test_split() -> None:
    data = pd.DataFrame({"A": range(10)})
    train, test = train_test_split(data, 0.6)
    assert len(train) == 6
    assert len(test) == 4
