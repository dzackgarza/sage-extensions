r"""The rational field carries the placement that names it.

``_rational_placements()`` documents ``QQ = Frac(ZZ)`` as the prime field of
characteristic 0, ordered, and the number field of degree one, but ``QQ`` is
constructed as the localization of ``ZZ`` at its nonzero elements and that
construction supplied none of those categories.  ``QQ in PrimeFields()`` was
False, and every guard of the form ``field in PrimeFields() and
field.characteristic() == 0`` rejected it -- the one in ``Lattices.O_plus``
among them.

These cases state the repaired condition itself rather than a suite's failure
count: the placement, the exact guard path, ordinary fractional arithmetic, and
fields that must *not* acquire the placement.
"""

from sage_extensions.all import AA, CountablyInfiniteSets, Lattices, OwnedNumberFields, PrimeFields, QQ, QQbar, ZZ


def test_the_rational_field_is_a_prime_field_of_characteristic_zero() -> None:
    assert QQ.characteristic() == 0
    assert QQ in PrimeFields()


def test_the_rational_field_carries_its_declared_ordered_number_field_placement() -> None:
    r"""The other categories ``_rational_placements()`` names are present too."""
    from sage_extensions.categories.rings.ring_foundation import OwnedOrderedRings

    assert QQ in OwnedOrderedRings()
    assert QQ in OwnedNumberFields()
    assert QQ in CountablyInfiniteSets()


def test_the_spinor_norm_guard_accepts_the_rational_field() -> None:
    r"""The exact path that rejected it: ``O_plus`` at the real place of ``Frac(ZZ)``."""
    plane = Lattices(ZZ)([[0, 1], [1, 0]])

    kernel = plane.O_plus()
    assert kernel.supergroup() is plane.O()
    assert plane.base_ring().fraction_field() in PrimeFields()


def test_ordinary_fractional_arithmetic_is_unchanged() -> None:
    third = QQ(1) / QQ(3)

    assert third + QQ(2) / QQ(3) == QQ.one()
    assert third * QQ(3) == QQ.one()
    assert QQ(2) / QQ(6) == third
    assert QQ.zero() / QQ(5) == QQ.zero()


def test_fields_that_are_not_prime_fields_do_not_acquire_the_placement() -> None:
    r"""Only the named prime field is placed there; the real algebraic numbers are not."""
    assert AA not in PrimeFields()
    assert QQbar not in PrimeFields()
    assert AA.characteristic() == 0
