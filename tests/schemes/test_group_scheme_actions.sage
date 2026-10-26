r"""The affine group schemes ``G_a``, ``G_m`` and ``mu_2``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_group_laws_of_ga_and_gm_are_addition_and_multiplication() -> None:
    r"""``G_a = Spec QQ[x]`` with ``m^* x = x ⊗ 1 + 1 ⊗ x``; ``G_m = Spec QQ[u, u^{-1}]`` with
    ``m^* u = u ⊗ u`` and ``i^* u = u^{-1}`` (Milne, *Algebraic Groups*, Examples 1.3--1.4)."""
    group_schemes = Grp(Schemes(QQ))
    Ga = group_schemes.additive_group()
    Gm = group_schemes.multiplicative_group()

    x = Ga.coordinate_ring().gen()
    m = Ga.multiplication()
    p, q = m.domain().projection(0), m.domain().projection(1)
    assert m.pullback(x) == p.pullback(x) + q.pullback(x)
    assert Ga.inverse_morphism().pullback(x) == -x
    assert Ga.unit_morphism().pullback(x) == 0

    u = Gm.coordinate_ring().gen()
    m = Gm.multiplication()
    p, q = m.domain().projection(0), m.domain().projection(1)
    assert m.pullback(u) == p.pullback(u) * q.pullback(u)
    assert Gm.inverse_morphism().pullback(u) == u**-1
    assert Gm.unit_morphism().pullback(u) == 1
    assert not Ga.is_isomorphic(Gm)


def test_mu2_is_etale_over_qq_and_nonreduced_over_gf2() -> None:
    r"""``mu_2 = Spec R[u]/(u^2 - 1)``: over ``QQ`` it is two reduced points ``u = ±1``;
    over ``GF(2)``, ``u^2 - 1 = (u - 1)^2`` and ``mu_2`` is a nonreduced point of degree 2.

    Derivation: ``QQ[u]/(u^2 - 1) = QQ x QQ`` by CRT; ``GF(2)[u]/(u - 1)^2`` has the
    nilpotent ``u - 1``.
    """
    over_QQ = Grp(Schemes(QQ)).roots_of_unity(2)
    over_GF2 = Grp(Schemes(GF(2))).roots_of_unity(2)

    assert over_QQ.degree() == 2
    assert over_QQ.is_reduced()
    assert over_QQ.rational_points().cardinality() == 2
    assert over_QQ.structure_morphism().is_etale()
    assert over_GF2.degree() == 2
    assert not over_GF2.is_reduced()
    assert over_GF2.rational_points().cardinality() == 1
    assert not over_GF2.structure_morphism().is_etale()
