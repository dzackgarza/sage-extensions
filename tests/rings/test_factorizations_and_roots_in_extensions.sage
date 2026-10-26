r"""Factorizations with their multiplicities, and roots in an extension field.

``360 = 2^3 * 3^2 * 5`` and ``x^4 - 1 = (x - 1)(x + 1)(x^2 + 1)`` over ``Q``, each
factor simple.  ``x^2 - 2`` has no rational root but splits in ``Q(sqrt 2)`` with the
two simple roots ``+- sqrt 2``.  ``Z`` and ``Q`` are countably infinite of
characteristic zero; ``Q`` is a field and ``Z`` a domain that is not; the units of
``Z`` are ``+- 1``; a commutative ring is its own centre.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_multiplicities_of_the_prime_factorization_of_three_hundred_sixty() -> None:
    factorization = ZZ(360).factor()
    multiplicities = dict(factorization.items())

    assert factorization.parent_ring() is ZZ
    assert multiplicities == {ZZ(2): 3, ZZ(3): 2, ZZ(5): 1}


def test_x_to_the_fourth_minus_one_factors_into_three_simple_factors_over_q() -> None:
    x = QQ["x"].algebra_generator("x")
    polynomial = x**4 - 1
    multiplicities = dict(polynomial.factor().items())

    assert polynomial.factor().reconstruct() == polynomial
    assert x**2 + 1 in multiplicities
    assert x - 1 in multiplicities
    assert x + 1 in multiplicities


def test_x_squared_minus_two_splits_in_q_root_two() -> None:
    x = QQ["x"].algebra_generator("x")
    field = QuadraticField(2)
    roots = dict((x**2 - 2).roots(field).items())

    assert all(root * root == 2 for root in roots)
    assert field.primitive_element() in roots
    assert -field.primitive_element() in roots


def test_the_integers_and_the_rationals() -> None:
    assert ZZ.cardinality() == aleph0
    assert QQ.cardinality() == aleph0
    assert QQ.is_field()
    assert not ZZ.is_field()
    assert ZZ.is_integral_domain()
    assert ZZ(-1).is_unit()
    assert not ZZ(2).is_unit()
    assert QQ(3).is_unit()
    assert not QQ(0).is_unit()
    assert ZZ.ring_center() is ZZ


def test_the_integers_and_the_rationals_have_characteristic_zero() -> None:
    assert ZZ.characteristic() == 0
    assert QQ.characteristic() == 0


def test_the_factors_of_x_to_the_fourth_minus_one_and_the_roots_of_x_squared_minus_two_are_simple() -> None:
    x = QQ["x"].algebra_generator("x")

    assert set(dict((x**4 - 1).factor().items()).values()) == {1}
    assert set(dict((x**2 - 2).roots(QuadraticField(2)).items()).values()) == {1}
