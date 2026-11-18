r"""A lattice point reaches a polytope's own ingress: `in`, `P(v)` and `contains_point` agree.

A convex polytope of the lattice `M` is a subset of its ambient space
`M \otimes \mathbf{Q}`, and `M` includes into that space by keeping coordinates,
so a lattice point and the ambient point at the same coordinates are one point of
the ambient space.  `contains_point` reads its argument through that conversion;
this file states that the ordinary subset tests -- membership `v in P` and the
element constructor `P(v)` -- answer the same thing about the same point, so a
caller of either route and a caller of the named operation get one decision.

The specimens are the three of the polytope lanes: the square
`\operatorname{conv}\{(\pm 1, \pm 1)\}`, the irregular quadrangle
`\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}` and the stored Sterk2 hull.

Each point is placed in the polytope by the mathematics and not by the library's
answer: a vertex is a point of its polytope, a convex combination of two vertices
is a point of it because a polytope is convex, a vertex of a face is a point of
that face, and a point whose every coordinate exceeds every coordinate of every
vertex is outside -- a point of a polytope is a convex combination of its
vertices, so each of its coordinates lies between the vertices' extremes.
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


def _labels(polytope):
    r"""The coordinate labels of the polytope's ambient space."""
    return tuple(polytope.ambient_space().module_generating_set())


def _a_vertex(polytope):
    r"""One vertex of ``polytope``, as the lattice point it is."""
    return tuple(polytope.vertices())[0]


def _an_ambient_point_between(polytope, left, right, weight):
    r"""The point ``(1-weight) left + weight right``, written in ambient coordinates.

    Both ends are points of the polytope, so this one is: a polytope is convex.
    Its coordinates are rational and need not be integral, and being integral
    would not make it another point -- a lattice point is the ambient point at
    its coordinates.
    """
    labels = _labels(polytope)
    left_coordinates = polytope.rational_point(left).to_vector()
    right_coordinates = polytope.rational_point(right).to_vector()
    remainder = QQ(1) - weight
    return polytope.rational_point(
        tuple(
            remainder * QQ(left_coordinates(label))
            + weight * QQ(right_coordinates(label))
            for label in labels
        )
    )


def _a_point_beyond_every_vertex(polytope):
    r"""A lattice point whose every coordinate exceeds every vertex's coordinate.

    A point of a polytope is a convex combination of its vertices, so each of its
    coordinates lies between the corresponding coordinates of the vertices; this
    point's do not, so it is not a point of the polytope.
    """
    coordinates = tuple(
        vertex.to_vector()(label)
        for vertex in polytope.vertices()
        for label in _labels(polytope)
    )
    bound = QQ(1) + max(QQ(coordinate) for coordinate in coordinates)
    return polytope.ambient_lattice()(tuple(bound for _label in _labels(polytope)))


def _the_three_routes_agree_that(polytope, point, member):
    r"""``in``, ``P(point)`` and ``contains_point`` answer ``member`` about ``point``.

    ``member`` is placed by the caller from the mathematics of the specimen, not
    read off the library: what is asserted is that the two ordinary subset tests
    answer what the named operation answers, and that this is the true answer.
    """
    assert polytope.contains_point(point) is member
    assert (point in polytope) is member
    if member:
        assert polytope(point) == polytope.rational_point(point)
    else:
        with pytest.raises(ValueError):
            polytope(point)


def test_a_lattice_vertex_is_a_point_of_its_polytope_through_every_route() -> None:
    r"""A vertex of a lattice polytope is one of its points, by membership and by call.

    The vertex is a lattice point, and `contains_point` already answered for it;
    membership and the element constructor answer for it too, and the point `P`
    returns is the ambient point at the vertex's coordinates.
    """
    for polytope in _specimens():
        vertex = _a_vertex(polytope)
        _the_three_routes_agree_that(polytope, vertex, True)
        assert polytope(vertex) == polytope.rational_point(vertex)


def test_a_point_of_the_ambient_space_is_a_point_of_the_polytope_that_contains_it() -> None:
    r"""A rational point of the ambient space inside the polytope is one of its points.

    The point is the midpoint of the segment between two vertices, so the
    polytope contains it; all three routes say so, and the point the constructor
    returns is that same point of the ambient space.
    """
    weight = QQ(1) / QQ(2)
    for polytope in _specimens():
        first, second = tuple(polytope.vertices())[:2]
        point = _an_ambient_point_between(polytope, first, second, weight)
        _the_three_routes_agree_that(polytope, point, True)
        assert polytope(point) == point


def test_a_point_outside_the_polytope_is_refused_by_every_route() -> None:
    r"""A lattice point beyond every vertex is no point of the polytope.

    Neither membership nor `contains_point` admits it, and the element
    constructor refuses it rather than answering a point.
    """
    for polytope in _specimens():
        outside = _a_point_beyond_every_vertex(polytope)
        _the_three_routes_agree_that(polytope, outside, False)


def test_a_vertex_of_a_face_is_a_point_of_that_face_through_every_route() -> None:
    r"""Every face of a polytope is a polytope, and its own ingress admits its vertices.

    The faces of a lattice polytope are lattice polytopes, so a vertex of a face
    is a lattice point of that face; its membership, its element constructor and
    its `contains_point` are one answer there as well.
    """
    for polytope in _specimens():
        faces = tuple(polytope.faces(0)) + tuple(polytope.faces(1)) + tuple(
            polytope.faces(2)
        )
        assert faces
        for face in faces:
            vertex = _a_vertex(face)
            _the_three_routes_agree_that(face, vertex, True)
