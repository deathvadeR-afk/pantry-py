from decimal import Decimal as D

from pantry.pricing import Coupon, Line, bulk_discount, bulk_rate, line_net, quote, split_coupon, tax_rate


def test_bulk_rate_tiers():
    assert bulk_rate(1) == D(0)
    assert bulk_rate(9) == D(0)
    assert bulk_rate(10) == D("0.05")
    assert bulk_rate(49) == D("0.05")
    assert bulk_rate(50) == D("0.10")
    assert bulk_rate(500) == D("0.10")


def test_bulk_discount_on_a_round_amount():
    line = Line("rice", "food", D("2.00"), 10)
    assert bulk_discount(line) == D("1.00")
    assert line_net(line) == D("19.00")


def test_no_discount_below_the_first_tier():
    line = Line("rice", "food", D("2.50"), 9)
    assert bulk_discount(line) == D("0.00")
    assert line_net(line) == D("22.50")


def test_tax_rates_by_category():
    assert tax_rate("produce") == D(0)
    assert tax_rate("food") == D("0.05")
    assert tax_rate("household") == D("0.18")
    assert tax_rate("toys") == D("0.12")


def test_quote_of_nothing_is_zero():
    q = quote([])
    assert (q.subtotal, q.bulk_discount, q.coupon_discount, q.tax, q.total) == (D(0), D(0), D(0), D(0), D(0))


def test_quote_with_bulk_discount_and_tax():
    q = quote([Line("rice", "food", D("2.00"), 10)])
    assert q.subtotal == D("20.00")
    assert q.bulk_discount == D("1.00")
    assert q.tax == D("0.95")
    assert q.total == D("19.95")


def test_tax_rounds_halves_up():
    # 10.10 at 5% is 0.505, which the shop rounds up to 0.51
    q = quote([Line("tea", "food", D("10.10"), 1)])
    assert q.tax == D("0.51")
    assert q.total == D("10.61")


def test_coupon_on_tax_free_produce():
    q = quote([Line("apple", "produce", D("4.00"), 3)], Coupon("TEN", D(10)))
    assert q.coupon_discount == D("1.20")
    assert q.total == D("10.80")


def test_coupon_is_taken_after_bulk_discount():
    q = quote([Line("apple", "produce", D("2.00"), 10)], Coupon("TEN", D(10)))
    # 20.00 less 1.00 bulk is 19.00; ten percent of that is 1.90
    assert q.coupon_discount == D("1.90")
    assert q.total == D("17.10")


def test_coupon_does_nothing_to_an_empty_basket():
    assert quote([], Coupon("TEN", D(10))).coupon_discount == D(0)


def test_split_coupon_shares_add_up():
    shares = split_coupon([D("10.00"), D("20.00"), D("30.00")], D("6.00"))
    assert shares == [D("1.00"), D("2.00"), D("3.00")]
    assert sum(shares) == D("6.00")
