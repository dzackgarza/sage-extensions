r"""The contact polytope of the square lattice is the diamond on its four shortest vectors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_contact_polytope_has_four_vertices() -> None:
    lattice = Lattices(ZZ)(ZZ^2)

    assert lattice.contact_polytope().n_vertices() == 4
