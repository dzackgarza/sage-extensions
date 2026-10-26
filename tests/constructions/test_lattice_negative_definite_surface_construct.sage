r"""Negative definiteness is the signature-(0,rank) predicate."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_is_negative_definite() -> None:
    lattice = Lattices(ZZ)("A2")

    assert lattice.is_negative_definite()


def test_hyperbolic_plane_is_not_negative_definite() -> None:
    lattice = NamedLattices.U

    assert not lattice.is_negative_definite()
