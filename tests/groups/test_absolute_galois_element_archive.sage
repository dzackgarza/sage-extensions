r"""Frobenius restricted to a finite stage."""

from sage_extensions.all import *  # noqa: F401,F403


def test_frobenius_restricts_to_the_generator_of_gal_f25_over_f5() -> None:
    r"""$\mathrm{Frob}|_{\mathbb{F}_{25}}$ is $x \mapsto x^5$, of order $2$; the Frobenius class of the abelian group $G_{\mathbb{F}_5}$ is $\{\mathrm{Frob}\}$, so it excludes $\mathrm{Frob}^2$."""
    group = GF(5).absolute_galois_group()
    stage = group.finite_extension(2)
    frobenius = group.frobenius()
    restricted = frobenius.restrict(stage)
    alpha = stage.field().field_generators()[0]

    assert restricted.multiplicative_order() == 2
    assert restricted.action()(alpha) == alpha**5
    assert restricted.action()(alpha) != alpha
    assert frobenius in frobenius.conjugacy_class()
    assert frobenius**2 not in frobenius.conjugacy_class()
