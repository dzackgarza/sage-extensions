r"""The lattice rank spelling agrees with the underlying module rank."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_rank_is_two() -> None:
    lattice = NamedLattices.U

    assert lattice.rank() == cardinal(2)


def test_lattice_rank_agrees_with_module_rank() -> None:
    lattice = Lattices(ZZ)("A2")

    assert lattice.rank() == lattice.module_rank()
