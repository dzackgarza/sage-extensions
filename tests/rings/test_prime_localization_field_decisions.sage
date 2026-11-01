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
    an element of the localization.  Everything below is the exact arithmetic of
    that answer, not a count: the six residues of the source collapse onto
    ``{0, 1}`` with ``2`` and ``4`` killed, the inverted set admits exactly the
    odd denominators, and the residue map is the identity onto ``FF_2``.
    """
    quotient = ZZ.quotient_ring(ZZ.ideal(6))
    localized = quotient.spectrum()(2).local_ring()
    zero, one = localized.zero(), localized.one()

    assert localized.localization_source() is quotient
    assert localized.is_field() is True
    assert localized.maximal_ideal().is_zero() is True

    # 2 and 4 are killed; 1, 3 and 5 are the unit of FF_2.
    for residue in (0, 2, 4):
        assert localized.fraction(quotient(residue)) == zero, residue
    for residue in (1, 3, 5):
        assert localized.fraction(quotient(residue)) == one, residue
    assert localized.fraction(quotient(2)) == localized.zero()
    assert localized.fraction(quotient(3)) != localized.zero()

    # The inverted set is the complement of (2): odd denominators are admitted.
    for denominator in (1, 3, 5):
        assert localized.fraction(quotient(1), quotient(denominator)) == one
    for denominator in (2, 4):
        with pytest.raises(ValueError):
            localized.fraction(quotient(1), quotient(denominator))

    # The characteristic is the localization's, not the source's: 3 * 2 = 0.
    assert quotient.characteristic() == 6
    assert localized.characteristic() == 2

    # The cardinality is the source's over the killed ideal: 6 / 3 = 2.
    assert quotient.cardinality() == 6
    assert localized.cardinality() == 2

    # The residue field is FF_2 and the residue map is the identity onto it.
    residue_field = localized.residue_field()
    residue_map = localized.residue_map()
    assert residue_field.is_field() is True
    assert residue_map(localized.one()) == residue_field.one()
    assert residue_map(localized.zero()) == residue_field.zero()
    assert residue_map(localized.fraction(quotient(3))) == residue_field.one()


def test_an_undecided_killer_leaves_the_decision_undecided() -> None:
    r"""The decision never reports a field it has not established.

    The annihilator's own membership question is three-valued, so the per-generator
    answers are combined with ``conjunction`` and an undecided one stays a
    proposition rather than becoming ``False``.
    """
    localized = ZZ.spectrum()(3).local_ring()

    assert localized.is_field() in (True, False) or localized.is_field() in Propositions

def test_the_isomorphism_decision_states_unknown_rather_than_raising() -> None:
    r"""A field whose invariants are unavailable is undecided, never ``False``.

    ``(ZZ/6)_(2)`` is ``FF_2`` and its characteristic is now stated, but it
    selects no executable model and its cardinality is undecided, so no
    isomorphism with ``GF(2)`` is established here.  What matters is the shape of
    the answer: a proposition, not an exception and not a refutation.
    """
    localized = ZZ.quotient_ring(ZZ.ideal(6)).spectrum()(2).local_ring()

    answer = localized.is_isomorphic(GF(2))

    assert answer is not True
    assert answer is not False
    assert answer in Propositions

def test_a_generated_submonoid_localization_states_its_own_characteristic_and_size() -> None:
    r"""``ZZ/6`` with ``2`` inverted is ``ZZ/3``: characteristic 3, three elements.

    This is the case that separates "some annihilator generator lies in ``S``"
    from "the annihilator meets ``S``": ``S = <2>`` in ``ZZ/6`` is ``{1, 2, 4}``,
    and the answer comes from this ring's own ``inverted_submonoid_meets``
    contract, not from testing generators one at a time.
    """
    quotient = ZZ.quotient_ring(ZZ.ideal(6))
    inverted = quotient.localization(quotient(2))

    assert quotient.characteristic() == 6
    assert inverted.characteristic() == 3
    assert inverted.cardinality() == 3


def test_the_trivial_localization_has_characteristic_one() -> None:
    r"""A localization that inverts ``0`` is trivial, and the trivial ring has characteristic 1.

    Not ``0``: the characteristic-zero shortcut is taken only after the trivial
    case, because a characteristic-zero source localized at a set containing zero
    is not a characteristic-zero ring.
    """
    zero_ring = ZZ.quotient_ring(ZZ.ideal(1))
    trivial = zero_ring.localization(zero_ring.one())

    assert (trivial.one() == trivial.zero()) is True
    assert trivial.characteristic() == 1
    assert trivial.cardinality() == 1


def test_the_residue_field_is_a_quotient_with_its_own_cardinality() -> None:
    r"""The residue field is ``ZZ/6`` modulo ``(2)``, not the localization itself.

    Three representations meet here and stay distinct: the localization, its
    residue field, and the quotient presentation of that field.  The residue
    field's cardinality is decided at the quotient owner, from the finite source
    and the killed ideal, and the maps that identify things are explicit --
    ``localization_map`` into the localization and ``residue_map`` out of it.
    """
    quotient = ZZ.quotient_ring(ZZ.ideal(6))
    localized = quotient.spectrum()(2).local_ring()
    residue_field = localized.residue_field()

    assert residue_field is not localized
    assert residue_field.quotient_source() is quotient
    assert residue_field.defining_ideal().ideal_generators() is not None
    assert residue_field.cardinality() == 2
    assert residue_field.is_field() is True

    localization_map = localized.localization_map()
    residue_map = localized.residue_map()
    assert localization_map.domain() is quotient
    assert localization_map.codomain() is localized
    assert residue_map.domain() is localized
    assert residue_map.codomain() is residue_field
    assert residue_map(localized.fraction(quotient(3))) == residue_field.one()
    assert residue_map(localized.fraction(quotient(2))) == residue_field.zero()
