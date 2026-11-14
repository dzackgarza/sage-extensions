r"""A localization's characteristic is decided in the source and answers in ``ZZ``.

``n * 1`` vanishes in ``S^{-1}R`` exactly when some ``s`` in ``S`` kills
``n * 1`` in ``R``, so the answer is the least divisor of the source's
characteristic with that property: ``(Z/6)[1/2]`` has characteristic 3, not 6.

The decision compares the source's characteristic with **zero in ``ZZ``**.  It
used to compare it with ``source.zero()`` — an element of the source ring — and
in ``Z/6`` the integer ``6`` *is* that zero, so the code took a
"characteristic zero source" branch and answered undecided for a localization
whose characteristic is 3.  The comparison is invisible until the scalar tower
reaches the quotient ring, which is what these tests hold in place.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_inverting_two_in_z_mod_six_leaves_z_mod_three() -> None:
    r"""``3`` is a unit after inverting ``2``, so ``3`` kills a multiple of one."""
    ring = ZZ.ideal(ZZ(6)).quotient_ring()
    localized = ring.localization(ring(2))

    assert localized(ring(3)) == localized.zero()
    assert localized(ring(2)).is_unit()
    assert localized.characteristic() == 3


def test_inverting_three_in_z_mod_six_leaves_z_mod_two() -> None:
    r"""The other idempotent: ``2`` is killed once ``3`` is inverted."""
    ring = ZZ.ideal(ZZ(6)).quotient_ring()
    localized = ring.localization(ring(3))

    assert localized(ring(2)) == localized.zero()
    assert localized.characteristic() == 2


def test_a_characteristic_zero_localization_still_answers_zero() -> None:
    r"""``Z[1/2]`` is a domain, so its localization map is injective: characteristic 0."""
    assert ZZ.localization(ZZ(2)).characteristic() == ZZ.zero()
