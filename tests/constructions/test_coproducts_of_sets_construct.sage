r"""The coproduct of a three-point and two-point set has five tagged elements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_set_coproduct() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    coproduct = Sets().coproduct((three, two))

    assert coproduct in CoproductsOfSets()
    assert coproduct.cardinality() == cardinal(5)
    assert coproduct.factors().cardinality() == cardinal(2)
