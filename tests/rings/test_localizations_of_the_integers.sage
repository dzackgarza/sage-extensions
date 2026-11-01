r"""Localizations ``S^{-1}R`` of the integers and of ``Q[x]`` at finitely many elements.

``Z[1/2]`` is the ring of fractions ``a/2^k``: fractions are equal when they
cross-multiply to equal integers (``2/4 = 1/2``), the image of ``2`` is a unit,
the image of ``3`` is not, and ``1/3`` is not an element at all.  The inverted set
``{2^k}`` meets the ideal ``(2)`` and misses ``(3)``, so ``(2)`` extends to the unit
ideal and ``(3)`` does not.  Since ``2`` divides ``6``, the
universal property gives a map ``Z[1/2] -> Z[1/6]`` over ``Z``.  In ``Q[x, 1/x]``
the image of ``x`` is a unit and that of ``x + 1`` is not.  Inverting ``2`` in
``Z/6`` kills the idempotent ``3`` and leaves ``Z/3``.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_fractions_in_z_one_half_are_equal_when_they_cross_multiply() -> None:
    ring = ZZ.localization(ZZ(2))
    three_quarters = ring.fraction(ZZ(3), ZZ(4))

    assert three_quarters.numerator() == 3
    assert three_quarters.denominator() == 4
    assert three_quarters * ring(4) == ring(3)
    assert ring.fraction(ZZ(2), ZZ(4)) == ring.fraction(ZZ(1), ZZ(2))
    assert ring.fraction(ZZ(1), ZZ(2)) + ring.fraction(ZZ(1), ZZ(2)) == ring.one()
    assert ring(3) / ring(4) == three_quarters
    assert ring(3) - ring(5) == -ring(2)


def test_two_becomes_a_unit_and_three_does_not() -> None:
    ring = ZZ.localization(ZZ(2))

    assert ring(2).is_unit()
    assert ring(2).inverse_of_unit() == ring.fraction(ZZ(1), ZZ(2))
    assert not ring(3).is_unit()
    assert not ring(6).is_unit()
    assert QQ(1) / QQ(4) in ring
    assert QQ(1) / QQ(3) not in ring


def test_a_denominator_outside_the_inverted_set_is_refused() -> None:
    ring = ZZ.localization(ZZ(2))

    with pytest.raises(ValueError):
        ring.fraction(ZZ(1), ZZ(3))


def test_a_raw_sage_rational_denotes_its_own_fraction() -> None:
    r"""``QQ(1/2)`` is ``1/2``, not the source ring's rounding of it.

    A rational of Sage's own field is a value this session has not constructed,
    and ``ZZ(1/2)`` is ``0`` or ``1`` depending on the rounding, never ``1/2``.
    Reading such a value through the localization's source ring alone would
    therefore denote a different element, so the localization constructor splits
    it into its own numerator and denominator and admits the denominator through
    the selected submonoid.  A proper localization refuses a denominator it does
    not invert, which is the same admission decision ``fraction`` asks.
    """
    from sage.rings.integer_ring import ZZ as SageIntegers
    from sage.rings.rational_field import QQ as SageRationals

    def raw(numerator: int, denominator: int = 1):
        return SageRationals(SageIntegers(numerator)) / SageRationals(
            SageIntegers(denominator)
        )

    half = raw(1, 2)
    third = raw(1, 3)

    assert QQ(half) == QQ(1) / QQ(2)
    assert QQ(half) != QQ(1)
    assert QQ(half).denominator() == ZZ(2)
    assert QQ(third) == QQ(1) / QQ(3)
    assert QQ(raw(4, 2)) == QQ(2)

    ring = ZZ.localization(ZZ(2))
    assert ring(half) == ring.fraction(ZZ(1), ZZ(2))
    assert ring(raw(3, 4)) == ring.fraction(ZZ(3), ZZ(4))
    with pytest.raises(ValueError):
        ring(third)

    # The reverse comparison is Sage's answer, not this localization's: Sage's
    # own rational field does not admit an element of this session, so
    # ``half == QQ(half)`` stays ``False`` there.  Equality in the owned
    # universe is the direction stated above.
    assert QQ(half) == half


def test_the_localization_map_and_its_source() -> None:
    ring = ZZ.localization(ZZ(2))
    localization = ring.localization_map()

    assert ring.localization_source() is ZZ
    assert localization.domain() is ZZ
    assert localization(ZZ(5)) == ring(5)
    assert localization(ZZ(6)) == localization(ZZ(2)) * localization(ZZ(3))
    assert ring.inverted_element() == 2
    assert not ring.is_fraction_field_localization()


def test_the_inverted_powers_of_two_meet_the_ideal_two_and_miss_the_ideal_three() -> None:
    ring = ZZ.localization(ZZ(2))

    assert ring.inverted_submonoid_meets(ZZ.ideal(ZZ(2)))
    assert ring.inverted_submonoid_meets(ZZ.ideal(ZZ(4)))
    assert not ring.inverted_submonoid_meets(ZZ.ideal(ZZ(3)))


def test_inverting_two_factors_through_inverting_six() -> None:
    half = ZZ.localization(ZZ(2))
    sixth = ZZ.localization(ZZ(6))
    restriction = half.restriction_to(sixth)

    assert restriction.domain() is half
    assert restriction.codomain() is sixth
    assert restriction(half.fraction(ZZ(1), ZZ(2))) == sixth.fraction(ZZ(3), ZZ(6))
    assert restriction(half.localization_map()(ZZ(7))) == sixth.localization_map()(ZZ(7))


def test_x_becomes_a_unit_in_the_laurent_localization_of_q_x() -> None:
    line = QQ["x"]
    x = line.algebra_generator("x")
    laurent = line.localization(x)

    assert laurent(x).is_unit()
    assert laurent(x).inverse_of_unit() * laurent(x) == laurent.one()
    assert not laurent(x + 1).is_unit()


def test_inverting_two_in_z_mod_six_leaves_z_mod_three() -> None:
    ring = ZZ.ideal(ZZ(6)).quotient_ring()
    localized = ring.localization(ring(2))

    assert localized(ring(3)) == localized.zero()
    assert localized(ring(2)).is_unit()
    assert localized.characteristic() == 3
