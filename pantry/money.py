"""Money helpers. All amounts are Decimal, in the shop's currency, to the cent."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_money(value) -> Decimal:
    """Round to the cent, halves away from zero (the shop's rule)."""
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def allocate(total: Decimal, weights: list[Decimal]) -> list[Decimal]:
    """Split `total` across `weights` in proportion, to the cent, so the parts add up to `total` exactly.

    Largest-remainder method: every part gets its floor share in cents, then the cents left over go one
    each to the parts with the biggest fractional remainder (ties: the earlier part first).
    """
    total = round_money(total)
    weight_sum = sum(weights, Decimal(0))
    if not weights:
        return []
    if weight_sum == 0:
        raise ValueError("weights must not all be zero")
    total_cents = int(total / CENT)
    exact = [Decimal(total_cents) * w / weight_sum for w in weights]
    floors = [int(e) for e in exact]
    leftover = total_cents - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - floors[i]), i))
    for i in order[:leftover]:
        floors[i] += 1
    return [Decimal(c) * CENT for c in floors]
