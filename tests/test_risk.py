import pandas as pd
import pytest

from russian_markets_lab.analytics.risk import (
    conditional_value_at_risk,
    correlation_matrix,
    max_drawdown,
    risk_contribution_approximation,
    risk_summary_table,
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


def test_risk_summary_table_includes_methodology_columns() -> None:
    returns = pd.Series([0.01, -0.02, 0.003, -0.04, 0.02])
    summary = risk_summary_table(returns)
    assert {"metric", "value", "method", "window", "limitations"}.issubset(
        summary.columns
    )
    assert "VaR 95%" in set(summary["metric"])


def test_risk_contribution_approximation_sums_to_one() -> None:
    returns = pd.DataFrame(
        {
            "A": [0.01, -0.02, 0.015, 0.004],
            "B": [0.005, -0.01, 0.006, 0.002],
        }
    )
    contribution = risk_contribution_approximation(returns, {"A": 0.5, "B": 0.5})
    assert {"risk_contribution_pct", "risk_contribution_vol"}.issubset(
        contribution.columns
    )
    assert contribution["risk_contribution_pct"].sum() == pytest.approx(1.0)


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
