from decimal import Decimal as D

import pytest

from pantry.money import allocate, round_money, to_decimal


def test_to_decimal_goes_through_text_not_float():
    assert to_decimal(0.1) == D("0.1")
    assert to_decimal(D("2.5")) == D("2.5")


def test_round_money_halves_go_up():
    assert round_money("0.125") == D("0.13")
    assert round_money("0.135") == D("0.14")
    assert round_money("2.675") == D("2.68")


def test_allocate_evenly():
    assert allocate(D("9.00"), [D(1), D(1), D(1)]) == [D("3.00"), D("3.00"), D("3.00")]


def test_allocate_leftover_cents_go_to_the_biggest_remainders():
    parts = allocate(D("10.00"), [D(1), D(1), D(1)])
    assert parts == [D("3.34"), D("3.33"), D("3.33")]
    assert sum(parts) == D("10.00")


def test_allocate_proportionally():
    assert allocate(D("1.00"), [D(1), D(3)]) == [D("0.25"), D("0.75")]


def test_allocate_needs_some_weight():
    with pytest.raises(ValueError):
        allocate(D("1.00"), [D(0), D(0)])
    assert allocate(D("1.00"), []) == []
