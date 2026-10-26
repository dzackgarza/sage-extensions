r"""Source-backed Voronoi geometry retained from the archived mathematics suite.

Conway--Sloane, *Sphere Packings, Lattices and Groups*, chapter 21: the
Voronoi cell of the square lattice is the half-cube, and the Voronoi cell of
``A2`` is a regular hexagon.  The live implementation already owns the exact
polyhedron and relevant vectors; these specimens retain the literature facts
that were not present in the current regression surface.
"""

from sage_extensions.all import *


def test_square_lattice_voronoi_cell_is_the_unit_area_half_cube() -> None:
    square = Lattices.Z ** 2
    cell = square.voronoi_cell()

    assert cell.volume() == 1
    assert cell.n_vertices() == 4
    assert Set(tuple(vertex) for vertex in cell.vertices()) == Set(
        (QQ(a) / 2, QQ(b) / 2)
        for a in (-1, 1)
        for b in (-1, 1)
    )


def test_a2_voronoi_cell_is_a_hexagon_with_six_relevant_vectors() -> None:
    hexagonal = Lattices.A2
    cell = hexagonal.voronoi_cell()

    assert cell.facets().cardinality() == 6
    assert cell.n_vertices() == 6
    assert hexagonal.voronoi_relevant_vectors().cardinality() == 6


def test_normalized_a2_facet_inequalities_recover_the_six_roots():
    lattice = Lattices.A2
    assert lattice.voronoi_relevant_vectors().cardinality() == 6
    assert all(vector.q() == 2 for vector in lattice.voronoi_relevant_vectors())
