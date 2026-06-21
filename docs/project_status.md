# Project Status

## 1. What Works Now

Russian Markets Lab now supports a reproducible research workflow:

```text
MOEX ISS public/delayed data
-> raw cache
-> processed datasets
-> analytics modules
-> notebooks
-> HTML reports
-> Streamlit dashboard
```

Working components:

- MOEX ISS client with table parsing, pagination, retries and clear failures.
- Raw table cache under `data/raw/<dataset_name>/<timestamp>.parquet`.
- Processed Parquet datasets with metadata sidecars.
- Market universe, liquidity, futures basis, options, risk and execution pipelines.
- CLI commands for building datasets and checking dataset status.
- Streamlit dashboard that reads processed data and does not silently fabricate market outputs.
- Opt-in demo mode with visible warnings.
- HTML reports that handle empty datasets without fake values.
- Executable research notebooks that import project modules instead of duplicating core logic.
- Fast test suite that does not require live internet.

## 2. What Was Refactored

- The large snapshot script was reduced to a small orchestrator.
- Pipeline logic was moved into `src/russian_markets_lab/pipelines/`.
- Data provenance was centralized in `src/russian_markets_lab/data/metadata.py` and `src/russian_markets_lab/data/io.py`.
- Raw caching was implemented in `src/russian_markets_lab/data/cache.py`.
- Dashboard logic was split into:
  - `dashboard/data_loader.py`
  - `dashboard/charts.py`
  - `dashboard/components.py`
  - `dashboard/app.py`
- Demo data was isolated in `src/russian_markets_lab/demo/demo_data.py`.
- Analytics modules were hardened for empty data, missing columns and invalid inputs.

## 3. Where Real MOEX Data Is Used

Real public/delayed MOEX ISS data is used in:

- TQBR instruments and current marketdata for market universe construction.
- TQBR historical candles for selected liquid instruments where available.
- FORTS futures securities and marketdata for basis monitoring.
- FORTS options securities and marketdata for option chain features.

All processed outputs identify their source and limitations in metadata sidecars.

## 4. Where Demo Mode Exists

Demo mode is limited to `src/russian_markets_lab/demo/demo_data.py` and the dashboard checkbox:

```text
Use demo data when processed data is missing
```

The default is off. When enabled, the dashboard displays:

```text
Demo mode is enabled. Displayed values may be illustrative and are not real market research output.
```

Demo outputs must not be presented as real market research.

## 5. How To Rebuild All Datasets

```bash
python -m russian_markets_lab.cli build-all --tickers-limit 30 --lookback-days 365
```

Check dataset status:

```bash
python -m russian_markets_lab.cli dataset-status
```

Legacy-compatible command:

```bash
python -m russian_markets_lab.scripts.build_research_snapshot
```

## 6. How To Run Dashboard

```bash
streamlit run src/russian_markets_lab/dashboard/app.py
```

The dashboard reads processed datasets and metadata. If data is missing, it shows a missing-data message instead of generating fallback market results.

## 7. How To Run Tests

```bash
pytest
python -m compileall src tests
ruff check .
black --check .
```

Makefile shortcuts:

```bash
make test
make lint
make build-data
make dashboard
```

## 8. Pre-Commit Hardening Check

Last checked: 2026-06-18.

Environment/dependency command available when setting up a clean environment:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Dependency status:

- `pyarrow` installed and available.
- `ruff` installed and available.
- `black` installed and available.
- No dependency installation failures were observed.
- Parquet read/write support requires `pyarrow` or another pandas parquet engine. The supported project setup installs `pyarrow` through:

```bash
pip install -r requirements.txt
```

- If a processed Parquet file exists but cannot be read because the local parquet engine is missing, dashboard dataset status falls back to the metadata sidecar for `row_count` and `columns` and marks `parquet_readable=false`.

Quality commands run:

```bash
.venv/bin/pytest -q
.venv/bin/python -m compileall src tests
.venv/bin/ruff check .
.venv/bin/black --check .
.venv/bin/python -m russian_markets_lab.cli dataset-status
```

Results:

- `pytest`: passed, 53 tests.
- `python -m compileall src tests`: passed.
- `ruff check .`: passed.
- `black --check .`: passed.
- `python -m russian_markets_lab.cli dataset-status`: passed.
- No dependency-related failures were observed.

Dataset status result:

- `dataset-status` reported `exists`, `parquet_readable`, `metadata_exists`, `row_count`, `columns`, `generated_at`, `source`, `is_demo`, `limitations`, and `parquet_error`.
- Existing processed datasets were readable with `parquet_readable=true`.
- Row counts were metadata-backed and visible for all processed outputs.
- Missing datasets are handled by the status machinery without crashing.

Data provenance check:

- Every `data/processed/*.parquet` file had a matching `.metadata.json` sidecar.
- Processed metadata reported `is_demo=false`.
- `data/raw/` is intentionally empty by default except for `.gitkeep`; raw cache snapshots are generated locally when the pipeline runs.

No-fake production data check:

```bash
rg -n "np\\.random|random\\.|fallback|sample|demo|SBER|GAZP|LKOH|fake|placeholder|Coming soon" \
  src/russian_markets_lab/dashboard \
  src/russian_markets_lab/pipelines \
  src/russian_markets_lab/reports \
  src/russian_markets_lab/analytics -S
```

Result:

- No silent fake market data generation was found in production dashboard, pipeline or report code.
- Demo wiring in the dashboard is explicit and imports only from `src/russian_markets_lab/demo/demo_data.py`.
- The market-universe fallback is explicitly documented as current-marketdata-based and marks low-observation fallback rows as not fully tradable.
- Strategy template wording such as `placeholder` refers to research scaffolding, not fabricated market output.

Dashboard smoke test:

- Streamlit launched successfully with:

```bash
.venv/bin/streamlit run src/russian_markets_lab/dashboard/app.py --server.headless true --server.port 8501 --server.address 127.0.0.1
```

- With processed data present: dashboard rendered, dataset status was visible, and no Streamlit exception was detected.
- Dashboard defaults to English UI.
- Russian remains available through the EN/RU selector.
- Demo mode was off by default.
- Demo mode remains opt-in and displays this warning when enabled:

```text
Demo mode is enabled. Displayed values may be illustrative and are not real market research output.
```

Notebook sanity check:

- All notebooks were parsed as valid `.ipynb` JSON.
- Each notebook contains a title, purpose, data loading cell, methodology note, table/chart cell, limitations, and disclaimer.
- Notebooks do not embed fake results.

## 9. Known Limitations

- MOEX ISS public data can be delayed, incomplete or temporarily unavailable.
- Public endpoints may not provide full order book depth.
- Futures-to-spot mappings are best effort and can miss contracts.
- Options parsing depends on public metadata fields; IV and Greeks can be NaN.
- Black-Scholes assumptions are simplified for Russian rates, dividends and liquidity.
- Historical risk metrics are backward-looking.
- Execution simulation is a simplified cost model, not a broker-grade simulator.
- Cached data can become stale.
- Strategy templates are research scaffolding and not trading signals.
- Dashboard screenshots should be manually regenerated after meaningful UI changes if browser screenshot capture is unavailable in the local environment.

## 10. Next Recommended Improvements

- First Git commit with the hardened codebase.
- Manual dashboard screenshots in a separate follow-up commit after launching the current dashboard locally.
- Add snapshot freshness checks and warnings in CLI and dashboard.
- Expand futures and options mapping validation.
- Add a small, documented raw-data fixture for offline demos.
- Add notebook execution checks in CI.
- Add a report build CLI command.
- Add optional SQLite storage for larger local research datasets.

## 11. Data Integrity Pass, 2026-06-21

Focus:

- confirm that demo, sample, mock or generated values are not silently shown as real market research;
- make processed-cache provenance clearer in `dataset-status`, dashboard status tables and reports;
- document the remaining data limitations in `docs/data_integrity_audit.md`.

Changes:

- Added `data_mode`, `stale` and `generated_age_days` to dataset status.
- Dataset modes are now explicit: `cache`, `stale`, `demo` or `missing`.
- Dashboard dataset status tables show the data mode and stale flag where relevant.
- HTML report metadata tables include a data-mode column.
- README now links to the data-integrity audit and describes raw snapshots as local public-ISS cache artifacts.

Commands run during the pass:

```bash
.venv/bin/python -m compileall src tests
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/black --check .
PYTHONPATH=src .venv/bin/python -m russian_markets_lab.cli dataset-status
```

Remaining limitations:

- Processed snapshots can become stale if pipelines are not rerun.
- Public MOEX ISS data can be delayed, sparse or temporarily unavailable.
- Market-universe fallback from current marketdata is real MOEX data, but it remains a limited low-history fallback and is documented as such.
- Demo mode remains available only as an explicit dashboard option and must not be presented as real market research output.
