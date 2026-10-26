r"""A unimodular lattice has trivial local modification with no glue classes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_trivial_two_local_modification_has_index_one() -> None:
    lattice = NamedLattices.U
    inclusion = lattice.local_modification(2)

    assert inclusion.domain() is lattice
    assert inclusion.index() == 1
    assert abs(inclusion.codomain().determinant()) == 1
