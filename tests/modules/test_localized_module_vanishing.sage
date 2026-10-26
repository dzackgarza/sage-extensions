r"""Vanishing of a localized module.

A finitely generated module $M$ has $S^{-1}M = 0$ exactly when
$\operatorname{Ann}(M) \cap S \ne \emptyset$, and $M_{\mathfrak p} = 0$ exactly
when $\mathfrak p \notin \operatorname{Supp}(M) = V(\operatorname{Ann} M)$
(Atiyah–Macdonald, *Introduction to Commutative Algebra*, 3.14 and ex. 3.19).
"""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(R, a):
    return Modules(R)(R.quotient_ring(R.ideal(a)))


def test_inverting_x_kills_q_x_mod_x() -> None:
    R = QQ["x"]
    x = R.gen()
    assert cyclic(R, x).localize(x).is_zero()


def test_inverting_x_minus_1_keeps_q_x_mod_x() -> None:
    """(x - 1)^n is 1 or -1 modulo x, never 0, so (x - 1)^n never kills the generator."""
    R = QQ["x"]
    x = R.gen()
    localized = cyclic(R, x).localize(x - 1)
    assert not localized.is_zero()
    assert localized.minimal_number_of_generators() == 1


def test_z_mod_6_vanishes_at_5_and_not_at_3() -> None:
    """Supp(Z/6) = {(2), (3)}."""
    M = cyclic(ZZ, 6)
    assert M.localize_at_prime(ZZ.ideal(5)).is_zero()
    assert not M.localize_at_prime(ZZ.ideal(3)).is_zero()
    assert M.localize_at_prime(ZZ.ideal(3)).cardinality() == 3
    assert M.localize_at_prime(ZZ.ideal(2)).cardinality() == 2
