r"""``Z[i]``, the ring of integers of ``Q(i)``.

``Z[i]`` has integral basis ``1, i``, is a Dedekind domain of Krull dimension one,
is maximal, and has fraction field ``Q(i)``; its discriminant is ``-4`` (LMFDB
2.0.4.1, checked 2026-09-24).  ``i`` is a unit and ``1 + i`` is not, but in
``Z[i][1/2]`` it becomes one, since ``(1 + i)(1 - i) = 2``.  ``2 = -i (1 + i)^2``
ramifies, so ``(1 + i)`` is a prime whose local ring is a discrete valuation ring
in which ``1 + i`` is not a unit and ``3`` is.  ``3`` is prime in ``Z[i]`` (it is
``3 mod 4``) and does not divide a power of ``2``, so it is not a unit of ``Z[i][1/2]``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_gaussian_integers_are_the_maximal_order_of_q_i() -> None:
    field = QuadraticField(-1)
    integers = field.ring_of_integers()
    i = integers(field.primitive_element())

    assert integers.is_maximal()
    assert integers.fraction_field() is field
    assert integers.krull_dimension() == 1
    assert integers.base_ring() is ZZ
    assert integers in OwnedRings().Commutative().DedekindDomains()
    assert integers not in OwnedRings().Commutative().NoZeroDivisors().PrincipalIdeals()
    assert "Order of rank 2" in repr(integers)
    hash(integers)
    assert i.is_unit()
    assert not (integers.one() + i).is_unit()


def test_a_nonmaximal_order_is_not_placed_in_dedekind_domains() -> None:
    field = QuadraticField(-1)
    nonmaximal = field.order_generated_by(2 * field.primitive_element())
    assert not nonmaximal.is_maximal()
    assert nonmaximal not in OwnedRings().Commutative().DedekindDomains()


def test_order_identity_and_dedekind_placement_do_not_depend_on_constructor_order() -> None:
    # First reach the maximal lattice through the generic order constructor.
    field = QuadraticField(-2)
    generic_order = field.order_generated_by(field.primitive_element())
    maximal_order = field.ring_of_integers()
    assert generic_order is maximal_order
    assert generic_order in OwnedRings().Commutative().DedekindDomains()

    # A distinct field exercises the reverse construction order.
    other_field = QuadraticField(-7)
    maximal_first = other_field.ring_of_integers()
    integral_generator = (other_field.one() + other_field.primitive_element()) / other_field(2)
    generic_after = other_field.order_generated_by(integral_generator)
    assert maximal_first is generic_after
    assert generic_after in OwnedRings().Commutative().DedekindDomains()


def test_one_plus_i_becomes_a_unit_after_inverting_two() -> None:
    field = QuadraticField(-1)
    integers = field.ring_of_integers()
    i = integers(field.primitive_element())
    localized = integers.localization(integers(2))

    assert localized(integers.one() + i).is_unit()
    assert localized(integers(2)).is_unit()


def test_the_discriminant_of_the_gaussian_integers_is_minus_four() -> None:
    assert QuadraticField(-1).ring_of_integers().discriminant() == -4


def test_the_local_ring_at_one_plus_i() -> None:
    field = QuadraticField(-1)
    integers = field.ring_of_integers()
    i = integers(field.primitive_element())
    local = integers.localize_at_prime(integers.ideal(integers.one() + i))

    assert integers.spectrum()(integers.ideal(integers.one() + i)).height() == 1

    assert not local(integers.one() + i).is_unit()
    assert local(integers(3)).is_unit()


def test_dedekind_ideal_colon_uses_fractional_ideal_inverses() -> None:
    integers = QuadraticField(-1).ring_of_integers()
    i = integers(QuadraticField(-1).primitive_element())
    ramified = integers.ideal(integers.one() + i)
    inert = integers.ideal(integers(3))
    fractional = integers.fractional_ideal(integers.one() + i)

    product = fractional * fractional.inverse()
    assert product == integers.fractional_ideal(integers.one())
    assert ramified.colon(ramified) == integers.ideal(integers.one())
    assert inert.colon(ramified) == inert
    assert inert.ideal_saturation(ramified) == inert
    assert ramified.ideal_saturation(ramified) == integers.ideal(integers.one())


def test_the_inert_prime_three_stays_a_nonunit_after_inverting_two() -> None:
    integers = QuadraticField(-1).ring_of_integers()
    localized = integers.localization(integers(2))

    assert not localized(integers(3)).is_unit()
