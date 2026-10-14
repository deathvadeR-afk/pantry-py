"""Restock calendar.

Rules of the shop:
  * A supplier delivers every N months on the same day of the month as the first delivery. When a month is too
    short for that day, the delivery falls on the last day of that month and later months go back to the usual day
    (a Jan 31 start delivers Feb 28, Mar 31, Apr 30, ...).
  * Deliveries never happen at the weekend: a Saturday or Sunday delivery moves to the following Monday.
"""

import calendar
from datetime import date, timedelta


def add_months(d: date, months: int) -> date:
    index = d.year * 12 + (d.month - 1) + months
    year, month = divmod(index, 12)
    month += 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def next_business_day(d: date) -> date:
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def restock_dates(start: date, every_months: int, count: int) -> list[date]:
    """The first `count` delivery dates, starting on `start`."""
    if every_months <= 0 or count <= 0:
        raise ValueError("every_months and count must be positive")
    nominal = [start]
    while len(nominal) < count:
        nominal.append(add_months(nominal[-1], every_months))
    return [next_business_day(d) for d in nominal]
