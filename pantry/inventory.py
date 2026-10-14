"""Stock held in batches that expire.

Rules of the shop:
  * Stock is held in batches, each with its own expiry date. A batch is usable up to and including its expiry date.
  * When stock is taken, the batch that expires first is used first (so nothing is thrown away that could have been
    sold), and an expired batch is never used.
  * Taking more than is available takes nothing at all and raises InsufficientStock.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date


class InsufficientStock(Exception):
    pass


@dataclass
class Batch:
    batch_id: str
    sku: str
    quantity: int
    expires: date


class Inventory:
    def __init__(self, today: Callable[[], date] = date.today):
        self._today = today
        self._batches: list[Batch] = []

    def add_batch(self, batch: Batch) -> None:
        if batch.quantity <= 0:
            raise ValueError("a batch needs a positive quantity")
        self._batches.append(batch)

    def _usable(self, sku: str, on: date) -> list[Batch]:
        return [b for b in self._batches if b.sku == sku and b.quantity > 0 and b.expires >= on]

    def available(self, sku: str, on: date | None = None) -> int:
        on = on or self._today()
        return sum(b.quantity for b in self._usable(sku, on))

    def consume(self, sku: str, quantity: int, on: date | None = None) -> list[tuple[str, int]]:
        """Take `quantity` units of `sku`. Returns [(batch_id, units_taken), ...] in the order they were taken."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        on = on or self._today()
        if self.available(sku, on) < quantity:
            raise InsufficientStock(f"only {self.available(sku, on)} of {sku} available")
        taken: list[tuple[str, int]] = []
        remaining = quantity
        for batch in self._usable(sku, on):
            if remaining == 0:
                break
            use = min(batch.quantity, remaining)
            batch.quantity -= use
            remaining -= use
            taken.append((batch.batch_id, use))
        return taken

    def expiring_before(self, cutoff: date) -> list[Batch]:
        return sorted((b for b in self._batches if b.quantity > 0 and b.expires < cutoff), key=lambda b: b.expires)
