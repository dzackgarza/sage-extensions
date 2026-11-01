r"""When are two fractions equal in a localization?

``a/s = b/t`` in ``S^{-1}R`` exactly when some ``u`` in ``S`` kills
``a t - b s`` in ``R`` (Mathlib ``IsLocalization.eq_iff_exists``,
``Localization/Defs.lean``), i.e. when ``S`` meets the annihilator
``(0 : (a t - b s))``.  That is the same source-side question
``LocalizationRings.ParentMethods.characteristic`` and the prime localization's
field decision already ask through ``inverted_submonoid_meets``.

The owner of equality is ``_fraction_equality_status``.  It decides through the
localization of the regular module; where that route establishes an answer, that
answer stands.  Where it says nothing, the source-side criterion above is
consulted, so no answer the module route gives can change, and a question the
``colon`` owner does not support keeps the undecided proposition rather than
being guessed.

These tests state the six cases that matter: an ordinary domain, units, zero
numerators, equal and unequal fractions, a quotient with zero divisors, a
quotient where the inverted element is nilpotent, and one question that stays
genuinely undecided.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.logic import ask


def _halves():
    r"""``ZZ[1/2]``: an ordinary domain whose inverted set is ``{2^k}``."""
    return ZZ.localization(ZZ(2))


def test_equal_fractions_in_a_domain_are_the_cross_product_relation() -> None:
    r"""``1/2 = 2/4`` because ``1*4 = 2*2``."""
    ring = _halves()

    assert ring.fraction(ZZ(1), ZZ(2)) == ring.fraction(ZZ(2), ZZ(4))
    assert ring.fraction(ZZ(3), ZZ(2)) == ring.fraction(ZZ(6), ZZ(4))


def test_unequal_fractions_in_a_domain_are_not_equal() -> None:
    r"""``1/2 != 3/2`` and ``1/2 != 1/1``, decided, not undecided."""
    ring = _halves()

    assert ring.fraction(ZZ(1), ZZ(2)) != ring.fraction(ZZ(3), ZZ(2))
    assert ring.fraction(ZZ(1), ZZ(2)) != ring.fraction(ZZ(1), ZZ(1))
    assert ring.fraction(ZZ(1), ZZ(2)) != ring.zero()


def test_a_unit_equals_its_own_fraction_and_a_zero_numerator_vanishes() -> None:
    r"""``4/2 = 2`` (a unit written as a fraction) and ``0/1 = 0/2 = 0``."""
    ring = _halves()

    assert ring.fraction(ZZ(4), ZZ(2)) == ring(ZZ(2))
    assert ring.fraction(ZZ(0), ZZ(1)) == ring.zero()
    assert ring.fraction(ZZ(0), ZZ(2)) == ring.zero()
    assert ring.fraction(ZZ(0), ZZ(1)) == ring.fraction(ZZ(0), ZZ(2))


def test_a_zero_divisor_dies_in_the_localization_that_inverts_it() -> None:
    r"""In ``(Z/6)[1/2]`` the class of ``3`` is zero and the class of ``2`` is not.

    ``3 * 2 = 0`` in ``Z/6`` and ``2`` is inverted, so ``3/1 = 0``; ``2`` becomes
    a unit, so it is not zero.
    """
    ring = ZZ.ideal(ZZ(6)).quotient_ring()
    localized = ring.localization(ring(2))

    assert localized(ring(3)) == localized.zero()
    assert localized(ring(2)) != localized.zero()
    assert localized(ring(3)) != localized(ring(2))


def test_a_nilpotent_denominator_makes_the_localization_trivial() -> None:
    r"""Inverting ``t`` in ``(Z/5)[t]/(t^2)`` gives the zero ring: ``t^2 = 0``.

    ``1/1 = 0/1`` needs some ``t^k`` with ``t^k * 1 = 0``, and ``k = 2`` is one.
    """
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    t = polynomial.algebra_generator("t")
    quotient = polynomial.quotient_ring(t**2)
    at_t = quotient.localization(quotient.quotient_map()(t))

    assert at_t.one() == at_t.zero()
    assert at_t(quotient.quotient_map()(t)) == at_t.zero()


def test_a_question_the_colon_owner_does_not_support_stays_undecided() -> None:
    r"""``y/1`` in ``(QQ[x,y]/(xy))_x`` is zero, and this owner does not yet say so.

    ``x y = 0`` and ``x`` is inverted, so the answer is yes; deciding it needs
    the annihilator ``(0 : (y)) = (x)`` of a word-framed presented algebra,
    whose ``colon`` the ideal owner does not implement.  Undecided is stated as
    undecided: ``ask`` answers ``Unknown``, and the equality is neither claimed
    nor refuted.
    """
    presentation = QQ.polynomial_ring(("x", "y"))
    x, y = presentation.algebra_generators()
    axes = presentation.quotient_by_relations((x * y,))
    xbar, ybar = axes.algebra_generator("x"), axes.algebra_generator("y")
    at_x = axes.localization(xbar)

    assert ask(at_x(ybar) == at_x.zero()) is Unknown
    # The same missing annihilator blocks every equality there: even `x`, which
    # is inverted and therefore not zero, is not *decided* unequal by this owner.
    assert ask(at_x(xbar) == at_x.zero()) is Unknown
