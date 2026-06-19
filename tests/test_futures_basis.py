import numpy as np

from russian_markets_lab.analytics.futures_basis import (
    annualized_basis,
    calculate_basis,
    calculate_basis_pct,
    classify_basis_confidence,
    classify_basis_signal,
)


def test_basis() -> None:
    assert calculate_basis(100, 105) == 5
    assert np.isnan(calculate_basis(0, 105))
    assert np.isnan(calculate_basis(100, 0))


def test_basis_pct() -> None:
    assert calculate_basis_pct(100, 105) == 0.05
    assert np.isnan(calculate_basis_pct(0, 105))


def test_annualized_basis() -> None:
    assert np.isclose(annualized_basis(100, 105, 365), 0.05)
    assert np.isnan(annualized_basis(100, 105, 0))
    assert np.isnan(annualized_basis(100, 105, -1))


def test_rich_fair_cheap_classification() -> None:
    assert classify_basis_signal(-0.06) == "cheap"
    assert classify_basis_signal(0.0) == "fair"
    assert classify_basis_signal(0.06) == "rich"
    assert classify_basis_signal(float("nan")) == "unknown"


def test_basis_confidence_classification() -> None:
    assert classify_basis_confidence(100, 105, 30, 1000, 500) == "high"
    assert classify_basis_confidence(100, 105, 30, 1000, 0) == "medium"
    assert classify_basis_confidence(100, 105, 30, 0, 0) == "low"
    assert classify_basis_confidence(0, 105, 30, 1000, 500) == "unknown"
    assert classify_basis_confidence(100, 105, 0, 1000, 500) == "unknown"
