"""Maximal ideals in ZZ and QQ[x], including their construction routes.

The quotient ZZ/(5) is F_5. Over QQ, x^2 + 1 is irreducible because
its roots are not rational; its principal ideal in QQ[x] is maximal.
"""

from sage_extensions.categories.rings.commutative_ideals import CommutativeIdeals
from sage_extensions.categories.rings.ring_foundation import (
    OwnedRings,
    _owned_integers,
    _owned_rationals,
)


def test_prime_and_maximal_ideal_construction() -> None:
    integers = _owned_integers()
    maximal = CommutativeIdeals(integers).Maximal()
    placed = maximal(5)
    routed = integers.ideal(5)
    assert placed in maximal
    assert routed in maximal
    assert placed.is_prime() is True
    assert integers.quotient_ring(routed) is integers.quotient_ring(placed)

    polynomial = _owned_rationals().polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    ideal = polynomial.ideal(x * x + polynomial(1))
    placement = ideal.category()
    assert ideal in CommutativeIdeals(polynomial).Maximal()
    assert ideal.category() is placement


def test_quotient_field_query_preserves_construction_placement() -> None:
    polynomial = _owned_rationals().polynomial_ring("t")
    t = polynomial.algebra_generator("t")
    ideal = polynomial.ideal(t * t + polynomial(1))
    quotient = polynomial.quotient_ring(ideal)
    placement = quotient.category()
    assert quotient in OwnedRings().Division()
    assert quotient.category() is placement
    maximal = CommutativeIdeals(polynomial).Maximal()(t * t + polynomial(1))
    assert polynomial.residue_field_at(maximal) in OwnedRings().Division()


def test_residue_field_construction_from_maximal_ideal() -> None:
    polynomial = _owned_rationals().polynomial_ring("s")
    s = polynomial.algebra_generator("s")
    maximal = CommutativeIdeals(polynomial).Maximal()(s * s + polynomial(1))
    assert polynomial.residue_field_at(maximal) in OwnedRings().Division()
