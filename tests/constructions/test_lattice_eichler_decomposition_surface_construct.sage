r"""Represented decompositions expose the hyperbolic-plane count used by Eichler's criterion."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_u_plus_a2_has_two_represented_hyperbolic_plane_summands() -> None:
    lattice = NamedLattices.U + NamedLattices.U + Lattices(ZZ)("A2")

    assert lattice.hyperbolic_plane_summand_count() == 2
    assert lattice.splits_two_hyperbolic_planes()
    assert lattice.eichler_criterion_applies()


def test_a2_does_not_split_two_hyperbolic_planes() -> None:
    lattice = Lattices(ZZ)("A2")

    assert lattice.hyperbolic_plane_summand_count() == 0
    assert not lattice.splits_two_hyperbolic_planes()
    assert not lattice.eichler_criterion_applies()
