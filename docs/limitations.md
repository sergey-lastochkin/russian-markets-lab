# Limitations

## Public Data Delay

MOEX ISS public endpoints can be delayed, sparse or temporarily unavailable. This project does not use paid real-time data.

## Order Book Depth

Full depth order book data is generally not available through delayed public endpoints. Spread and execution metrics are diagnostics, not guarantees.

## No Broker Execution

The project has no broker integration and cannot send real orders.

## No Investment Advice

Outputs are research diagnostics only. They are not trading recommendations, investment advice or performance promises.

## Survivorship and Selection Bias

Universe selection by current liquidity can introduce survivorship and selection bias. Historical constituents are not reconstructed.

## Cached Data Staleness

Raw and processed caches can become stale. Metadata sidecars should be checked before using outputs.

## Derivatives Mapping

Futures basis is calculated only where public FORTS `ASSETCODE` can be mapped to a TQBR spot ticker. Contract specifications, dividends, borrow and funding are simplified.

## Black-Scholes Limitations

Options analytics use simplified Black-Scholes assumptions. Russian rates, dividends, liquidity, exercise style and settlement conventions can materially affect IV and Greeks.

