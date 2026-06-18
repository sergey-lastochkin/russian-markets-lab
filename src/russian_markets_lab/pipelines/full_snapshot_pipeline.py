"""Full research snapshot orchestration."""

from __future__ import annotations

import pandas as pd

from russian_markets_lab.moex_client import MOEXISSClient
from russian_markets_lab.paths import REPORTS_DIR
from russian_markets_lab.pipelines.execution_pipeline import build_execution_snapshot
from russian_markets_lab.pipelines.futures_basis_pipeline import (
    build_futures_basis_snapshot,
)
from russian_markets_lab.pipelines.liquidity_pipeline import build_liquidity_snapshot
from russian_markets_lab.pipelines.market_universe_pipeline import (
    build_market_universe_components,
)
from russian_markets_lab.pipelines.options_pipeline import build_options_snapshot
from russian_markets_lab.pipelines.risk_pipeline import build_risk_snapshot
from russian_markets_lab.reports.report_builder import (
    build_derivatives_risk_report,
    build_execution_cost_report,
    build_liquidity_report,
    build_project_overview_report,
)


def build_full_research_snapshot(
    tickers_limit: int = 30,
    lookback_days: int = 365,
    use_cache: bool = True,
    max_option_contracts: int = 200,
) -> dict[str, pd.DataFrame]:
    """Build all processed research datasets and reports."""

    client = MOEXISSClient(timeout=20, retries=2)
    universe, marketdata, candles_by_ticker = build_market_universe_components(
        client,
        tickers_limit=tickers_limit,
        lookback_days=lookback_days,
        use_cache=use_cache,
    )
    from russian_markets_lab.data.io import write_processed_dataset

    write_processed_dataset(
        universe,
        "market_universe",
        source="MOEX ISS public/delayed data",
        endpoints=["TQBR securities", "TQBR marketdata", "TQBR candles"],
        parameters={"tickers_limit": tickers_limit, "lookback_days": lookback_days},
        limitations=[
            "Universe is selected by current traded value from public TQBR marketdata.",
            "If candles are unavailable, current-marketdata fallback is explicitly marked by low observations and tradable_flag=False.",
        ],
    )
    liquidity = build_liquidity_snapshot(universe, marketdata)
    futures_basis = build_futures_basis_snapshot(client, universe, use_cache=use_cache)
    options = build_options_snapshot(
        client, max_contracts=max_option_contracts, use_cache=use_cache
    )
    risk = build_risk_snapshot(candles_by_ticker, universe)
    execution = build_execution_snapshot(liquidity)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    build_liquidity_report(universe, REPORTS_DIR / "moex_liquidity_report.html")
    build_derivatives_risk_report(
        futures_basis, options, risk, REPORTS_DIR / "derivatives_risk_report.html"
    )
    build_execution_cost_report(execution, REPORTS_DIR / "execution_cost_report.html")
    build_project_overview_report(REPORTS_DIR / "project_overview_report.html")
    return {
        "market_universe": universe,
        "liquidity_radar": liquidity,
        "futures_basis": futures_basis,
        "options_chain_features": options,
        "risk_snapshot": risk,
        "execution_comparison": execution,
    }
