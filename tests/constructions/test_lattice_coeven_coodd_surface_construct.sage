r"""Coeven and coodd are complementary predicates on even lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_unimodular_hyperbolic_plane_is_coeven() -> None:
    lattice = NamedLattices.U

    assert lattice.is_coeven()


def test_unimodular_hyperbolic_plane_is_not_coodd() -> None:
    lattice = NamedLattices.U

    assert not lattice.is_coodd()
    assert lattice.is_coodd() is (not lattice.is_coeven())
