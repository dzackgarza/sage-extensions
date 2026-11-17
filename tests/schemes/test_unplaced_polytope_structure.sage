r"""The structure of an unplaced lattice polygon: faces, boundary, cells, lifts.

The unplaced polytope is the one that knows its own face poset, so it answers its
own structure and no placement is chosen anywhere in this file.  Its faces are
polytopes of its own ambient lattice, ``face_inclusion`` is the inclusion of one
of them into it, a facet's inclusion is that inclusion at a face of codimension
one, ``boundary`` is the family of those facets, ``triangulate`` cuts the
polytope into cells whose vertices are its own vertices, and the lift of one of
its geometric automorphisms to a face is that face's own automorphism -- or
nothing, when the automorphism carries the face to another one.

The specimens are the square `\operatorname{conv}\{(\pm 1, \pm 1)\}`, the
irregular quadrangle `\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}` and the
stored Sterk2 hull: the three the placed lane reads its own six operations on, so
the two lanes are read on the same polygons.
"""

import pytest

from sage_extensions.all import *


def _square():
    return LatticePolygons(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))


def _quadrangle():
    return LatticePolygons(ZZ.free_module(2))(((0, 0), (1, 0), (0, 1), (2, 3)))


def _sterk2():
    return Sterk.sterk2_polygon(ZZ.free_module(2))


def _specimens():
    return (_square(), _quadrangle(), _sterk2())


def _faces_below_the_top(polygon):
    r"""The vertices and the edges of ``polygon``: every face but the polygon itself."""
    return tuple(polygon.faces(0)) + tuple(polygon.faces(1))


def _check_a_face_inclusion(polygon, face):
    r"""The inclusion of ``face`` into ``polygon`` fixes the face's points and is injective.

    Both ends are objects of one category, the arrow's image is the face it
    started from, and the inclusion sends each of the face's points to that same
    point of the ambient space.  Composed with the identity of the face it is
    itself: that is what it is for the inclusion to be the identity on the face.
    """
    inclusion = polygon.face_inclusion(face)

    assert inclusion.domain() is face
    assert inclusion.codomain() is polygon
    assert inclusion.image() is face
    assert inclusion.is_injective() is True
    assert inclusion * Sets().Mor(face, face).identity() == inclusion
    for vertex in face.vertices():
        point = face.rational_point(vertex)
        assert inclusion(point) == polygon.rational_point(vertex)


def test_the_unplaced_polygons_faces_include_into_the_polytope() -> None:
    r"""A polygon's faces are its vertices, its edges and itself, and each includes into it.

    The faces of a polygon of dimension two are the faces of dimension one and
    zero together with the polygon itself and the empty face, and no others:
    those four families are the whole face object.  An edge's inclusion into the
    polygon, followed by a vertex's inclusion into that edge, is that vertex's
    inclusion into the polygon.
    """
    for polygon in _specimens():
        vertices = int(polygon.vertices().cardinality())
        whole = (
            *polygon.faces(0),
            *polygon.faces(1),
            *polygon.faces(2),
            *polygon.faces(-1),
        )

        assert int(polygon.dimension()) == 2
        assert int(polygon.faces(0).cardinality()) == vertices
        assert int(polygon.faces(1).cardinality()) == vertices
        assert tuple(polygon.faces(2)) == (polygon,)
        assert int(polygon.faces(-1).cardinality()) == 1
        assert frozenset(tuple(polygon.face_poset())) == frozenset(whole)
        for face in _faces_below_the_top(polygon):
            _check_a_face_inclusion(polygon, face)
        for edge in tuple(polygon.faces(1)):
            for vertex in tuple(edge.faces(0)):
                assert (
                    polygon.face_inclusion(edge) * edge.face_inclusion(vertex)
                    == polygon.face_inclusion(vertex)
                )
        assert polygon.face_inclusion(polygon).domain() is polygon
        for vertex in polygon.vertices():
            point = polygon.rational_point(vertex)
            assert polygon.face_inclusion(polygon)(point) == point


def test_the_unplaced_polygons_facets_include_into_the_polytope() -> None:
    r"""A facet is an edge here, and its inclusion is the inclusion of that face.

    The facets of a polygon are its faces of codimension one, which are its
    edges; a vertex is a face but not a facet, and the operation refuses it
    rather than including it as one.
    """
    for polygon in _specimens():
        facets = tuple(polygon.faces(1))

        assert int(polygon.faces(1).cardinality()) == int(polygon.vertices().cardinality())
        for facet in facets:
            inclusion = polygon.facet_inclusion(facet)
            assert inclusion.domain() is facet
            assert inclusion.codomain() is polygon
            for vertex in facet.vertices():
                assert (
                    inclusion(facet.rational_point(vertex))
                    == polygon.rational_point(vertex)
                )
        with pytest.raises(AssertionError):
            polygon.facet_inclusion(tuple(polygon.faces(0))[0])
        with pytest.raises(AssertionError):
            polygon.facet_inclusion(polygon)


def test_the_unplaced_polygons_boundary_is_their_codimension_one_faces() -> None:
    r"""The boundary is exactly the faces of codimension one, and a point has none.

    A polygon's boundary is the union of its facets, so the family of boundary
    faces and the family of edges are the same family; a face of dimension zero
    or less has no proper face at all, so its boundary is empty.
    """
    for polygon in _specimens():
        boundary = tuple(polygon.boundary())

        assert frozenset(boundary) == frozenset(polygon.faces(1))
        assert int(polygon.boundary().cardinality()) == int(polygon.faces(1).cardinality())
        assert all(
            int(face.dimension()) == int(polygon.dimension()) - 1 for face in boundary
        )
        for vertex in tuple(polygon.faces(0)):
            assert int(vertex.boundary().cardinality()) == 0
        assert int(tuple(polygon.faces(-1))[0].boundary().cardinality()) == 0


def test_the_unplaced_boundary_inclusion_is_one_inclusion_per_boundary_face() -> None:
    r"""The boundary is not a polytope, so its inclusion is one arrow per boundary face.

    Each of those arrows has one boundary face as its source and the polygon as
    its target, and it moves none of that face's points.
    """
    for polygon in _specimens():
        boundary = tuple(polygon.boundary())
        inclusion = polygon.boundary_inclusion()
        arrows = tuple(inclusion.values())

        assert int(inclusion.index_set().cardinality()) == int(polygon.boundary().cardinality())
        for face, arrow in zip(boundary, arrows, strict=True):
            assert arrow.domain() is face
            assert arrow.codomain() is polygon
            for vertex in face.vertices():
                assert arrow(face.rational_point(vertex)) == polygon.rational_point(vertex)


def test_the_unplaced_polygons_triangulate_into_cells_on_their_own_vertices() -> None:
    r"""The cells of a triangulation are simplices on the polygon's own vertices.

    A triangulation of a convex polygon whose vertices are all extreme points has
    exactly two fewer triangles than it has vertices: its triangles meet along
    diagonals, and a maximal family of pairwise non-crossing diagonals of an
    `n`-gon has `n - 3` of them, which leaves `n - 2` triangles.  The cells lie in
    the polygon, use every one of its vertices, and their normalized volumes add
    up to the polygon's, which is what it is for their union to be the polygon.
    """
    for polygon in _specimens():
        cells = tuple(polygon.triangulate())
        own = frozenset(polygon.vertices())
        vertices = int(polygon.vertices().cardinality())

        assert int(polygon.triangulate().cardinality()) == vertices - 2
        assert all(int(cell.dimension()) == 2 for cell in cells)
        assert all(frozenset(cell.vertices()) <= own for cell in cells)
        assert all(cell.is_contained_in(polygon) is True for cell in cells)
        assert frozenset(vertex for cell in cells for vertex in cell.vertices()) == own
        assert sum(int(cell.normalized_volume()) for cell in cells) == int(
            polygon.normalized_volume()
        )
        assert all(cell in ConvexPolytopes(polygon.ambient_lattice()) for cell in cells)
    square = _square()
    assert int(square.normalized_volume()) == 8
    assert tuple(int(cell.normalized_volume()) for cell in square.triangulate()) == (4, 4)
    quadrangle = _quadrangle()
    assert sum(
        int(cell.normalized_volume()) for cell in quadrangle.triangulate(engine="internal")
    ) == int(quadrangle.normalized_volume())


def test_the_unplaced_polygons_lift_an_automorphism_to_exactly_the_faces_it_preserves() -> None:
    r"""A geometric automorphism of a polygon lifts to a face exactly when it keeps it.

    The lift is an element of the face's own geometric automorphism group acting
    on the face's vertices as the parent's automorphism does; a face the
    automorphism carries to another face has none, because that restriction is an
    isomorphism of the face onto a different face and no automorphism of it.

    Every one of the three polygons has an automorphism that keeps a face, so a
    lift is asked for and read on each; the square is where the other case occurs,
    and its identity keeps all four edges, two reflections keep two edges each and
    the other five automorphisms move every edge, while the identity's lift is each
    face's own identity.  The irregular quadrangle's group is trivial and the
    Sterk2 hull's two elements keep every face, so on those two no face is moved.
    """
    for polygon in _specimens():
        automorphisms = tuple(polygon.geometric_automorphisms())
        abstract = polygon.geometric_to_abstract_automorphisms()
        preserved = 0

        assert automorphisms
        for element in automorphisms:
            for face in _faces_below_the_top(polygon):
                lift = polygon.geometric_lifts_of_face_automorphism(element, face)
                keeps = abstract(element)(face) == face
                assert (lift is None) != keeps
                if keeps:
                    preserved += 1
                    assert lift in face.geometric_automorphisms()
                    assert all(lift(vertex) == element(vertex) for vertex in face.vertices())
        assert preserved > 0
    square = _square()
    automorphisms = tuple(square.geometric_automorphisms())
    identity = square.geometric_automorphisms().one()
    kept_edges = tuple(
        int(
            square.faces(1)
            .filtered(
                lambda face, element=element: square.geometric_lifts_of_face_automorphism(
                    element, face
                )
                is not None
            )
            .cardinality()
        )
        for element in automorphisms
    )

    assert int(square.geometric_automorphisms().order()) == 8
    assert kept_edges.count(4) == 1
    assert kept_edges.count(2) == 2
    assert kept_edges.count(0) == 5
    for face in _faces_below_the_top(square):
        assert square.geometric_lifts_of_face_automorphism(identity, face) == face.geometric_automorphisms().one()
