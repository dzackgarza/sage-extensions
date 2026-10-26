r"""A unimodular lattice has full stable orthogonal group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_stable_orthogonal_group_is_full_orthogonal_group() -> None:
    lattice = NamedLattices.U

    assert lattice.stable_orthogonal_group().cardinality() == lattice.Aut().cardinality()
