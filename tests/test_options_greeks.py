import numpy as np

from russian_markets_lab.analytics.options_greeks import (
    black_scholes_price,
    delta,
    gamma,
    implied_volatility,
)


def test_call_price_positive() -> None:
    price = black_scholes_price(100, 100, 1, 0.05, 0.2, "call")
    assert price > 0


def test_put_price_positive() -> None:
    price = black_scholes_price(100, 100, 1, 0.05, 0.2, "put")
    assert price > 0


def test_delta_range() -> None:
    call_delta = delta(100, 100, 1, 0.05, 0.2, "call")
    put_delta = delta(100, 100, 1, 0.05, 0.2, "put")
    assert 0 < call_delta < 1
    assert -1 < put_delta < 0


def test_gamma_positive() -> None:
    assert gamma(100, 100, 1, 0.05, 0.2) > 0


def test_implied_volatility_returns_finite_value() -> None:
    market_price = black_scholes_price(100, 100, 1, 0.05, 0.25, "call")
    iv = implied_volatility(market_price, 100, 100, 1, 0.05, "call")
    assert np.isfinite(iv)
    assert np.isclose(iv, 0.25, atol=1e-4)


def test_invalid_input_returns_nan() -> None:
    assert np.isnan(implied_volatility(-1, 100, 100, 1, 0.05, "call"))
