r"""Babai rounding is exact for the orthonormal square lattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_babai_rounds_three_quarters_one_quarter() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    first = lattice.basis_vector(0)

    assert lattice.babai((QQ(3) / 4, QQ(1) / 4)) == first
