"""Pricing a basket.

Rules of the shop:
  * Bulk discount per line: 10 or more units 5% off the line, 50 or more 10% off. The discount is rounded to the
    cent, halves up.
  * A coupon takes a percentage off the basket AFTER bulk discounts. Tax differs by category, so the coupon is
    shared across the lines in proportion to what each line is worth, and tax is worked out per line on what the
    line costs after its share of the coupon.
  * Tax per line is rounded to the cent, halves up.
"""

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal

from .money import CENT, allocate, round_money

TAX_RATES = {
    "produce": Decimal("0"),
    "food": Decimal("0.05"),
    "household": Decimal("0.18"),
}
DEFAULT_TAX_RATE = Decimal("0.12")

# (minimum units, discount rate), biggest first
BULK_TIERS = (
    (50, Decimal("0.10")),
    (10, Decimal("0.05")),
)


@dataclass(frozen=True)
class Line:
    sku: str
    category: str
    unit_price: Decimal
    quantity: int

    @property
    def gross(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Coupon:
    code: str
    percent: Decimal  # 10 means 10% off


@dataclass(frozen=True)
class Quote:
    subtotal: Decimal
    bulk_discount: Decimal
    coupon_discount: Decimal
    tax: Decimal
    total: Decimal


def bulk_rate(quantity: int) -> Decimal:
    for minimum, rate in BULK_TIERS:
        if quantity >= minimum:
            return rate
    return Decimal(0)


def bulk_discount(line: Line) -> Decimal:
    raw = line.gross * bulk_rate(line.quantity)
    return raw.quantize(CENT, rounding=ROUND_DOWN)


def line_net(line: Line) -> Decimal:
    return line.gross - bulk_discount(line)


def tax_rate(category: str) -> Decimal:
    return TAX_RATES.get(category, DEFAULT_TAX_RATE)


def quote(lines: list[Line], coupon: Coupon | None = None) -> Quote:
    nets = [line_net(line) for line in lines]
    subtotal = sum((line.gross for line in lines), Decimal(0))
    bulk_total = sum((bulk_discount(line) for line in lines), Decimal(0))
    net_total = sum(nets, Decimal(0))

    coupon_discount = Decimal(0)
    if coupon is not None and net_total > 0:
        coupon_discount = round_money(net_total * coupon.percent / 100)

    tax = sum(
        (round_money(net * tax_rate(line.category)) for line, net in zip(lines, nets)),
        Decimal(0),
    )
    total = net_total - coupon_discount + tax
    return Quote(
        subtotal=round_money(subtotal),
        bulk_discount=bulk_total,
        coupon_discount=coupon_discount,
        tax=tax,
        total=round_money(total),
    )


def split_coupon(nets: list[Decimal], coupon_discount: Decimal) -> list[Decimal]:
    """How much of the coupon each line carries (kept for the receipt printer)."""
    return allocate(coupon_discount, nets)
