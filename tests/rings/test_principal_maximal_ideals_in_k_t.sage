r"""``(f)`` in ``k[t]`` is maximal exactly when ``f`` is irreducible.

``k[t]`` is a principal ideal domain, so ``k[t]/(f)`` is a field exactly when
``(f)`` is prime, and that holds exactly at the irreducible ``f``.  The ideal
therefore carries the ``Maximal`` placement, and the quotient inherits the
field and local placements from it — the quotient owner reads the *ideal's*
construction category and never asks the maximality predicate itself.

Before this rule, ``k[t]/(t)`` carried no placement at all and was neither a
field nor a local ring, although it is ``k`` itself.

Stated here for a finite coefficient field.  Over ``QQ`` the same theorem holds,
but the quotient of a one-variable polynomial ring by a maximal ideal is the
number-field construction, whose parent does not carry the class map from the
polynomial ring that a localization's residue map needs; that route has to gain
its map before the placement is stated for characteristic zero.
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


def test_an_irreducible_of_higher_degree_gives_the_finite_field_of_q_elements() -> None:
    r"""``t^2 + 2`` is irreducible over ``Z/5``, so the quotient is the field of ``5^2`` elements."""
    field, polynomial, t = _field_and_its_line()
    quotient = polynomial.quotient_ring(t**2 + 2)

    assert quotient in OwnedRings().Commutative().Local()
    assert int(quotient.cardinality()) == 25
