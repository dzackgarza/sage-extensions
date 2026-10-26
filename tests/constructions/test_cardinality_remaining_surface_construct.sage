r"""Cardinals expose their finite values, expressions, countability, and thin-category identities."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_and_infinite_cardinal_remaining_surface() -> None:
    three = cardinal(3)

    assert three.cardinality() is three
    assert three.finite_value() == 3
    assert Cardinalities().from_expression(three.expression()) == three
    assert three.is_finite()
    assert three.is_countable()
    assert not three.is_uncountable()
    assert aleph0.is_countable()
    assert continuum.is_uncountable()


def test_cardinality_identity_morphism_is_identity() -> None:
    three = cardinal(3)
    identity = three.Mor(three).unique_morphism()

    assert identity.is_identity()
