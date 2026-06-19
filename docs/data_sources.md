# Data Sources

## MOEX ISS

Russian Markets Lab uses public/delayed MOEX ISS data.

Main endpoint groups:

- TQBR shares instruments and marketdata;
- TQBR daily candles;
- FORTS futures securities and marketdata;
- FORTS options securities and marketdata.

No private APIs, broker credentials or real-time paid feeds are used.

## Data Source Design

Russian Markets Lab currently uses MOEX ISS as the implemented data source. The processed datasets are stored as pandas/parquet tables, and most analytics functions operate on DataFrames rather than directly on MOEX API responses.

This makes it possible to add CSV or other market data sources later, as long as they are converted into the expected processed schema. MOEX ISS is the first implemented adapter, not the final limit of the project. The reusable analytics layer is a design direction, not a completed full abstraction across every possible market data source.

## Raw Cache

Raw tables are cached under:

`data/raw/<dataset_name>/<YYYYMMDD_HHMMSS>.parquet`

Each raw parquet file has:

`data/raw/<dataset_name>/<YYYYMMDD_HHMMSS>.metadata.json`

Raw cache metadata includes source, endpoint, params, generated_at, row_count, columns and limitations.

## Processed Datasets

Processed datasets are stored under `data/processed/` with metadata sidecars:

- `market_universe.parquet`
- `liquidity_radar.parquet`
- `futures_basis.parquet`
- `options_chain_features.parquet`
- `risk_snapshot.parquet`
- `execution_comparison.parquet`

Each has a matching `*.metadata.json` file.

## Update Process

Build all datasets:

```bash
python -m russian_markets_lab.cli build-all
```

Check dataset provenance:

```bash
python -m russian_markets_lab.cli dataset-status
```
