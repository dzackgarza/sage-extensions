r"""Restriction between localizations, and its composition.

Localization is universal among maps out of ``R`` inverting a set of scalars,
so for ``S`` inside ``T`` there is exactly one map ``S^{-1}R -> T^{-1}R`` over
``R``.  Uniqueness makes these maps compose, which is the cocycle condition an
affine cover needs before any sheaf is glued on it.  Localizing a module along
the same restriction gives the map from a section to its restriction, and at a
prime to its germ.
"""

from sage_extensions.all import *


def test_localization_restrictions_compose_along_a_chain_of_inverted_scalars() -> None:
    inverted_two = ZZ.localization(2)
    inverted_six = ZZ.localization(2, 3)
    inverted_thirty = ZZ.localization(2, 3, 5)

    step = inverted_two.restriction_to(inverted_six)
    rest = inverted_six.restriction_to(inverted_thirty)
    whole = inverted_two.restriction_to(inverted_thirty)
    element = inverted_two(1) / 2

    assert rest(step(element)) == whole(element)
    assert rest * step == whole


def test_localization_source_map_determines_ring_morphism_equality() -> None:
    polynomial = QQ.polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    away_from_x = polynomial.localization(x)

    induced_identity = away_from_x.induced_morphism(away_from_x.localization_map())

    assert induced_identity == away_from_x.Mor(away_from_x).identity()


def test_a_localization_restricts_into_a_prime_localization_as_a_germ() -> None:
    polynomial = QQ.polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    away_from_x = polynomial.localization(x)
    at_x_minus_one = polynomial.localize_at_prime(polynomial.ideal(x - 1))

    germ = away_from_x.restriction_to(at_x_minus_one)

    assert germ.codomain() is at_x_minus_one
    assert germ(away_from_x(1) / x) == at_x_minus_one(1) / at_x_minus_one(x)
