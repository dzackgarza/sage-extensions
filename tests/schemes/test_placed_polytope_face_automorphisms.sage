r"""Placed polytopes: their face object, their geometric automorphisms and the map between.

A placed polytope is a convex polytope placed in a real affine space with a
selected lattice.  Its faces are read on the face object of the polytope it
places, its geometric automorphisms are the affine automorphisms of that ambient
space carrying it onto itself -- with linear parts acting on the selected lattice
-- and the map from them to the abstract automorphisms is the faces' map each of
them induces.

The square `\operatorname{conv}\{(\pm 1, \pm 1)\}` has eight of each, and the
irregular quadrangle `\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}` has the
dihedral group of order eight as its combinatorial group and only the identity as
its geometric one.
"""

from sage_extensions.all import *


def _placed_category():
    r"""The category of lattice polygons placed in `\mathbf{R}^2` with the lattice `\mathbf{Z}^2`."""
    vector_space = RealVectorSpaces(2).an_object()
    affine_space = RealVectorSpaces(2).affinization()(vector_space)
    lattice = ZZ.free_module(2)
    labels = tuple(lattice.module_generating_set())
    inclusion = Sets().Mor(lattice, vector_space)(
        lambda vector: vector_space(
            tuple(RR(vector.to_vector()(label)) for label in labels)
        )
    )
    return LatticePolytopesIn(AffineSpacesWithLattice().on(affine_space, inclusion))


def _placed(category, polytope):
    r"""``polytope`` placed in ``category``'s ambient space by its lattice."""
    return category.on(
        ("vertices", polytope.vertices()),
        category.canonical_placement(polytope),
    )


def _square():
    return LatticePolygons(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))


def _placed_point(placed, coordinates):
    r"""The placed image of the underlying polytope's vertex at ``coordinates``."""
    underlying = placed.underlying_polytope()
    corner = next(
        vertex
        for vertex in underlying.vertices()
        if underlying.rational_point(vertex) == underlying.ambient_space()(coordinates)
    )
    return placed.ambient_inclusion()(underlying.rational_point(corner))


def _edge_spanning(polytope, corners):
    r"""The edge of ``polytope``'s face object whose vertices are exactly ``corners``."""
    coordinates = tuple(polytope.ambient_space()(corner) for corner in corners)
    return next(
        face
        for face in polytope.face_poset().faces(1)
        if all(
            (polytope.rational_point(vertex) in coordinates)
            == face.contains_point(vertex)
            for vertex in polytope.vertices()
        )
    )


def test_the_placed_square_keeps_its_polytope_and_answers_its_face_object() -> None:
    r"""A placed square is placed, not copied, and answers for that polytope's faces.

    The placed polytope retains the polytope it places and the map that places it,
    so the face object it answers is that polytope's own: ten faces, the top face
    that polytope, and the eight automorphisms of a four-cycle.  Its geometric
    automorphisms are eight affine automorphisms of the ambient space, and the map
    between the two groups is onto here: the square's symmetries realize all of
    its combinatorial ones.
    """
    category = _placed_category()
    square = _square()
    placed = _placed(category, square)
    face_poset = placed.face_poset()
    geometric = placed.geometric_automorphisms()
    abstract = placed.abstract_automorphisms()
    induced = placed.geometric_to_abstract_automorphisms()

    assert placed in category
    assert placed.underlying_polytope() is square
    assert face_poset is square.face_poset()
    assert tuple(face_poset)[-1] is square
    assert face_poset.faces(0).cardinality() == 4
    assert face_poset.faces(1).cardinality() == 4
    assert abstract.order() == 8
    assert geometric.order() == 8
    assert induced.domain() is geometric
    assert induced.codomain() is abstract
    assert induced(geometric.one()) == abstract.one()
    assert all(
        induced(left * right) == induced(left) * induced(right)
        for left in tuple(geometric.group_generators())
        for right in tuple(geometric.group_generators())
    )
    assert all(
        induced(~element) == ~induced(element) for element in tuple(geometric)
    )
    assert induced.is_injective() is True
    assert induced.is_surjective() is True
    assert all(
        frozenset(
            element.underlying_polytope_morphism()(square.rational_point(vertex))
            for vertex in square.vertices()
        )
        == frozenset(square.rational_point(vertex) for vertex in square.vertices())
        for element in tuple(geometric)
    )


def test_the_placed_irregular_quadrangle_has_dihedral_combinatorics_only() -> None:
    r"""`\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}`: eight combinatorial, one affine.

    The quadrangle's face object is a four-cycle, whose automorphism group is
    dihedral of order eight; its only affine automorphism is the identity, so the
    placed polytope's geometric group is trivial and the map between the two
    groups is not onto.  The two groups are different objects and the induced map
    does not confuse them.
    """
    category = _placed_category()
    quadrangle = LatticePolygons(ZZ.free_module(2))(((0, 0), (1, 0), (0, 1), (2, 3)))
    placed = _placed(category, quadrangle)
    geometric = placed.geometric_automorphisms()
    abstract = placed.abstract_automorphisms()
    induced = placed.geometric_to_abstract_automorphisms()

    assert abstract.order() == 8
    assert geometric.order() == 1
    assert tuple(induced(element) for element in tuple(geometric)) == (abstract.one(),)
    assert induced.is_surjective() is False


def test_the_placed_square_reflection_acts_on_the_ambient_space_and_the_faces() -> None:
    r"""The reflection `(x,y) \mapsto (-x,y)` is one ambient automorphism of the placed square.

    Its images are known without asking this library: it carries the placed vertex
    `(-1,-1)` to `(1,-1)` and `(-1,1)` to `(1,1)`, so the left edge goes to the
    right one while the bottom and the top edges stay, and the square and the empty
    face do not move.  Its ambient map is an arrow of the affine space with the
    selected lattice and its linear part is the diagonal matrix of `-1` and `1` on
    that lattice, so it is a symmetry of the lattice and not of the affine space
    alone; the group's own inverse and product act as they say.
    """
    category = _placed_category()
    square = _square()
    placed = _placed(category, square)
    geometric = placed.geometric_automorphisms()
    induced = placed.geometric_to_abstract_automorphisms()
    lower_left = _placed_point(placed, (-1, -1))
    lower_right = _placed_point(placed, (1, -1))
    upper_left = _placed_point(placed, (-1, 1))
    upper_right = _placed_point(placed, (1, 1))
    reflection = next(
        element
        for element in tuple(geometric)
        if element(lower_left) == lower_right
        and element(lower_right) == lower_left
        and element(upper_left) == upper_right
        and element(upper_right) == upper_left
    )
    lattice = category.ambient_space().affine_lattice()
    labels = tuple(lattice.module_generating_set())
    left_edge = _edge_spanning(square, ((-1, -1), (-1, 1)))
    right_edge = _edge_spanning(square, ((1, -1), (1, 1)))
    bottom_edge = _edge_spanning(square, ((-1, -1), (1, -1)))
    top_edge = _edge_spanning(square, ((-1, 1), (1, 1)))
    empty_face = tuple(placed.face_poset().faces(-1))[0]
    faces = induced(reflection)

    assert reflection.ambient_map().lattice_map()(
        lattice.module_generator(labels[0])
    ) == -lattice.module_generator(labels[0])
    assert reflection.ambient_map().lattice_map()(
        lattice.module_generator(labels[1])
    ) == lattice.module_generator(labels[1])
    assert faces(left_edge) == right_edge
    assert faces(right_edge) == left_edge
    assert faces(bottom_edge) == bottom_edge
    assert faces(top_edge) == top_edge
    assert faces(_edge_spanning(square, ((1, -1), (1, 1)))) == left_edge
    assert faces(square) == square
    assert faces(empty_face) == empty_face
    assert (~reflection)(reflection(lower_left)) == lower_left
    assert (reflection * reflection)(lower_left) == lower_left
    assert (reflection * ~reflection)(lower_left) == lower_left


def test_the_placed_sterk2_polygon_answers_its_face_action() -> None:
    r"""The stored Sterk2 hull placed: 34 combinatorial moves and two affine ones.

    The stored specimen's hull has seventeen edges, so its face object's
    automorphism group is dihedral of order 34, while its restricted affine
    automorphisms are two; the placed polytope answers both and the map from the
    second into the first is injective and not onto.
    """
    category = _placed_category()
    polygon = Sterk.sterk2_polygon(ZZ.free_module(2))
    placed = _placed(category, polygon)
    geometric = placed.geometric_automorphisms()
    abstract = placed.abstract_automorphisms()
    induced = placed.geometric_to_abstract_automorphisms()

    assert int(polygon.n_vertices()) == 17
    assert placed.face_poset().faces(1).cardinality() == 17
    assert abstract.order() == 2 * 17
    assert geometric.order() == 2
    assert induced.codomain() is abstract
    assert induced.is_injective() is True
    assert induced.is_surjective() is False
