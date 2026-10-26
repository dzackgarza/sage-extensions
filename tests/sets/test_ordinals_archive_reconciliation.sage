from sage_extensions.all import *


def test_archive_natural_and_ordinary_ordinal_products_are_distinct() -> None:
    one = Ordinals().one()
    omega0 = omega(0)

    assert one * omega0 == omega0 * one
    assert one.ordinal_product(omega0) == omega0
    assert omega0.ordinal_product(one) == omega0

    two = Ordinals()(2)
    assert two * omega0 == omega0 * two
    assert two.ordinal_product(omega0) != omega0.ordinal_product(two)


def test_archive_ordinary_ordinal_power_retains_nonfinite_structure() -> None:
    omega0 = omega(0)
    exponent = Ordinals()(2)
    power = omega0.ordinal_power(exponent)

    assert power != omega0
    assert power.cardinality() == omega0.cardinality() ** exponent.cardinality()
