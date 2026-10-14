"""Sales reporting."""

from collections import defaultdict
from decimal import Decimal

from .money import round_money


def median(values: list[Decimal]) -> Decimal:
    """The middle value; for an even count, the average of the two middle values, rounded to the cent."""
    if not values:
        raise ValueError("median of nothing")
    ordered = sorted(values)
    mid = len(ordered) // 2
    return round_money(ordered[mid])


def sales_by_category(rows: list[dict]) -> dict[str, Decimal]:
    """Total per category. Each row: {"category": str, "amount": Decimal}."""
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for row in rows:
        totals[row["category"]] += row["amount"]
    return dict(totals)


def top_n(totals: dict[str, Decimal], n: int) -> list[tuple[str, Decimal]]:
    """The n biggest categories, biggest first; categories with equal totals are listed alphabetically."""
    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:n]


def moving_average(values: list[Decimal], window: int) -> list[Decimal]:
    """Average of each full window of `window` consecutive values, to the cent."""
    if window <= 0:
        raise ValueError("window must be positive")
    out = []
    for i in range(len(values) - window + 1):
        chunk = values[i : i + window]
        out.append(round_money(sum(chunk, Decimal(0)) / window))
    return out
