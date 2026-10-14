from datetime import date

import pytest

from pantry.inventory import Batch, InsufficientStock, Inventory

TODAY = date(2026, 10, 1)


def make() -> Inventory:
    return Inventory(today=lambda: TODAY)


def test_available_adds_up_usable_batches():
    inv = make()
    inv.add_batch(Batch("a", "milk", 5, date(2026, 10, 5)))
    inv.add_batch(Batch("b", "milk", 7, date(2026, 10, 9)))
    inv.add_batch(Batch("c", "eggs", 12, date(2026, 10, 9)))
    assert inv.available("milk") == 12
    assert inv.available("eggs") == 12
    assert inv.available("flour") == 0


def test_a_batch_is_usable_on_its_expiry_date_but_not_after():
    inv = make()
    inv.add_batch(Batch("a", "milk", 5, date(2026, 10, 1)))
    assert inv.available("milk") == 5
    assert inv.available("milk", on=date(2026, 10, 2)) == 0


def test_consume_spans_batches_in_expiry_order():
    inv = make()
    inv.add_batch(Batch("a", "milk", 5, date(2026, 10, 5)))
    inv.add_batch(Batch("b", "milk", 10, date(2026, 10, 9)))
    assert inv.consume("milk", 8) == [("a", 5), ("b", 3)]
    assert inv.available("milk") == 7


def test_consume_stops_when_it_has_enough():
    inv = make()
    inv.add_batch(Batch("a", "milk", 5, date(2026, 10, 5)))
    inv.add_batch(Batch("b", "milk", 10, date(2026, 10, 9)))
    assert inv.consume("milk", 3) == [("a", 3)]


def test_consume_more_than_available_takes_nothing():
    inv = make()
    inv.add_batch(Batch("a", "milk", 5, date(2026, 10, 5)))
    with pytest.raises(InsufficientStock):
        inv.consume("milk", 6)
    assert inv.available("milk") == 5


def test_an_expired_batch_is_not_counted_or_used():
    inv = make()
    inv.add_batch(Batch("old", "milk", 4, date(2026, 9, 20)))
    inv.add_batch(Batch("new", "milk", 4, date(2026, 10, 9)))
    assert inv.available("milk") == 4
    assert inv.consume("milk", 4) == [("new", 4)]


def test_rejects_empty_batches_and_bad_quantities():
    inv = make()
    with pytest.raises(ValueError):
        inv.add_batch(Batch("a", "milk", 0, date(2026, 10, 5)))
    with pytest.raises(ValueError):
        inv.consume("milk", 0)


def test_expiring_before_lists_soonest_first():
    inv = make()
    inv.add_batch(Batch("late", "milk", 1, date(2026, 10, 20)))
    inv.add_batch(Batch("soon", "milk", 1, date(2026, 10, 3)))
    inv.add_batch(Batch("mid", "eggs", 1, date(2026, 10, 10)))
    assert [b.batch_id for b in inv.expiring_before(date(2026, 10, 15))] == ["soon", "mid"]
