r"""``(f)`` in ``k[t]`` is maximal exactly when ``f`` is irreducible.

``k[t]`` is a principal ideal domain, so ``k[t]/(f)`` is a field exactly when
``(f)`` is prime, and that holds exactly at the irreducible ``f``.  The ideal
therefore carries the ``Maximal`` placement, and the quotient inherits the
field and local placements from it — the quotient owner reads the *ideal's*
construction category and never asks the maximality predicate itself.

Before this rule, ``k[t]/(t)`` carried no placement at all and was neither a
field nor a local ring, although it is ``k`` itself.

The theorem holds for every field.  Over ``QQ`` the quotient of a one-variable
polynomial ring by a maximal ideal is the *number-field* construction, which
retained its quotient map only on the labelled generating set; it now states the
class map ``QQ[t] -> QQ[t]/(f)`` that a localization's residue map composes with,
so the placement reaches characteristic zero too.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _field_and_its_line():
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    return field, polynomial, polynomial.algebra_generator("t")


def test_a_quotient_by_an_irreducible_generator_is_a_field() -> None:
    r"""``(Z/5)[t]/(t)`` is ``Z/5``: a field, a local ring, five elements."""
    field, polynomial, t = _field_and_its_line()
    residue = polynomial.quotient_ring(t)

    assert residue in OwnedRings().Commutative().Local()
    assert residue in OwnedRings().Division().Commutative()
    assert int(residue.cardinality()) == 5


def test_a_quotient_by_a_reducible_generator_is_not_placed() -> None:
    r"""``t(t+1)`` is reducible, so ``(t^2 + t)`` is not maximal and nothing is claimed."""
    field, polynomial, t = _field_and_its_line()
    quotient = polynomial.quotient_ring(t**2 + t)

    assert quotient not in OwnedRings().Commutative().Local()
    assert quotient not in OwnedRings().Division().Commutative()


def test_over_the_rationals_an_irreducible_generator_gives_the_number_field() -> None:
    r"""``QQ[t]/(t^2 - 2)`` is a field, and its class map sends ``t`` to ``sqrt 2``.

    The quotient is the number-field construction, so this also states the class
    map that construction retains: ``t |-> theta``, with ``theta^2 = 2``.
    """
    polynomial = QQ.polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    field = polynomial.quotient_ring(x**2 - 2)

    assert field in OwnedRings().Division().Commutative()
    quotient_map = field.quotient_map()
    assert quotient_map.domain() is polynomial
    assert quotient_map.codomain() is field
    assert quotient_map(x) == field.algebra_generator("x")
    assert quotient_map(x**2) == field(QQ(2))


def test_over_the_rationals_a_reducible_generator_is_still_not_placed() -> None:
    r"""``t^2 - 1`` splits over ``QQ``, so ``(t^2 - 1)`` is not maximal."""
    polynomial = QQ.polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    quotient = polynomial.quotient_ring(x**2 - 1)

    assert quotient not in OwnedRings().Division().Commutative()


def test_an_irreducible_of_higher_degree_gives_the_finite_field_of_q_elements() -> None:
    r"""``t^2 + 2`` is irreducible over ``Z/5``, so the quotient is the field of ``5^2`` elements."""
    field, polynomial, t = _field_and_its_line()
    quotient = polynomial.quotient_ring(t**2 + 2)

    assert quotient in OwnedRings().Commutative().Local()
    assert int(quotient.cardinality()) == 25
