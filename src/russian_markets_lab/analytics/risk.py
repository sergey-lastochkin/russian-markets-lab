"""Portfolio risk analytics and stress testing."""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_SCENARIOS: dict[str, dict[str, float]] = {
    "USD/RUB +10%": {"usdrub": 0.10, "fx": 0.10},
    "MOEX index -15%": {"moex": -0.15, "equity": -0.15},
    "oil -20%": {"oil": -0.20, "energy": -0.20},
    "volatility x2": {"volatility": 1.00},
    "interest rates +300 bps": {"rates": -0.03, "bond": -0.03},
    "single-name gap down -25%": {"single_name": -0.25, "equity": -0.25},
}


def portfolio_returns(
    returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    """Calculate weighted portfolio returns."""

    aligned = returns.copy()
    weight_series = pd.Series(weights, dtype=float).reindex(aligned.columns).fillna(0)
    return aligned.mul(weight_series, axis=1).sum(axis=1)


def value_at_risk(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:
    """Historical value at risk as a positive loss number."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(-np.quantile(clean, 1 - confidence))


def conditional_value_at_risk(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:
    """Historical conditional value at risk as a positive loss number."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    cutoff = np.quantile(clean, 1 - confidence)
    tail = clean[clean <= cutoff]
    if tail.empty:
        return float("nan")
    return float(-tail.mean())


def drawdown_series(equity_curve: pd.Series) -> pd.Series:
    """Calculate drawdown series from an equity curve."""

    equity = pd.to_numeric(equity_curve, errors="coerce")
    running_max = equity.cummax()
    return equity / running_max - 1


def max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate maximum drawdown."""

    dd = drawdown_series(equity_curve)
    if dd.empty:
        return float("nan")
    return float(dd.min())


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Calculate a correlation matrix."""

    return returns.corr()


def risk_summary_table(returns: pd.Series) -> pd.DataFrame:
    """Return a compact historical risk summary table."""

    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty:
        return pd.DataFrame(columns=["metric", "value"])
    equity = (1 + clean).cumprod()
    return pd.DataFrame(
        [
            {"metric": "mean_daily_return", "value": float(clean.mean())},
            {
                "metric": "annualized_volatility",
                "value": float(clean.std(ddof=1) * np.sqrt(252)),
            },
            {"metric": "VaR 95%", "value": value_at_risk(clean)},
            {"metric": "CVaR 95%", "value": conditional_value_at_risk(clean)},
            {"metric": "max_drawdown", "value": max_drawdown(equity)},
            {"metric": "observations", "value": float(len(clean))},
        ]
    )


def volatility_target_weights(
    returns: pd.DataFrame,
    target_vol: float = 0.15,
) -> dict[str, float]:
    """Estimate inverse-volatility weights scaled to a target portfolio volatility."""

    vols = returns.std() * np.sqrt(252)
    inv = 1 / vols.replace(0, np.nan)
    weights = inv / inv.sum()
    portfolio_vol = float(
        np.sqrt((returns.mul(weights, axis=1).sum(axis=1)).var() * 252)
    )
    if portfolio_vol > 0 and np.isfinite(portfolio_vol):
        weights = weights * (target_vol / portfolio_vol)
    return weights.fillna(0).to_dict()


def stress_test_portfolio(
    positions: pd.DataFrame,
    scenarios: dict[str, dict[str, float]] | None = None,
) -> pd.DataFrame:
    """Apply scenario shocks to a portfolio positions table."""

    scenario_map = scenarios or DEFAULT_SCENARIOS
    pos = positions.copy()
    pos.columns = [str(col).lower() for col in pos.columns]
    if "position" not in pos.columns and "market_value" in pos.columns:
        pos["position"] = pos["market_value"]
    if "risk_factor" not in pos.columns:
        pos["risk_factor"] = pos.get("instrument", "").astype(str).str.lower()
    total_position = pd.to_numeric(pos["position"], errors="coerce").abs().sum()
    rows: list[dict[str, object]] = []
    for scenario, shocks in scenario_map.items():
        scenario_rows: list[dict[str, object]] = []
        for _, row in pos.iterrows():
            factor = str(row.get("risk_factor", "")).lower()
            shock = shocks.get(factor, shocks.get("default", 0.0))
            position = float(row.get("position", 0.0))
            pnl = position * shock
            scenario_rows.append(
                {
                    "scenario": scenario,
                    "instrument": row.get("instrument", row.get("secid", "")),
                    "position": position,
                    "shock": shock,
                    "pnl": pnl,
                }
            )
        portfolio_pnl = sum(item["pnl"] for item in scenario_rows)
        portfolio_pnl_pct = portfolio_pnl / total_position if total_position else np.nan
        for item in scenario_rows:
            item["portfolio_pnl"] = portfolio_pnl
            item["portfolio_pnl_pct"] = portfolio_pnl_pct
            rows.append(item)
    return pd.DataFrame(rows)
