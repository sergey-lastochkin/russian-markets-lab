import pandas as pd

from russian_markets_lab.analytics.risk import (
    conditional_value_at_risk,
    correlation_matrix,
    max_drawdown,
    stress_test_portfolio,
    value_at_risk,
)


def test_var() -> None:
    returns = pd.Series([0.01, -0.02, 0.003, -0.04, 0.02])
    assert value_at_risk(returns, 0.8) > 0


def test_cvar() -> None:
    returns = pd.Series([0.01, -0.02, 0.003, -0.04, 0.02])
    assert conditional_value_at_risk(returns, 0.8) > 0


def test_max_drawdown() -> None:
    equity = pd.Series([1.0, 1.1, 1.0, 0.9, 1.2])
    assert max_drawdown(equity) < 0


def test_correlation_matrix_shape() -> None:
    returns = pd.DataFrame({"A": [0.1, 0.2], "B": [0.2, 0.1]})
    assert correlation_matrix(returns).shape == (2, 2)


def test_stress_test_output() -> None:
    positions = pd.DataFrame(
        {"instrument": ["A"], "position": [100], "risk_factor": ["equity"]}
    )
    result = stress_test_portfolio(positions, {"shock": {"equity": -0.1}})
    assert {
        "scenario",
        "instrument",
        "position",
        "shock",
        "pnl",
        "portfolio_pnl",
        "portfolio_pnl_pct",
    }.issubset(result.columns)
    assert result.iloc[0]["pnl"] == -10
