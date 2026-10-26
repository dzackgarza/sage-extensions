r"""The residue rings ``Z/nZ`` built as quotients by ideals of the integers.

By the Chinese remainder theorem ``Z/6 = F_2 x F_3``: it is finite of cardinality 6
and characteristic 6, reduced, zero-dimensional, neither a field nor a domain, has
exactly the two minimal primes ``(2)`` and ``(3)``, and its units are the residues
prime to 6, with ``5^2 = 1``.  ``Z/7`` is a field, so ``3 * 5 = 1`` there.  ``Z/12``
is not reduced, since ``6^2 = 0``; the radical of ``(12)`` is ``(6)``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_six_is_a_finite_zero_dimensional_ring_that_is_not_a_domain() -> None:
    ring = ZZ.ideal(ZZ(6)).quotient_ring()

    assert ring.is_finite()
    assert not ring.is_field()
    assert not ring.is_integral_domain()
    assert ring.krull_dimension() == 0
    assert ring.is_reduced()


def test_z_mod_six_has_six_elements() -> None:
    assert ZZ.ideal(ZZ(6)).quotient_ring().cardinality() == 6


def test_z_mod_six_has_characteristic_six() -> None:
    assert ZZ.ideal(ZZ(6)).quotient_ring().characteristic() == 6


def test_the_units_of_z_mod_six_are_the_residues_prime_to_six() -> None:
    ring = ZZ.ideal(ZZ(6)).quotient_ring()

    assert ring(5).is_unit()
    assert ring(5).inverse_of_unit() == ring(5)
    assert ring(5) * ring(5) == ring.one()
    assert not ring(2).is_unit()
    assert not ring(3).is_unit()
    assert ring(2) * ring(3) == ring.zero()


def test_the_quotient_map_reduces_integers_modulo_six() -> None:
    ideal = ZZ.ideal(ZZ(6))
    ring = ideal.quotient_ring()
    reduction = ring.quotient_map()

    assert ring.quotient_source() is ZZ
    assert ring.defining_ideal() == ideal
    assert reduction(ZZ(8)) == ring(2)
    assert reduction(ZZ(-1)) == ring(5)
    assert reduction(ZZ(8) * ZZ(5)) == reduction(ZZ(8)) * reduction(ZZ(5))
    assert ring(3).lift() - ZZ(3) in ideal


def test_z_mod_six_has_the_two_minimal_primes_two_and_three() -> None:
    ring = ZZ.ideal(ZZ(6)).quotient_ring()

    assert ring.minimal_primes().cardinality() == 2
    assert ring.irreducible_components().cardinality() == 2


def test_a_product_of_fields_is_normal() -> None:
    assert ZZ.ideal(ZZ(6)).quotient_ring().is_normal()


def test_z_mod_seven_is_a_field() -> None:
    field = ZZ.ideal(ZZ(7)).quotient_ring()

    assert field.is_field()
    assert field.is_integral_domain()
    assert field.krull_dimension() == 0
    assert field(3).inverse_of_unit() == field(5)


def test_z_mod_twelve_is_not_reduced_and_twelve_has_radical_six() -> None:
    ring = ZZ.ideal(ZZ(12)).quotient_ring()

    assert not ring.is_reduced()
    assert ring(6) * ring(6) == ring.zero()
    assert ZZ.ideal(ZZ(12)).radical() == ZZ.ideal(ZZ(6))
    assert not ZZ.ideal(ZZ(12)).is_prime()
    assert ZZ.ideal(ZZ(7)).is_prime()
    assert ZZ.ideal(ZZ(7)).is_maximal()
