import pandas as pd

from russian_markets_lab.dashboard.charts import (
    execution_cost_bar,
    market_liquidity_bar,
)


def test_chart_returns_none_for_missing_columns() -> None:
    assert market_liquidity_bar(pd.DataFrame({"a": [1]})) is None


def test_chart_returns_figure_for_valid_data() -> None:
    fig = market_liquidity_bar(
        pd.DataFrame({"ticker": ["A"], "tradability_score": [0.5]})
    )
    assert fig is not None


def test_execution_chart_returns_figure() -> None:
    fig = execution_cost_bar(
        pd.DataFrame({"execution_style": ["market"], "total_cost_bps": [10]})
    )
    assert fig is not None
