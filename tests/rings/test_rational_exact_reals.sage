r"""An exact real that is rational is read as that rational, whatever radicals present it."""

from sage_extensions.all import *


def test_a_product_of_distinct_square_roots_that_is_rational_converts_to_qq() -> None:
    r"""``sqrt(6) sqrt(3) sqrt(2) = 6``, though the symbolic ring keeps the three roots apart."""
    value = RR(37) / 3 * RR(6).sqrt() * RR(3).sqrt() * RR(2).sqrt()

    assert value == RR(74)
    assert QQ(value) == QQ(74)
    assert ZZ(value) == ZZ(74)
