r"""A lattice reports pairings against its selected generators."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_generator_pairings_are_its_gram_row() -> None:
    lattice = NamedLattices.U
    labels = lattice.module_generating_set()
    e = lattice.module_generator(labels[0])
    pairings = lattice.generator_pairings(e)

    assert pairings[labels[0]] == ZZ.zero()
    assert pairings[labels[1]] == ZZ.one()


def test_hyperbolic_plane_generator_pairings_match_the_form() -> None:
    lattice = NamedLattices.U
    labels = lattice.module_generating_set()
    f = lattice.module_generator(labels[1])
    pairings = lattice.generator_pairings(f)

    for label in labels:
        assert pairings[label] == lattice.b(f, lattice.module_generator(label))
