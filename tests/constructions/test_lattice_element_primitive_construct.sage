r"""Lattice vectors report primitivity through their rank-one sublattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_basis_vector_is_primitive() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)

    assert e.is_primitive()
    assert e.is_primitive() == e.sublattice().is_primitive()


def test_twice_a_hyperbolic_basis_vector_is_not_primitive() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    doubled = 2 * e

    assert not doubled.is_primitive()
    assert doubled.is_primitive() == doubled.sublattice().is_primitive()
