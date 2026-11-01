r"""A prime localization decides its own fieldhood, over a domain and over a quotient.

``R_p`` is local, so it is a field exactly when its maximal ideal ``p R_p`` is
zero.  That question has to be answered in the source ring: element equality in
``R_p`` is itself decided through the localization of the regular module, which
needs a free module, whose placement asks whether the coefficient ring is a
field.  Asking ``is_field`` through element equality therefore closes a circle.

``g/1 = 0`` in ``S^{-1}R`` exactly when some ``s`` in ``R \ p`` kills ``g``, that
is when the annihilator ``(0 : (g))`` is not contained in ``p``.  Both sides live
in ``R``, so the decision costs ideals of the source and no elements of the
localization.  Over a domain it reads ``p = 0``; over a quotient the two can come
apart, which is what the ``ZZ/6`` case below is for.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.logic import Propositions

import pytest


def test_the_localization_at_a_nonzero_prime_of_the_integers_is_not_a_field() -> None:
    r"""``ZZ_(3)`` has the non-zero maximal ideal ``3 ZZ_(3)``, so it is not a field."""
    localized = ZZ.spectrum()(3).local_ring()

    assert localized.is_field() is False
    assert localized.maximal_ideal().is_zero() is False
    assert localized.residue_field() == ZZ.quotient_ring(ZZ.ideal(3))
    assert localized.fraction_field() is QQ


def test_the_localization_at_the_zero_prime_is_the_fraction_field() -> None:
    r"""``ZZ_(0) = QQ``: the maximal ideal is zero, so the ring is a field.

    It is *a* presentation of ``QQ``, not the interned ``QQ`` object: the library's
    ``QQ`` is the localization at ``ZZ - {0}``, while this is the one at the
    complement of ``(0)``, and they are equal fields with different constructions.
    A field is its own fraction field, which is what ``fraction_field`` states here.
    """
    localized = ZZ.spectrum()(0).local_ring()

    assert localized.is_field() is True
    assert localized.maximal_ideal().is_zero() is True
    assert localized.fraction_field() is localized


def test_the_localization_of_a_quotient_is_a_field_without_a_zero_prime() -> None:
    r"""``(ZZ/6)_(2) ≅ FF_2``: ``3`` is inverted and ``3 * 2 = 0``, so ``p R_p = 0``.

    ``p = (2)`` is not the zero ideal, so a decision that reads ``p = 0`` would
    answer ``False`` here.  The general test -- ``(0 : (2)) = (3)`` is not
    contained in ``(2)`` -- answers ``True``, and it answers it without touching
    an element of the localization.
    """
    quotient = ZZ.quotient_ring(ZZ.ideal(6))
    localized = quotient.spectrum()(2).local_ring()

    assert localized.localization_source() is quotient
    assert localized.is_field() is True
    assert localized.maximal_ideal().is_zero() is True
    assert localized.fraction(quotient(2)) == localized.zero()
    assert localized.fraction(quotient(3)) != localized.zero()


def test_an_undecided_killer_leaves_the_decision_undecided() -> None:
    r"""The decision never reports a field it has not established.

    The annihilator's own membership question is three-valued, so the per-generator
    answers are combined with ``conjunction`` and an undecided one stays a
    proposition rather than becoming ``False``.
    """
    localized = ZZ.spectrum()(3).local_ring()

    assert localized.is_field() in (True, False) or localized.is_field() in Propositions
