r"""A polygon's chosen triangulations: their cells, coverage, common faces, axioms.

A triangulation of a lattice polygon is a family of cells of it whose union is
the polygon and whose pairwise intersections are common faces.  The collection
``polygon.triangulations()`` holds that family as an object: ``on`` receives the
cells the polygon answers in ``triangulate`` and computes none of them, the
object answers whether the family covers the polygon and whether its members
meet along common faces, and the two axioms ``Integral`` and ``Unimodular``
refine it by its cells' lattice and their normalized volumes.

The specimens are the square `\operatorname{conv}\{(\pm 1, \pm 1)\}` and the
stored Sterk2 hull, the two #582 measured, and, for the axioms, the unit square
and the triangle `\operatorname{conv}\{(0,0),(2,0),(0,1)\}` of normalized volume
two: a triangulation is unimodular when every one of its cells has normalized
volume one, so the unit square's two cells are and this triangle's single cell
is not.

Counts and volume sums are asserted as the polygon's own -- `n - 2` cells, and
volumes adding up to its normalized volume -- rather than as the numbers #582
recorded, which the report beside this file compares them against.
"""

from sage_extensions.all import *

import pytest


def _square():
    r"""The square `\operatorname{conv}\{(\pm 1, \pm 1)\}` in the lattice `\mathbf{Z}^2`."""
    return LatticePolygons(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))


def _sterk2():
    r"""The stored Sterk2 hull, whose seventeen vertices all span it."""
    return Sterk.sterk2_polygon(ZZ.free_module(2))


def _specimens():
    return (_square(), _sterk2())


def _unit_square():
    r"""The unit square, whose standard triangulation is two unimodular triangles."""
    return LatticePolygons(ZZ.free_module(2))(((0, 0), (0, 1), (1, 1), (1, 0)))


def _volume_two_triangle():
    r"""The triangle `\operatorname{conv}\{(0,0),(2,0),(0,1)\}`, of normalized volume two."""
    return LatticePolygons(ZZ.free_module(2))(((0, 0), (2, 0), (0, 1)))


def _overlapping_cells():
    r"""Two triangles of the square, the second inside the first and not a face of it.

    ``first`` is the lower-right half `\operatorname{conv}\{(-1,-1),(1,-1),(1,1)\}`
    and ``second`` is `\operatorname{conv}\{(-1,-1),(1,-1),(0,0)\}`, whose third
    vertex lies on the first's hypotenuse: the intersection is the second
    triangle, which is no face of the first, and their volumes add up to six.
    """
    lattice = ZZ.free_module(2)
    first = ConvexPolygons(lattice)(((-1, -1), (1, -1), (1, 1)))
    second = ConvexPolygons(lattice)(((-1, -1), (1, -1), (0, 0)))
    return first, second


def test_the_collection_receives_the_cells_the_polytope_answers() -> None:
    r"""The cells of a chosen triangulation are the polygon's own, on both specimens.

    A triangulation of a convex polygon whose vertices are all extreme points has
    two fewer triangles than it has vertices, uses every vertex, and its cells'
    normalized volumes add up to the polygon's.  The collection is built from the
    family ``triangulate`` answers and holds exactly that family, so no cell is
    recomputed and each is a polytope of the polygon's own lattice.
    """
    for polygon in _specimens():
        cells = tuple(polygon.triangulate())
        collection = polygon.triangulations().on(cells)
        own = frozenset(polygon.vertices())
        vertices = int(polygon.vertices().cardinality())

        assert collection.target() is polygon
        assert frozenset(collection.cells()) == frozenset(cells)
        assert int(collection.cells().cardinality()) == vertices - 2
        assert all(frozenset(cell.vertices()) <= own for cell in collection.cells())
        assert frozenset(
            vertex for cell in collection.cells() for vertex in cell.vertices()
        ) == own
        assert all(
            cell in ConvexPolytopes(polygon.ambient_lattice())
            for cell in collection.cells()
        )
        assert sum(
            int(cell.normalized_volume()) for cell in collection.cells()
        ) == int(polygon.normalized_volume())


def test_the_cells_cover_the_polytope_exactly_when_their_volumes_add_up() -> None:
    r"""A family of cells inside the polygon covers it exactly when its volumes do.

    Each cell of the standard triangulation lies in the polygon and their volumes
    add up to its, so a finite union of closed cells of the polygon's own volume
    is the polygon.  Drop one cell and the sum falls short, so the union is not
    the polygon; and the supplied overlapping pair is contained in the square
    with volumes adding up to six of its eight, so it covers neither.
    """
    for polygon in _specimens():
        cells = tuple(polygon.triangulate())
        triangulations = polygon.triangulations()

        assert triangulations.on(cells).covers_target() is True
        assert triangulations.on(cells[:-1]).covers_target() is False
    square = _square()
    overlapping = square.triangulations().on(_overlapping_cells())

    assert overlapping.covers_target() is False


def test_the_cells_meet_in_common_faces() -> None:
    r"""The standard triangulation's cells meet in faces; an overlapping pair does not.

    Two cells of a triangulation meet along a face of each -- an edge of the
    square's triangles -- and the intersection of the overlapping pair is the
    second triangle itself, which is no face of the first: it is a subpolytope
    whose third vertex lies inside a facet of the first.
    """
    for polygon in _specimens():
        collection = polygon.triangulations().on(tuple(polygon.triangulate()))

        assert collection.intersections_are_common_faces() is True
    square = _square()
    overlapping = square.triangulations().on(_overlapping_cells())

    assert overlapping.intersections_are_common_faces() is False


def test_the_integral_and_unimodular_axioms_answer() -> None:
    r"""The two axioms answer on the unit square and on the volume-two triangle.

    Unimodular means that every cell has normalized volume one, so the unit
    square's two triangles are unimodular and the volume-two triangle's single
    cell is not.  Integral means that every cell's vertices are lattice points of
    the polygon's own lattice, which all three families satisfy -- integrality is
    weaker than unimodularity, so the volume-two triangle is admitted as an
    integral triangulation and refused as a unimodular one.
    """
    unit = _unit_square()
    unimodular = unit.triangulations().unimodular(tuple(unit.triangulate()))

    assert all(
        int(unimodular.normalized_volume(cell)) == 1 for cell in unimodular.cells()
    )
    for polygon in _specimens():
        triangulations = polygon.triangulations()
        cells = tuple(polygon.triangulate())
        integral = triangulations.integral(cells)

        assert all(
            integral.simplex_vertices_are_integral(cell) is True
            for cell in integral.cells()
        )
        with pytest.raises(ValueError):
            triangulations.unimodular(cells)
    triangle = _volume_two_triangle()
    triangle_cells = tuple(triangle.triangulate())
    triangle_triangulations = triangle.triangulations()

    assert int(tuple(triangle_cells)[0].normalized_volume()) == 2
    assert all(
        triangle_triangulations.integral(triangle_cells).simplex_vertices_are_integral(
            cell
        )
        is True
        for cell in triangle_cells
    )
    with pytest.raises(ValueError):
        triangle_triangulations.unimodular(triangle_cells)
