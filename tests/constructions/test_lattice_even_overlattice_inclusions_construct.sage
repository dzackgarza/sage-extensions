r"""A unimodular even lattice has only its identity even overlattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_has_one_even_overlattice_inclusion() -> None:
    lattice = NamedLattices.U
    inclusions = lattice.even_overlattice_inclusions()

    assert inclusions.cardinality() == cardinal(1)
    inclusion = inclusions[0]
    assert inclusion.domain() is lattice
    assert inclusion.index() == 1
