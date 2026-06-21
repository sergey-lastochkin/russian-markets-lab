# Data Integrity Audit

Last updated: 2026-06-21.

## Scope

This note checks the main data-integrity risk in Russian Markets Lab:

- demo, sample, mock or generated values must not be shown as real market research;
- missing data must remain missing;
- cached data must be identifiable as cached or stale;
- public wording must not imply trading signals, guaranteed freshness or investment advice.

## Data Sources

The implemented market-data source is MOEX ISS public/delayed data.

Current processed datasets are built from:

- TQBR instruments, marketdata and candles;
- FORTS futures securities and marketdata;
- FORTS options securities and marketdata;
- derived analytics over processed pandas DataFrames.

The current implementation remains MOEX-first. Other data adapters are a possible future direction, not a completed abstraction.

## Processed Data

Processed datasets live in `data/processed/` as Parquet files with JSON metadata sidecars. Each sidecar records:

- dataset name;
- source;
- generation time;
- row count;
- columns;
- endpoints and parameters where available;
- limitations;
- `is_demo`.

The CLI command `python -m russian_markets_lab.cli dataset-status` reports the metadata-backed status for each processed dataset, including `data_mode`, `parquet_readable`, `source`, `generated_at`, `is_demo`, `stale` and any parquet read error.

## Raw Cache

Raw MOEX snapshots are stored under `data/raw/<dataset_name>/<timestamp>.parquet` when pipelines run locally. These files are cache artifacts from public ISS tables, not manually invented data.

The repository may not always ship a complete raw history. A missing raw cache is allowed; pipelines should either rebuild from MOEX ISS or use explicitly available cached tables without fabricating data.

## Demo And Sample Data

Demo data is isolated in:

```text
src/russian_markets_lab/demo/demo_data.py
```

Every demo helper states that it returns illustrative demo data only and must not be presented as real market output.

Dashboard demo mode is off by default. If enabled manually, the UI shows a visible warning. Demo data is only used for explicit demonstration paths and not as a silent fallback for production datasets.

Test fixtures and mocked values are allowed in `tests/` because they are not production output.

## Fallbacks

The market-universe pipeline can build a limited fallback universe from current MOEX marketdata if candles are unavailable. This fallback is still based on public MOEX data, not random or generated values. It is marked by low observation counts and limitations metadata.

Unreadable Parquet files do not crash the dashboard. Dataset status falls back to the metadata sidecar for row count and columns and sets `parquet_readable=false`.

Missing processed datasets return empty DataFrames and show missing-data messages rather than synthetic values.

## Safeguards

Current safeguards:

- processed datasets require metadata sidecars;
- dataset status includes `data_mode` values: `cache`, `stale`, `demo`, or `missing`;
- stale processed cache is flagged when metadata is older than the dashboard freshness threshold;
- dashboard and reports expose source, row count, generated time and demo flag;
- demo mode is opt-in and visibly marked;
- tests scan production code for suspicious silent fake-data patterns;
- dashboards and reports show empty or unavailable states instead of invented charts.

## Remaining Limitations

- MOEX ISS public data can be delayed, unavailable, sparse or revised.
- Processed snapshots can become stale if pipelines are not rerun.
- Public data does not include full broker routing, queue position or complete order-book depth.
- Futures and options mappings are best effort.
- Risk metrics are historical diagnostics and do not predict future losses.
- Execution cost modeling is simplified and does not represent real order placement.

## Review Result

No silent production path was found that turns demo, random, sample or mock values into real market output. The remaining fallback paths are either test-only, explicitly demo-only, or based on public MOEX cache/marketdata with limitations metadata.
