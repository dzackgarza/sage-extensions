r"""A unimodular lattice enlarged by no discriminant classes is unchanged."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_trivial_overlattice_has_index_one() -> None:
    lattice = NamedLattices.U
    inclusion = lattice.overlattice()

    assert inclusion.domain() is lattice
    assert inclusion.index() == 1
    assert abs(inclusion.codomain().determinant()) == 1
