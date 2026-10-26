r"""The Voronoi cell of the integer line is an interval with two vertices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_line_voronoi_cell_has_two_vertices() -> None:
    lattice = Lattices(ZZ)(ZZ^1)

    assert lattice.voronoi_cell().n_vertices() == 2
