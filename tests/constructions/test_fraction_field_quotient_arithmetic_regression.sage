r"""Native QmodnZ arithmetic stays in the owned fraction-field quotient."""

from sage_extensions.all import FractionFieldQuotients, QQ, ZZ


def test_native_fraction_field_quotient_arithmetic_returns_owned_classes() -> None:
    quotient = FractionFieldQuotients(ZZ)(2)
    left = quotient(QQ(1) / 2)
    right = quotient(QQ(1) / 3)

    assert left + right == quotient(QQ(5) / 6)
    assert -left == quotient(-QQ(1) / 2)
    assert quotient.base_ring()(3) * left == quotient(QQ(3) / 2)
