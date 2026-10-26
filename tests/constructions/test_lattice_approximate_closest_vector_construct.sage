r"""The public approximate closest-vector operation agrees with nearest-plane rounding."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_approximate_closest_vector_rounds_coordinates() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    first = lattice.basis_vector(0)

    assert lattice.approximate_closest_vector((QQ(3) / 4, QQ(1) / 4)) == first
