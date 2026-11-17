r"""Face automorphisms as rank-preserving order maps of the face object.

An abstract automorphism of a polytope is a self-isomorphism of the exact finite
graded poset of its faces: a forward and an inverse rank-preserving order map of
that poset.  The group is the categorical ``Aut`` of the face object itself, so a
face poset presented without any polyhedral computation still answers it, and the
geometric group maps into that same object.

The square `\operatorname{conv}\{(\pm 1, \pm 1)\}` is the specimen: its reflection
in the vertical axis is one explicit affine automorphism whose images of the
vertices and the edges are known independently of this library, and whose face
action fixes the top face and the empty face.
"""

from sage_extensions.all import *


def _square():
    return ConvexPolytopes(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))


def _corner(polytope, coordinates):
    r"""The vertex of ``polytope`` at ``coordinates`` in its ambient space."""
    point = polytope.ambient_space()(coordinates)
    return next(
        vertex
        for vertex in polytope.vertices()
        if polytope.rational_point(vertex) == point
    )


def _face_spanning(polytope, corners):
    r"""The face of ``polytope`` whose vertices are exactly ``corners``."""
    return next(
        face
        for face in polytope.face_poset()
        if all(
            (corner in corners) == face.contains_point(corner)
            for corner in polytope.vertices()
        )
    )


def test_the_empty_face_poset_answers_its_own_automorphism_group() -> None:
    r"""The two-face graded poset of a point answers ``Aut`` with no polyhedral datum.

    A zero-dimensional polytope has the empty face below its vertex, so its face
    poset is the two-element chain; its only automorphism is the identity, and it
    is an automorphism of that poset itself, not a permutation of something else.
    """
    polytope = AbstractPolytopes().an_object()
    automorphisms = polytope.abstract_automorphisms()

    assert automorphisms.order() == 1
    assert automorphisms.one() in automorphisms
    assert automorphisms.one()(tuple(polytope.faces(0))[0]) == tuple(polytope.faces(0))[0]
    assert automorphisms.one()(tuple(polytope.faces(-1))[0]) == tuple(polytope.faces(-1))[0]


def test_an_abstract_automorphism_is_a_pair_of_rank_preserving_order_maps() -> None:
    r"""An element of ``Aut`` of a face poset is an isomorphism of the poset itself.

    The forward arrow of an abstract automorphism is a rank-preserving monotone
    self-map of the face object, its inverse is one too, and the two compose to
    the identity of that object: the element is a categorical isomorphism and not
    a permutation of the faces carrying no rank or order data.
    """
    square = _square()
    face_poset = square.face_poset()
    automorphisms = square.abstract_automorphisms()

    assert automorphisms.order() == 8
    order_maps = FiniteGradedPosets().Mor(face_poset, face_poset)
    identity = order_maps.identity()
    assert tuple(automorphisms)
    for element in tuple(automorphisms):
        forward = element.forward()
        inverse = element.inverse().forward()
        assert element.parent() is automorphisms
        assert forward.parent() is order_maps
        assert inverse.parent() is order_maps
        assert inverse * forward == identity
        assert forward * inverse == identity
        assert all(forward(face) in face_poset for face in face_poset)
        assert all(
            face_poset.grade(forward(face)) == face_poset.grade(face)
            for face in face_poset
        )


def test_the_geometric_group_maps_into_the_face_objects_own_automorphisms() -> None:
    r"""The induced map's codomain is the abstract group retained on the face object.

    ``geometric_to_abstract_automorphisms`` is a group map from the affine
    symmetries to the very object :meth:`abstract_automorphisms` returns, and its
    values are automorphisms of that face poset; the map preserves multiplication.
    """
    square = _square()
    geometric = square.geometric_automorphisms()
    abstract = square.abstract_automorphisms()
    induced = square.geometric_to_abstract_automorphisms()

    assert induced.domain() is geometric
    assert induced.codomain() is abstract
    assert abstract is square.face_poset().Aut()
    assert induced(geometric.one()) == abstract.one()
    assert all(
        induced(element).forward().parent()
        is FiniteGradedPosets().Mor(square.face_poset(), square.face_poset())
        for element in tuple(geometric)
    )
    assert all(
        induced(left * right) == induced(left) * induced(right)
        for left in tuple(geometric)
        for right in tuple(geometric)
    )


def test_the_vertical_reflection_of_the_square_permutes_its_faces() -> None:
    r"""`(x,y) \mapsto (-x,y)` fixes the top and empty faces and swaps the edges' sides.

    The reflection's images are known without asking this library: it carries
    `(-1,-1)` to `(1,-1)` and `(-1,1)` to `(1,1)`, so it carries the left edge to
    the right edge and keeps the bottom and top edges; the square and the empty
    face are fixed by every automorphism of the face poset.
    """
    square = _square()
    lower_left = _corner(square, (-1, -1))
    lower_right = _corner(square, (1, -1))
    upper_left = _corner(square, (-1, 1))
    upper_right = _corner(square, (1, 1))
    reflection = next(
        element
        for element in tuple(square.geometric_automorphisms())
        if element(lower_left) == lower_right
        and element(upper_left) == upper_right
        and element(lower_right) == lower_left
        and element(upper_right) == upper_left
    )
    induced = square.geometric_to_abstract_automorphisms()(reflection)
    left_edge = _face_spanning(square, (lower_left, upper_left))
    right_edge = _face_spanning(square, (lower_right, upper_right))
    bottom_edge = _face_spanning(square, (lower_left, lower_right))
    top_edge = _face_spanning(square, (upper_left, upper_right))
    empty_face = _face_spanning(square, ())

    assert induced(left_edge) == right_edge
    assert induced(right_edge) == left_edge
    assert induced(bottom_edge) == bottom_edge
    assert induced(top_edge) == top_edge
    assert induced(square) == square
    assert induced(empty_face) == empty_face
    assert induced(_face_spanning(square, (lower_left,))) == _face_spanning(
        square, (lower_right,)
    )
    assert induced(_face_spanning(square, (upper_left,))) == _face_spanning(
        square, (upper_right,)
    )
    assert induced.forward()(left_edge) == right_edge
    assert induced.inverse().forward()(right_edge) == left_edge


def test_a_face_answers_for_a_point_written_by_its_coordinates() -> None:
    r"""A lattice vertex and the ambient point at its coordinates are one point.

    A polytope of this category is presented in coordinates, and a lattice vertex
    includes into the rational ambient space keeping them, so a face answers for
    either form: `(1, -1)` is the lower right vertex of the square and `(0, 0)` is
    an interior point of the square but not of that vertex.
    """
    square = _square()
    lower_right_face = _face_spanning(square, (_corner(square, (1, -1)),))

    assert square.contains_point((1, -1)) is True
    assert square.contains_point((0, 0)) is True
    assert square.contains_point((2, 0)) is False
    assert square.interior_contains_point((0, 0)) is True
    assert lower_right_face.contains_point((1, -1)) is True
    assert lower_right_face.contains_point((0, 0)) is False


def test_the_stored_sterk2_polygon_answers_its_face_action() -> None:
    r"""Sterk's stored `II_{18,0,0}` polygon: 17 edges of a cycle, so 34 moves.

    The plotting source walks seventeen boundary directions from the origin and
    takes the hull, and the stored lengths make one of those steps zero, so the
    stored specimen's hull has seventeen vertices and seventeen edges and its face
    lattice is a cycle of seventeen.  A cycle's automorphism group is dihedral of
    order `2 * 17`, which is the abstract group of that face lattice, while the
    restricted affine symmetries of this hull are a proper subgroup of it; the
    induced map is therefore injective and not onto.
    """
    polygon = Sterk.sterk2_polygon(ZZ.free_module(2))
    face_poset = polygon.face_poset()
    geometric = polygon.geometric_automorphisms()
    abstract = polygon.abstract_automorphisms()
    induced = polygon.geometric_to_abstract_automorphisms()

    assert int(polygon.n_vertices()) == 17
    assert face_poset.faces(0).cardinality() == 17
    assert face_poset.faces(1).cardinality() == 17
    assert abstract.order() == 2 * 17
    assert geometric.order() < abstract.order()
    assert induced.domain() is geometric
    assert induced.codomain() is abstract
    assert abstract is face_poset.Aut()
    assert induced(geometric.one()) == abstract.one()
    assert all(
        induced(left * right) == induced(left) * induced(right)
        for left in tuple(geometric)
        for right in tuple(geometric)
    )
    assert all(
        induced(element).forward().parent()
        is FiniteGradedPosets().Mor(face_poset, face_poset)
        for element in tuple(geometric)
    )
    assert induced.is_injective() is True
    assert induced.is_surjective() is False
