# Russian Markets Lab

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![pytest](https://img.shields.io/badge/tests-pytest-green)
![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red)
![MOEX ISS](https://img.shields.io/badge/data-MOEX%20ISS-lightgrey)

**Research platform for MOEX liquidity, derivatives, risk, and execution analysis.**  

This is a reproducible market research stack, not an order-sending or signal-selling application.

Russian Markets Lab is a Python-based research environment for Russian market analysis through public and delayed MOEX ISS data. The project is organized around a real research workflow:

```text
MOEX ISS public/delayed data
-> raw cached data
-> processed research datasets
-> analytics modules
-> notebooks and reports
-> Streamlit dashboard
```

Current status: broad research prototype under active hardening. The project already includes core modules for MOEX data ingestion, market universe construction, liquidity diagnostics, futures basis, options analytics, risk, execution simulation, dashboard, reports and tests. The current focus is reproducibility, methodology, data provenance and deeper validation.

## What This Project Does

- Builds a MOEX market universe from public ISS instruments, marketdata and candles.
- Computes first-pass liquidity diagnostics: average value, turnover, spread proxy, volatility penalty and score components.
- Monitors futures basis as a rich/fair/cheap diagnostic, not as an arbitrage claim.
- Builds options chain features, implied volatility and Greeks where public fields are sufficient.
- Estimates portfolio risk from historical daily returns: VaR, CVaR, volatility, drawdown, correlation and stress scenarios.
- Compares execution styles with transparent cost assumptions: market, limit, TWAP and VWAP.
- Provides research notebooks, HTML reports, CLI commands and a Streamlit dashboard.

## What It Does Not Do

- No broker integration.
- No real order sending.
- No personal PnL tracking.
- No private API keys.
- No investment advice or trading signals.
- No performance promises, predictive claims or certainty language.
- No silent fake data. Demo data is opt-in and visibly marked.

## Architecture

```text
russian-markets-lab/
  docs/                         methodology, data sources, limitations, audit
  data/raw/                     timestamped MOEX raw cache snapshots
  data/processed/               research datasets plus metadata sidecars
  src/russian_markets_lab/
    moex_client/                MOEX ISS clients and endpoint wrappers
    data/                       provenance, processed IO, raw cache
    analytics/                  market universe, liquidity, basis, options, risk, execution
    pipelines/                  raw -> processed dataset builders
    strategies/                 research strategy templates
    backtester/                 vectorized backtest utilities
    dashboard/                  thin Streamlit frontend
    reports/                    HTML report builders
    scripts/                    small orchestration entrypoints
  notebooks/                    executable research notebooks
  tests/                        fast unit tests, no live internet dependency
```

The dashboard is not the project. It is a frontend window into the pipeline outputs.

## Data Pipeline

Processed datasets are written as Parquet with JSON metadata sidecars:

- `data/processed/market_universe.parquet`
- `data/processed/market_universe.metadata.json`
- `data/processed/liquidity_radar.parquet`
- `data/processed/liquidity_radar.metadata.json`
- `data/processed/futures_basis.parquet`
- `data/processed/futures_basis.metadata.json`
- `data/processed/options_chain_features.parquet`
- `data/processed/options_chain_features.metadata.json`
- `data/processed/risk_snapshot.parquet`
- `data/processed/risk_snapshot.metadata.json`
- `data/processed/execution_comparison.parquet`
- `data/processed/execution_comparison.metadata.json`

Raw ISS snapshots are cached under `data/raw/<dataset_name>/<timestamp>.parquet` with matching metadata when the pipeline runs locally. The repository keeps `data/raw/` empty by default except for `.gitkeep`, because raw snapshots are timestamped local artifacts. If MOEX is temporarily unavailable, pipelines may use the latest local raw cache. They do not fabricate market data.

## Modules

1. **MOEX Market Universe Scanner**: instruments, marketdata, candles, tradability and data quality.
2. **Liquidity Radar**: liquidity scores, score components, turnover, spread proxy and volume spikes.
3. **Futures Basis Monitor**: basis, annualized basis, liquidity filter and rich/fair/cheap screen.
4. **Options Volatility Surface**: chain features, moneyness, time to expiry, IV, Greeks, smile and surface.
5. **Portfolio Risk Engine**: historical risk metrics, drawdown, correlation and stress scenarios.
6. **Execution Simulator**: spread crossing, slippage, market impact, fill-rate assumptions and cost comparison.
7. **Strategy Research Lab**: strategy templates with cost sensitivity and failure analysis.
8. **Streamlit Dashboard**: EN/RU language selector, dataset status, metadata, charts and explicit demo mode.
9. **Research Reports**: HTML reports with methodology, metadata, limitations and disclaimer.

## Dashboard Screenshots

Screenshots should be regenerated after running the current dashboard.

The dashboard uses English as the default UI language, keeps Russian available through the EN/RU selector, and is designed as a dark, dense internal markets research terminal. Stale screenshots are intentionally not embedded in this README.

## Methodology

- [Methodology](docs/methodology.md)
- [Data Sources](docs/data_sources.md)
- [Limitations](docs/limitations.md)
- [Audit](docs/audit.md)
- [Project Status](docs/project_status.md)

## Quickstart

```bash
git clone https://github.com/<username>/russian-markets-lab.git
cd russian-markets-lab
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
pip install -e .
```

Windows:

```bat
.venv\Scripts\activate
```

## Build Data

Build the full research snapshot:

```bash
python -m russian_markets_lab.cli build-all --tickers-limit 30 --lookback-days 365
```

Other CLI commands:

```bash
python -m russian_markets_lab.cli build-universe --tickers-limit 30 --lookback-days 365
python -m russian_markets_lab.cli build-liquidity
python -m russian_markets_lab.cli build-futures-basis
python -m russian_markets_lab.cli build-options --max-contracts 200
python -m russian_markets_lab.cli build-risk
python -m russian_markets_lab.cli build-execution
python -m russian_markets_lab.cli dataset-status
```

Legacy-compatible orchestrator:

```bash
python -m russian_markets_lab.scripts.build_research_snapshot
```

## Run Dashboard

```bash
streamlit run src/russian_markets_lab/dashboard/app.py
```

The dashboard defaults to English UI, includes an EN/RU language selector, and has an explicit demo-mode checkbox. Demo mode is off by default.

## Run Tests

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

## Project Status

Implemented:

- MOEX ISS client and endpoint wrappers.
- Raw cache and processed dataset metadata.
- Split pipelines for universe, liquidity, futures basis, options, risk and execution.
- Streamlit dashboard with explicit missing-data and demo-mode states.
- HTML report builders.
- Research notebooks.
- Fast unit tests without live internet dependency.

In progress:

- Deeper validation of derivative contract mappings.
- Better handling of corporate actions and security lifecycle.
- Broader notebook QA with multiple market regimes.
- More complete screenshot regeneration workflow.

Planned:

- Optional SQLite storage layer.
- More robust option symbol parser.
- More detailed transaction cost calibration from public data.
- Walk-forward strategy research templates with clearer train/test reporting.

## Disclaimer

This project is for research and educational purposes only. It does not provide investment advice, trading signals, brokerage functionality, or real-money order execution.
