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

The liquidity score is a first-pass liquidity diagnostic score. It is relative to the
current processed dataset and should be read as a screening tool, not as a perfect
measure of executable liquidity.

The score combines rank-normalized components:

- average traded value;
- average volume;
- number of trades;
- quoted or reported spread when available;
- volatility penalty;
- data quality component.

Quoted spread is calculated as:

`spread = ask - bid`

`spread_bps = (ask - bid) / mid * 10000`

If bid/ask are missing, the dashboard labels the spread as unavailable instead of
presenting a fabricated quote. A high-low or close-to-close proxy may be used in
research functions, but it must be labelled as a proxy.

Amihud illiquidity is calculated as:

`mean(abs(return) / traded_value)`

Rows with zero, negative or missing traded value are excluded from the calculation.

Liquidity regimes are conservative labels:

- `liquid`;
- `watch`;
- `illiquid`;
- `insufficient_data`.

Limitations:

- MOEX ISS public data can be delayed;
- full order book depth is not available in every public endpoint;
- spread can be missing or only approximated;
- liquidity can change intraday;
- the score is relative to the current dataset and should not be compared blindly across runs.

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

The basis screen also assigns a confidence label:

- `high`: valid prices, valid expiry, positive time to expiry and both volume and open interest are available;
- `medium`: valid prices and expiry, with partial liquidity fields;
- `low`: valid prices and expiry, but weak liquidity fields;
- `unknown`: invalid or missing core inputs.

Limitations:

- the model does not include a full funding, dividend or repo curve;
- underlying mapping is best effort and may be incomplete;
- public/delayed data can be stale;
- liquidity fields matter for interpretation;
- a basis deviation does not imply executable arbitrage.

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
- annualized volatility;
- maximum drawdown;
- average pairwise correlation;
- simple stress scenario diagnostics.

The risk summary table includes the method, sample window and limitation note for
each metric. Historical VaR is the positive loss at the historical 5th percentile
for 95% confidence. CVaR is the average loss beyond that cutoff.

Risk contribution is a simple covariance-based approximation:

`contribution_i = weight_i * (Cov * weights)_i / portfolio_variance`

It is useful for orientation, but it is not a full factor risk model.

Stress scenarios are simplified shocks such as broad equity selloff, FX shock,
single-name gap, rates shock and volatility shock. They are diagnostics, not
forecasts.

Limitations:

- historical risk is backward-looking;
- no full margin model is implemented;
- no liquidation or order book impact model is included;
- scenario shocks are deliberately simplified;
- estimates can change materially with the selected universe and history window.

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
