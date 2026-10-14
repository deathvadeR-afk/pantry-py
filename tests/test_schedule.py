from datetime import date

import pytest

from pantry.schedule import add_months, next_business_day, restock_dates


def test_add_months_keeps_the_day_when_it_fits():
    assert add_months(date(2026, 10, 15), 1) == date(2026, 11, 15)
    assert add_months(date(2026, 10, 15), 3) == date(2027, 1, 15)


def test_add_months_clamps_to_a_short_month():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2028, 1, 31), 1) == date(2028, 2, 29)


def test_next_business_day():
    assert next_business_day(date(2026, 10, 9)) == date(2026, 10, 9)  # Friday
    assert next_business_day(date(2026, 10, 10)) == date(2026, 10, 12)  # Saturday -> Monday
    assert next_business_day(date(2026, 10, 11)) == date(2026, 10, 12)  # Sunday -> Monday


def test_restock_dates_monthly_with_weekend_shift():
    # 15 Oct is a Thursday, 15 Nov a Sunday (moves to Monday the 16th), 15 Dec a Tuesday
    assert restock_dates(date(2026, 10, 15), 1, 3) == [date(2026, 10, 15), date(2026, 11, 16), date(2026, 12, 15)]


def test_restock_dates_every_few_months():
    assert restock_dates(date(2026, 10, 15), 3, 2) == [date(2026, 10, 15), date(2027, 1, 15)]


def test_restock_dates_one_delivery():
    assert restock_dates(date(2026, 10, 15), 1, 1) == [date(2026, 10, 15)]


def test_restock_dates_rejects_nonsense():
    with pytest.raises(ValueError):
        restock_dates(date(2026, 10, 15), 0, 3)
    with pytest.raises(ValueError):
        restock_dates(date(2026, 10, 15), 1, 0)
