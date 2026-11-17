r"""Face posets and face automorphism groups of rational polytopes.

A polytope's faces are the polytopes its defining inequalities cut out, and they
are ordered by inclusion, which grades them by affine dimension with the empty
face of dimension `-1`.  Its abstract automorphisms are the rank-preserving
automorphisms of that graded face poset, and its geometric ones are the affine
automorphisms of the ambient space carrying the polytope onto itself.

The square `\operatorname{conv}\{(\pm 1, \pm 1)\}` has dihedral symmetry of order
eight acting on its ten faces.  The irregular quadrangle
`\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}` has the same dihedral
combinatorial group and no nontrivial affine symmetry, which separates the two
groups.
"""

from sage_extensions.all import *


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


def test_the_face_poset_of_a_square_grades_its_ten_faces_by_dimension() -> None:
    r"""The square has one empty face, four vertices, four edges and itself.

    A polygon's face poset is the empty face, its vertices, its edges and the
    polygon, graded by dimension `-1, 0, 1, 2`; the top face is the polygon
    itself, so the face poset retains the supplied polytope.
    """
    square = ConvexPolytopes(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))
    face_poset = square.face_poset()

    assert face_poset.faces(-1).cardinality() == 1
    assert face_poset.faces(0).cardinality() == 4
    assert face_poset.faces(1).cardinality() == 4
    assert face_poset.faces(2).cardinality() == 1
    assert tuple(face_poset.faces(2))[0] is square
    assert all(int(face_poset.grade(face)) == 0 for face in face_poset.faces(0))


def test_the_face_poset_of_a_square_orders_faces_by_their_vertices() -> None:
    r"""An edge lies on exactly its two vertices, and every face lies in the square.

    A face is the convex hull of its vertices, so one face lies in another
    exactly when its vertices are among the other's: the empty face lies in
    everything, the left edge lies on the two left vertices and in the square,
    and the square does not lie in the left edge.
    """
    square = ConvexPolytopes(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))
    face_poset = square.face_poset()
    order = face_poset.underlying_graded_poset().underlying_poset()
    empty_face = _face_spanning(square, ())
    lower_left = _corner(square, (-1, -1))
    upper_left = _corner(square, (-1, 1))
    lower_left_face = _face_spanning(square, (lower_left,))
    upper_left_face = _face_spanning(square, (upper_left,))
    left_edge = _face_spanning(square, (lower_left, upper_left))

    assert face_poset.grade(empty_face) == -1
    assert int(face_poset.grade(left_edge)) == 1
    assert order.le(empty_face, left_edge)
    assert order.le(lower_left_face, left_edge)
    assert order.le(left_edge, square)
    assert order.le(square, left_edge) is False
    assert order.le(left_edge, upper_left_face) is False
    assert square.vertices().filtered(
        lambda vertex: left_edge.contains_point(vertex)
    ).cardinality() == 2
    assert face_poset.faces(1).filtered(
        lambda edge: edge.contains_point(_corner(square, (1, 1)))
    ).cardinality() == 2


def test_the_square_has_eight_abstract_and_eight_geometric_automorphisms() -> None:
    r"""The square's dihedral group is both its face-poset and its affine symmetry group.

    Four vertices and four edges give a dihedral group of order eight, and every
    one of its elements is realized by an affine automorphism of the square, so
    the geometric group has the same eight elements as the abstract one.
    """
    square = ConvexPolytopes(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))

    assert square.abstract_automorphisms().order() == 8
    assert square.geometric_automorphisms().order() == 8
    assert square.geometric_to_abstract_automorphisms()(
        square.geometric_automorphisms().one()
    ) == square.abstract_automorphisms().one()


def test_a_quarter_turn_of_the_square_permutes_its_faces() -> None:
    r"""The quarter turn `(x,y) \mapsto (-y,x)` takes the left edge to the bottom one.

    The corner `(-1,-1)` goes to `(1,-1)` and `(1,-1)` to `(1,1)`, so the left
    edge, on the two left vertices, goes to the bottom edge, on the two bottom
    ones; the square and its empty face are fixed, as a bijection of the face
    poset preserves both ends.
    """
    square = ConvexPolytopes(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))
    lower_left = _corner(square, (-1, -1))
    lower_right = _corner(square, (1, -1))
    upper_left = _corner(square, (-1, 1))
    upper_right = _corner(square, (1, 1))
    quarter_turn = next(
        element
        for element in tuple(square.geometric_automorphisms())
        if element(lower_left) == lower_right and element(lower_right) == upper_right
    )
    induced = square.geometric_to_abstract_automorphisms()(quarter_turn)
    left_edge = _face_spanning(square, (lower_left, upper_left))
    bottom_edge = _face_spanning(square, (lower_left, lower_right))
    empty_face = _face_spanning(square, ())

    assert induced(_face_spanning(square, (lower_left,))) == _face_spanning(
        square, (lower_right,)
    )
    assert induced(_face_spanning(square, (upper_left,))) == _face_spanning(
        square, (lower_left,)
    )
    assert induced(_face_spanning(square, (upper_right,))) == _face_spanning(
        square, (upper_left,)
    )
    assert induced(left_edge) == bottom_edge
    assert induced(square) == square
    assert induced(empty_face) == empty_face


def test_the_induced_face_action_of_a_square_preserves_composition() -> None:
    r"""The face action is a homomorphism of the geometric group onto the abstract one.

    Composing two affine automorphisms composes the permutations of the faces
    they induce, the identity induces the identity, and inverses induce
    inverses; the induced map is onto here, since the square's eight affine
    symmetries realize all eight combinatorial ones.
    """
    square = ConvexPolytopes(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))
    geometric = square.geometric_automorphisms()
    abstract = square.abstract_automorphisms()
    induced = square.geometric_to_abstract_automorphisms()
    elements = tuple(geometric)

    assert all(
        induced(left * right) == induced(left) * induced(right)
        for left in elements
        for right in elements
    )
    assert all(induced(~element) == ~induced(element) for element in elements)
    assert induced(geometric.one()) == abstract.one()
    assert abstract.subgroup(frozenset(induced(element) for element in elements)).order() == 8


def test_a_cube_has_the_octahedral_group_on_its_twenty_six_faces() -> None:
    r"""The `3`-cube has eight vertices, twelve edges, six facets and itself.

    The face poset of `[-1,1]^3` is graded `-1, 0, 1, 2, 3` with `1, 8, 12, 6, 1`
    faces, and its automorphism group is the full octahedral group of order `48`,
    every element of which is realized by an affine automorphism of the cube.
    """
    cube = ConvexPolytopes(ZZ.free_module(3))(
        tuple(
            (x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)
        )
    )
    face_poset = cube.face_poset()

    assert face_poset.faces(-1).cardinality() == 1
    assert face_poset.faces(0).cardinality() == 8
    assert face_poset.faces(1).cardinality() == 12
    assert face_poset.faces(2).cardinality() == 6
    assert face_poset.faces(3).cardinality() == 1
    assert cube.abstract_automorphisms().order() == 48
    assert cube.geometric_automorphisms().order() == 48
    assert cube.geometric_to_abstract_automorphisms()(
        cube.geometric_automorphisms().one()
    ) == cube.abstract_automorphisms().one()


def test_the_irregular_quadrangle_has_dihedral_combinatorics_and_no_affine_symmetry() -> None:
    r"""`\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}` is combinatorially but not affinely symmetric.

    Its eight combinatorial automorphisms are the symmetries of its incidence
    graph, and its only affine automorphism is the identity, so the geometric
    group is trivial inside a dihedral abstract group and the induced map is not
    onto.
    """
    quadrangle = ConvexPolytopes(ZZ.free_module(2))(((0, 0), (1, 0), (0, 1), (2, 3)))
    geometric = quadrangle.geometric_automorphisms()
    abstract = quadrangle.abstract_automorphisms()

    assert abstract.order() == 8
    assert geometric.order() == 1
    assert tuple(
        quadrangle.geometric_to_abstract_automorphisms()(element)
        for element in tuple(geometric)
    ) == (abstract.one(),)


def test_a_translated_square_keeps_eight_affine_symmetries() -> None:
    r"""`[1,2]^2` has eight affine automorphisms although it is not centred at the origin.

    Its symmetries are affine maps with translations, not linear ones, so the
    geometric group is a group of affine automorphisms of the ambient space and
    not the stabilizer of an origin.
    """
    translated = ConvexPolytopes(ZZ.free_module(2))(
        ((1, 1), (1, 2), (2, 2), (2, 1))
    )

    assert translated.abstract_automorphisms().order() == 8
    assert translated.geometric_automorphisms().order() == 8


def test_a_segment_in_the_plane_is_graded_by_its_own_dimension() -> None:
    r"""`\operatorname{conv}\{(0,0),(1,0)\}` has faces in dimensions `-1, 0, 1` only.

    A polytope of lower dimension than its ambient space keeps the ambient
    lattice, and its faces are graded by their own affine dimension, so there is
    no face of dimension two.
    """
    segment = ConvexPolytopes(ZZ.free_module(2))(((0, 0), (1, 0)))
    face_poset = segment.face_poset()

    assert face_poset.faces(-1).cardinality() == 1
    assert face_poset.faces(0).cardinality() == 2
    assert face_poset.faces(1).cardinality() == 1
    assert face_poset.faces(2).cardinality() == 0
    assert tuple(face_poset.faces(1))[0] is segment
    assert segment.abstract_automorphisms().order() == 2
    assert segment.geometric_automorphisms().order() == 2
