r"""The nearest point in the square lattice is determined by Euclidean distance."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_closest_vector_to_three_quarters_one_quarter() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    first = lattice.basis_vector(0)

    assert lattice.closest_vector((QQ(3) / 4, QQ(1) / 4)) == first
