r"""Ordinal and cardinal arithmetic.

Source: Jech, *Set Theory* (3rd millennium ed.), Ch. 2--3 and 5: natural (Hessenberg)
sum and product are commutative and associative while ordinal sum is not
(`\omega + 1 \ne 1 + \omega`); `\aleph_0 + 2^{\aleph_0} = \aleph_0 \cdot 2^{\aleph_0} =
\aleph_0^{\aleph_0} = 2^{\aleph_0}`; `\aleph_1 \le 2^{\aleph_0}` in ZFC while the
comparison of `\aleph_2` with `2^{\aleph_0}` is independent of ZFC (Cohen); ordinal
exponentiation `2^\omega = \omega` is countable.
"""

from sage_extensions.all import *


def test_natural_ordinal_operations_form_the_commutative_semiring() -> None:
    alpha = omega(0)
    beta = omega(1)
    gamma = omega(2)
    assert alpha + beta == beta + alpha
    assert alpha * beta == beta * alpha
    assert (alpha + beta) + gamma == alpha + (beta + gamma)
    assert (alpha * beta) * gamma == alpha * (beta * gamma)
    assert (alpha + beta) * gamma == alpha * gamma + beta * gamma
    assert Ordinals()(2).ordinal_sum(3) == 5
    assert alpha.ordinal_sum(1) != Ordinals()(1).ordinal_sum(alpha)


def test_cardinal_arithmetic_and_order_do_not_assume_continuum_hypothesis() -> None:
    cardinals = Cardinalities()
    assert cardinal(3) ** cardinal(5) == cardinal(243)
    assert aleph0 + continuum == continuum
    assert aleph0 * continuum == continuum
    assert aleph0 ** aleph0 == continuum

    assert cardinals.compare(aleph(1), continuum) is CardinalComparison.LESS_OR_EQUAL
    assert cardinals.Mor(aleph(1), continuum).cardinality() == 1
    assert ask(cardinals.Mor(continuum, aleph(1)).is_empty()) is Unknown
    assert cardinals.compare(aleph(2), continuum) is CardinalComparison.INCOMPARABLE
    assert ask(cardinals.Mor(aleph(2), continuum).is_empty()) is Unknown
    assert ask(cardinals.Mor(continuum, aleph(2)).is_empty()) is Unknown
    assert cardinals.Mor(continuum, aleph0).is_empty() is True
    assert cardinals.Mor(continuum, aleph0).cardinality() == 0


def test_ordinal_powers_have_ordinal_not_cardinal_exponentiation_size() -> None:
    assert Ordinals()(2).ordinal_power(omega(0)).cardinality() == aleph0
    assert omega(0).ordinal_power(omega(0)).cardinality() == aleph0
    assert Ordinals()(2).ordinal_power(omega(1)).cardinality() == aleph(1)


def test_an_integer_literal_to_an_infinite_cardinal_is_the_cardinal_power() -> None:
    r"""``2 ** aleph0``: the session's own integer literal defers to the cardinal.

    A preparsed integer literal is a session integer, whose ``__pow__`` reads an
    integer exponent through ``__index__``.  An infinite cardinal refuses that
    conversion on purpose, and the reflected ``Cardinal.__rpow__`` is the
    maintained ``2**aleph0 = continuum``; the ring power must therefore return
    ``NotImplemented`` instead of letting the refusal escape.
    """
    assert 2 ** aleph0 == continuum
    assert cardinal(2) ** aleph0 == continuum
