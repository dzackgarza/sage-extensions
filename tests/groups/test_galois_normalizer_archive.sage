r"""$N_{G_{\mathbb{Q}}}(G_K)/G_K = \operatorname{Aut}(K/\mathbb{Q})$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_real_cube_root_of_two_has_no_nontrivial_automorphisms() -> None:
    r"""$K = \mathbb{Q}(\sqrt[3]{2})$: $G_K$ has index $3$, is not normal, and $\operatorname{Aut}(K/\mathbb{Q}) = 1$ since the other roots of $x^3 - 2$ are not real."""
    x = QQ.polynomial_ring("x").algebra_generator("x")
    subgroup = QQ.absolute_galois_group().open_subgroup((x**3 - 2).number_field("a"))

    assert subgroup.index() == 3
    assert not subgroup.is_normal()
    assert subgroup.normalizer_quotient().order() == 1


def test_the_normalizer_quotient_for_root_five_is_its_galois_group_of_order_two() -> None:
    r"""$K = \mathbb{Q}(\sqrt5)$: $G_K$ is normal of index $2$ and $N(G_K)/G_K = \operatorname{Gal}(K/\mathbb{Q}) \cong \mathbb{Z}/2$."""
    x = QQ.polynomial_ring("x").algebra_generator("x")
    subgroup = QQ.absolute_galois_group().open_subgroup((x**2 - 5).number_field("a"))
    quotient = subgroup.normalizer_quotient()

    assert subgroup.index() == 2
    assert subgroup.is_normal()
    assert quotient.order() == 2
    assert quotient.is_isomorphic_to(Groups.C(2))
