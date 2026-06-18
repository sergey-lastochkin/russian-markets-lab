import numpy as np

from russian_markets_lab.analytics.futures_basis import (
    annualized_basis,
    calculate_basis,
    calculate_basis_pct,
    classify_basis_signal,
)


def test_basis() -> None:
    assert calculate_basis(100, 105) == 5


def test_basis_pct() -> None:
    assert calculate_basis_pct(100, 105) == 0.05


def test_annualized_basis() -> None:
    assert np.isclose(annualized_basis(100, 105, 365), 0.05)


def test_rich_fair_cheap_classification() -> None:
    assert classify_basis_signal(-0.06) == "cheap"
    assert classify_basis_signal(0.0) == "fair"
    assert classify_basis_signal(0.06) == "rich"
    assert classify_basis_signal(float("nan")) == "unknown"
