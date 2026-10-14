from decimal import Decimal as D

import pytest

from pantry.report import median, moving_average, sales_by_category, top_n


def test_median_of_an_odd_count():
    assert median([D("3.00"), D("1.00"), D("2.00")]) == D("2.00")


def test_median_of_one_value():
    assert median([D("5.50")]) == D("5.50")


def test_median_of_nothing_is_an_error():
    with pytest.raises(ValueError):
        median([])


def test_sales_by_category_adds_up_each_category():
    rows = [
        {"category": "food", "amount": D("2.50")},
        {"category": "produce", "amount": D("1.00")},
        {"category": "food", "amount": D("0.75")},
    ]
    assert sales_by_category(rows) == {"food": D("3.25"), "produce": D("1.00")}


def test_sales_by_category_of_nothing():
    assert sales_by_category([]) == {}


def test_top_n_biggest_first():
    totals = {"food": D("30"), "produce": D("10"), "household": D("20")}
    assert top_n(totals, 2) == [("food", D("30")), ("household", D("20"))]


def test_top_n_equal_totals_go_alphabetically():
    totals = {"zeta": D("10"), "alpha": D("10"), "mid": D("5")}
    assert top_n(totals, 2) == [("alpha", D("10")), ("zeta", D("10"))]


def test_moving_average():
    assert moving_average([D(1), D(2), D(3), D(4)], 2) == [D("1.50"), D("2.50"), D("3.50")]


def test_moving_average_window_longer_than_data():
    assert moving_average([D(1), D(2)], 3) == []
