"""Build all Russian Markets Lab processed research snapshots."""

from __future__ import annotations

from russian_markets_lab.pipelines.full_snapshot_pipeline import (
    build_full_research_snapshot,
)


def main() -> None:
    """CLI entry point for `python -m russian_markets_lab.scripts.build_research_snapshot`."""

    outputs = build_full_research_snapshot()
    for name, frame in outputs.items():
        print(f"{name}.parquet: {len(frame)} rows")


if __name__ == "__main__":
    main()
