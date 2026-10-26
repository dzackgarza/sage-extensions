r"""Nikulin's criterion distinguishes primitive embeddings into even unimodular lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_but_not_a2_embeds_primitively_into_the_hyperbolic_plane() -> None:
    a1 = NamedLattices.A1
    a2 = NamedLattices.A2

    assert a1.embeds_in_even_unimodular(1, 1)
    assert not a2.embeds_in_even_unimodular(1, 1)


def test_positive_a1_embeds_primitively_into_e8() -> None:
    lattice = Lattices(ZZ)([[2]])
    embedding = lattice.embed_in_even_unimodular(8, 0)
    target = embedding.codomain()

    assert embedding.domain() is lattice
    assert embedding.is_primitive()
    assert target.module_rank() == cardinal(8)
    assert target.determinant() == 1
    assert target.is_even()
