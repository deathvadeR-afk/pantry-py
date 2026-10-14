"""Price list in several currencies, with a lookup cache (the till asks for the same prices all day)."""

from decimal import Decimal

from .money import round_money


class UnknownPrice(KeyError):
    pass


class PriceBook:
    def __init__(self):
        self._prices: dict[tuple[str, str], Decimal] = {}
        self._cache: dict[str, Decimal] = {}
        self.lookups = 0  # how many times the underlying table was read (the cache saves these)

    def set_price(self, sku: str, currency: str, amount) -> None:
        self._prices[(sku, currency)] = round_money(amount)
        self._cache.pop(sku, None)

    def price(self, sku: str, currency: str = "USD") -> Decimal:
        if sku in self._cache:
            return self._cache[sku]
        self.lookups += 1
        try:
            value = self._prices[(sku, currency)]
        except KeyError:
            raise UnknownPrice(f"{sku} has no {currency} price") from None
        self._cache[sku] = value
        return value
