"""Black-Scholes option pricing, implied volatility, and Greeks."""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


def _valid_inputs(
    spot: float, strike: float, time_to_expiry: float, volatility: float
) -> bool:
    return spot > 0 and strike > 0 and time_to_expiry > 0 and volatility > 0


def _d1(
    spot: float, strike: float, time_to_expiry: float, rate: float, volatility: float
) -> float:
    return (np.log(spot / strike) + (rate + 0.5 * volatility**2) * time_to_expiry) / (
        volatility * np.sqrt(time_to_expiry)
    )


def _d2(
    spot: float, strike: float, time_to_expiry: float, rate: float, volatility: float
) -> float:
    return _d1(spot, strike, time_to_expiry, rate, volatility) - volatility * np.sqrt(
        time_to_expiry
    )


def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    option_type: str,
) -> float:
    """Price a European call or put with the Black-Scholes model."""

    if not _valid_inputs(spot, strike, time_to_expiry, volatility):
        return float("nan")
    opt = option_type.lower()
    d1_value = _d1(spot, strike, time_to_expiry, rate, volatility)
    d2_value = _d2(spot, strike, time_to_expiry, rate, volatility)
    discount = np.exp(-rate * time_to_expiry)
    if opt == "call":
        return float(spot * norm.cdf(d1_value) - strike * discount * norm.cdf(d2_value))
    if opt == "put":
        return float(
            strike * discount * norm.cdf(-d2_value) - spot * norm.cdf(-d1_value)
        )
    return float("nan")


def implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    option_type: str,
    initial_guess: float = 0.3,
) -> float:
    """Solve Black-Scholes implied volatility with a bounded root finder."""

    del initial_guess
    if market_price <= 0 or spot <= 0 or strike <= 0 or time_to_expiry <= 0:
        return float("nan")

    def objective(volatility: float) -> float:
        return (
            black_scholes_price(
                spot, strike, time_to_expiry, rate, volatility, option_type
            )
            - market_price
        )

    try:
        low, high = objective(1e-6), objective(5.0)
        if not np.isfinite(low) or not np.isfinite(high) or low * high > 0:
            return float("nan")
        return float(brentq(objective, 1e-6, 5.0, maxiter=100))
    except (ValueError, RuntimeError, OverflowError):
        return float("nan")


def delta(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    option_type: str,
) -> float:
    """Calculate Black-Scholes delta."""

    if not _valid_inputs(spot, strike, time_to_expiry, volatility):
        return float("nan")
    d1_value = _d1(spot, strike, time_to_expiry, rate, volatility)
    if option_type.lower() == "call":
        return float(norm.cdf(d1_value))
    if option_type.lower() == "put":
        return float(norm.cdf(d1_value) - 1)
    return float("nan")


def gamma(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    option_type: str | None = None,
) -> float:
    """Calculate Black-Scholes gamma."""

    del option_type
    if not _valid_inputs(spot, strike, time_to_expiry, volatility):
        return float("nan")
    d1_value = _d1(spot, strike, time_to_expiry, rate, volatility)
    return float(norm.pdf(d1_value) / (spot * volatility * np.sqrt(time_to_expiry)))


def vega(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    option_type: str | None = None,
) -> float:
    """Calculate Black-Scholes vega per 1.00 volatility point."""

    del option_type
    if not _valid_inputs(spot, strike, time_to_expiry, volatility):
        return float("nan")
    d1_value = _d1(spot, strike, time_to_expiry, rate, volatility)
    return float(spot * norm.pdf(d1_value) * np.sqrt(time_to_expiry))


def theta(
    spot: float,
    strike: float,
    time_to_expiry: float,
    rate: float,
    volatility: float,
    option_type: str,
) -> float:
    """Calculate annualized Black-Scholes theta."""

    if not _valid_inputs(spot, strike, time_to_expiry, volatility):
        return float("nan")
    opt = option_type.lower()
    d1_value = _d1(spot, strike, time_to_expiry, rate, volatility)
    d2_value = _d2(spot, strike, time_to_expiry, rate, volatility)
    first = -(spot * norm.pdf(d1_value) * volatility) / (2 * np.sqrt(time_to_expiry))
    discount = np.exp(-rate * time_to_expiry)
    if opt == "call":
        return float(first - rate * strike * discount * norm.cdf(d2_value))
    if opt == "put":
        return float(first + rate * strike * discount * norm.cdf(-d2_value))
    return float("nan")
