"""Command line interface for Russian Markets Lab."""

from __future__ import annotations

import argparse

import pandas as pd

from russian_markets_lab.dashboard.data_loader import all_dataset_statuses
from russian_markets_lab.data.io import read_processed_dataset
from russian_markets_lab.moex_client import MOEXISSClient
from russian_markets_lab.pipelines.execution_pipeline import build_execution_snapshot
from russian_markets_lab.pipelines.full_snapshot_pipeline import (
    build_full_research_snapshot,
)
from russian_markets_lab.pipelines.futures_basis_pipeline import (
    build_futures_basis_snapshot,
)
from russian_markets_lab.pipelines.liquidity_pipeline import build_liquidity_snapshot
from russian_markets_lab.pipelines.market_universe_pipeline import (
    build_market_universe_components,
)
from russian_markets_lab.pipelines.options_pipeline import build_options_snapshot
from russian_markets_lab.pipelines.risk_pipeline import build_risk_snapshot

DATASET_NAMES = [
    "market_universe",
    "liquidity_radar",
    "futures_basis",
    "options_chain_features",
    "risk_snapshot",
    "execution_comparison",
]


def _print_shape(name: str, df: pd.DataFrame) -> None:
    print(f"{name}: {len(df)} rows, {len(df.columns)} columns")


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(description="Russian Markets Lab CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    universe = sub.add_parser("build-universe")
    universe.add_argument("--tickers-limit", type=int, default=30)
    universe.add_argument("--lookback-days", type=int, default=365)

    sub.add_parser("build-liquidity")
    sub.add_parser("build-futures-basis")

    options = sub.add_parser("build-options")
    options.add_argument("--max-contracts", type=int, default=200)

    sub.add_parser("build-risk")
    sub.add_parser("build-execution")

    all_cmd = sub.add_parser("build-all")
    all_cmd.add_argument("--tickers-limit", type=int, default=30)
    all_cmd.add_argument("--lookback-days", type=int, default=365)
    all_cmd.add_argument("--max-contracts", type=int, default=200)

    sub.add_parser("dataset-status")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run CLI command."""

    args = build_parser().parse_args(argv)
    client = MOEXISSClient(timeout=20, retries=2)

    if args.command == "build-universe":
        universe, _, _ = build_market_universe_components(
            client,
            tickers_limit=args.tickers_limit,
            lookback_days=args.lookback_days,
        )
        from russian_markets_lab.data.io import write_processed_dataset

        write_processed_dataset(
            universe,
            "market_universe",
            source="MOEX ISS public/delayed data",
            endpoints=["TQBR securities", "TQBR marketdata", "TQBR candles"],
            parameters={
                "tickers_limit": args.tickers_limit,
                "lookback_days": args.lookback_days,
            },
            limitations=["See docs/methodology.md and docs/limitations.md."],
        )
        _print_shape("market_universe", universe)
    elif args.command == "build-liquidity":
        universe = read_processed_dataset("market_universe")
        liquidity = build_liquidity_snapshot(universe)
        _print_shape("liquidity_radar", liquidity)
    elif args.command == "build-futures-basis":
        universe = read_processed_dataset("market_universe")
        basis = build_futures_basis_snapshot(client, universe)
        _print_shape("futures_basis", basis)
    elif args.command == "build-options":
        options = build_options_snapshot(client, max_contracts=args.max_contracts)
        _print_shape("options_chain_features", options)
    elif args.command == "build-risk":
        risk = build_risk_snapshot({})
        _print_shape("risk_snapshot", risk)
    elif args.command == "build-execution":
        liquidity = read_processed_dataset("liquidity_radar")
        execution = build_execution_snapshot(liquidity)
        _print_shape("execution_comparison", execution)
    elif args.command == "build-all":
        outputs = build_full_research_snapshot(
            tickers_limit=args.tickers_limit,
            lookback_days=args.lookback_days,
            max_option_contracts=args.max_contracts,
        )
        for name, frame in outputs.items():
            _print_shape(name, frame)
    elif args.command == "dataset-status":
        statuses = all_dataset_statuses(DATASET_NAMES)
        print(statuses.to_string(index=False))


if __name__ == "__main__":
    main()
