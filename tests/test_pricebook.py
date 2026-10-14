from decimal import Decimal as D

import pytest

from pantry.pricebook import PriceBook, UnknownPrice


def test_price_lookup():
    book = PriceBook()
    book.set_price("rice", "USD", "2.50")
    assert book.price("rice") == D("2.50")


def test_unknown_price_raises():
    book = PriceBook()
    with pytest.raises(UnknownPrice):
        book.price("rice")


def test_the_second_lookup_is_served_from_the_cache():
    book = PriceBook()
    book.set_price("rice", "USD", "2.50")
    book.price("rice")
    book.price("rice")
    assert book.lookups == 1


def test_changing_a_price_replaces_the_cached_one():
    book = PriceBook()
    book.set_price("rice", "USD", "2.50")
    assert book.price("rice") == D("2.50")
    book.set_price("rice", "USD", "2.75")
    assert book.price("rice") == D("2.75")


def test_prices_are_rounded_to_the_cent():
    book = PriceBook()
    book.set_price("tea", "USD", "1.005")
    assert book.price("tea") == D("1.01")
