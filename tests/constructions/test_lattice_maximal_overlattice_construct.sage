r"""A unimodular lattice is already a maximal integral overlattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_maximal_overlattice_is_identity_extension() -> None:
    lattice = NamedLattices.U
    inclusion = lattice.maximal_overlattice()

    assert inclusion.domain() is lattice
    assert inclusion.index() == 1
    assert abs(inclusion.codomain().determinant()) == 1
