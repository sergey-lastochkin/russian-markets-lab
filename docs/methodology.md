# Methodology

## Market Universe

Universe construction starts from public MOEX ISS TQBR shares data. The pipeline loads instruments, current marketdata and daily candles for the most liquid names by current traded value.

Calculated fields:

- `avg_daily_value`: average daily traded value from candles;
- `median_daily_value`: median daily traded value;
- `realized_volatility`: annualized volatility from daily log returns;
- `num_observations`: number of valid close observations;
- `tradable_flag`: true only when value, observation count, volatility and last close pass basic quality gates;
- `data_quality_score`: observation count, missing close/value ratios and finite volatility.

The universe is a research input, not an investable index.

## Realized Volatility

Returns are log returns by default:

`r_t = log(P_t / P_{t-1})`

Annualized volatility:

`sigma_ann = std(r_t) * sqrt(252)`

Missing and non-numeric prices are coerced to `NaN` and dropped.

## Liquidity Score

The liquidity score is a first-pass liquidity diagnostic score. It combines rank-normalized:

- average traded value;
- average volume;
- number of trades;
- spread/spread proxy;
- volatility penalty.

It is not a perfect liquidity metric. Public data may omit full depth and venue-specific microstructure.

## Futures Basis

Basis:

`basis = futures_price - spot_price`

Basis percentage:

`basis_pct = basis / spot_price`

Annualized basis:

`annualized_basis = basis_pct * 365 / days_to_expiry`

Guardrails:

- expired contracts are excluded;
- invalid spot/futures prices return `NaN`;
- futures prices are normalized by `LOTVOLUME` when available;
- rich/fair/cheap classification is a carry screen, not an arbitrage signal.

## Options Surface

The options pipeline uses public FORTS fields such as `STRIKE`, `OPTIONTYPE`, `UNDERLYINGASSET`, `UNDERLYINGSETTLEPRICE` and settlement/last prices.

Calculated fields:

- option type;
- strike;
- expiration;
- underlying;
- moneyness;
- time to expiry;
- Black-Scholes implied volatility;
- delta, gamma, vega, theta.

IV is `NaN` when market price, spot, strike, time to expiry or solver conditions are invalid.

## Risk Engine

Risk estimates use historical daily returns from selected candle histories:

- historical VaR;
- historical CVaR;
- maximum drawdown;
- average pairwise correlation;
- simple stress scenario diagnostics.

Stress scenarios are not forecasts.

## Execution Simulator

Execution cost modeling includes:

- spread crossing;
- commission in basis points;
- square-root market impact proxy;
- fill rate assumptions for limit orders;
- simplified TWAP/VWAP schedules.

The simulator does not model queue position, full order book depth, hidden liquidity, broker routing or real order placement.

## Strategy Research

Strategy modules are research templates. They require:

- cost-aware backtesting;
- turnover checks;
- capacity analysis;
- walk-forward validation;
- failure analysis.

They are not trading signals and do not imply predictive performance.

