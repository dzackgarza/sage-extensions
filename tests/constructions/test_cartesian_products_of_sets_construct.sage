r"""The Cartesian product of a three-point and two-point set has six elements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_cartesian_product() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    product = Sets().product((three, two))

    assert product in CartesianProductsOfSets()
    assert product.cardinality() == cardinal(6)
    assert product.factors().cardinality() == cardinal(2)
