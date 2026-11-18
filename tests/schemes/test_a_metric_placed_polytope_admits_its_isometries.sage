r"""A placed Euclidean polytope admits exactly the ambient maps that are isometries.

A Euclidean space is a real affine space with a chosen inner product, and its
arrows are affine isometries: an affine map `x \mapsto A x + t` is one exactly
when `A` preserves the form, since a translation is an isometry of every
Euclidean space.  That decision is the metric space's own, and a placed
Euclidean polytope reads it: the reflection `(x,y) \mapsto (-x,y)` of the square
`\operatorname{conv}\{(\pm 1,\pm 1)\}` is an arrow of the placed square, of order
two, while the shear `(x,y) \mapsto (x+y,y)` is not one, although that very shear
is an arrow of the affine space the square is placed in.

The square's isometry group is the dihedral group of order eight, four
reflections and four rotations, known without asking this library; the two maps
below are named on the corners, and every assertion about them is an assertion
about where they carry a corner or an edge.
"""

import pytest

from sage_extensions.all import *


def _plane():
    r"""The Euclidean plane `\mathbf{R}^2` with `dx^2 + dy^2`, and its model space."""
    vector_space = RealVectorSpaces(2).an_object()
    affine_space = RealVectorSpaces(2).affinization()(vector_space)
    one, zero = RR.one(), RR.zero()
    inner_product = vector_space.bilinear_forms(RR)([[one, zero], [zero, one]])
    return vector_space, EuclideanSpaces().on(affine_space, inner_product)


def _square():
    return LatticePolygons(ZZ.free_module(2))(((-1, -1), (-1, 1), (1, 1), (1, -1)))


def _placement(polytope, space, vector_space):
    r"""Place ``polytope``'s points at the points of ``space`` with their coordinates."""
    labels = tuple(vector_space.module_generating_set())
    return Sets().Mor(polytope, space.point_set())(
        lambda point: vector_space(
            tuple(RR(point.to_vector()(label)) for label in labels)
        )
    )


def _euclidean_arrow(space, vector_space, images, offset=None):
    r"""The arrow of ``space`` whose linear part carries the ``i``-th generator to ``images[i]``.

    The affine space is canonically based, so a linear map of the model is the
    affine map fixing the origin, and the isometry is that linear map and the
    point map it induces; ``offset`` translates that point map, so the map is
    `x \\mapsto A x + t` with `t` the offset.
    """
    labels = tuple(vector_space.module_generating_set())
    linear_part = vector_space.Mor(vector_space)(
        lambda label: images[labels.index(label)]
    )
    affine_space = space.underlying_affine_space()
    if offset is None:
        point_map = lambda point: linear_part(point)
    else:
        point_map = lambda point: space.translation_action()(linear_part(point), offset)
    return EuclideanSpaces().Mor(space, space)(
        RealAffineSpaces().Mor(affine_space, affine_space)(
            linear_part,
            Sets().Mor(space.point_set(), space.point_set())(point_map),
        )
    )


def _line_arrow(space, model, affine_space, scale, shift):
    r"""The arrow ``x \\mapsto scale * x + shift`` of a Euclidean line."""
    linear_part = model.Mor(model)(
        lambda label: scale * model.module_generator(label)
    )
    return EuclideanSpaces().Mor(space, space)(
        RealAffineSpaces().Mor(affine_space, affine_space)(
            linear_part,
            Sets().Mor(affine_space.point_set(), affine_space.point_set())(
                lambda point: space.translation_action()(
                    linear_part(point), model((shift,))
                )
            ),
        )
    )


def _circle(space, center, radius):
    r"""The round circle of ``space`` with this centre and radius, as a selected sphere."""
    inner_product = space.model_inner_product()
    points = space.point_set()
    return SphericalSpaces().in_space(
        space,
        center,
        radius,
        points.condition_set(
            lambda point: inner_product(
                space.difference(point, center), space.difference(point, center)
            )
            == radius * radius
        ).inclusion(),
    )


def _edge_spanning(polytope, corners):
    r"""The edge of ``polytope``'s face object whose vertices are exactly ``corners``."""
    coordinates = tuple(polytope.ambient_space()(corner) for corner in corners)
    return next(
        face
        for face in polytope.face_poset().faces(1)
        if all(
            (polytope.rational_point(vertex) in coordinates) == face.contains_point(vertex)
            for vertex in polytope.vertices()
        )
    )


def test_the_euclidean_owner_decides_an_isometry_from_its_inner_product() -> None:
    r"""The metric owner answers on a reflection, a shear and a dilation.

    The reflection in the `y`-axis and the shear `(x,y) \mapsto (x+y,y)` are
    both affine automorphisms of the plane, and only the first preserves
    `dx^2 + dy^2`: `b(e_0 + e_1, e_0 + e_1) = 2` while `b(e_0, e_0) = 1`.  The
    dilation by two moves every norm, so it is not an isometry either.
    """
    vector_space, space = _plane()
    (first, second) = vector_space.module_generators()

    assert space.is_an_isometry(
        _euclidean_arrow(space, vector_space, (-first, second))
    ) is True
    assert space.is_an_isometry(_euclidean_arrow(space, vector_space, (first + second, second))) is False
    assert space.is_an_isometry(_euclidean_arrow(space, vector_space, (first + first, second))) is False


def test_the_euclidean_owner_states_an_inhabitant_and_refuses_a_foreign_arrow() -> None:
    r"""The owner names one of its spaces, and decides only about its own arrows.

    The line `(\mathbf{R}, dx^2)` is a Euclidean space: one-dimensional, with the
    unit generator of norm one.  The decision at the plane is a decision about
    the plane's own arrows, so an arrow of the plane's underlying affine space
    is refused there rather than answered: the affine space states no metric and
    the plane's metric is not the form of a map of it.
    """
    vector_space, space = _plane()
    line = EuclideanSpaces().an_object()
    (generator,) = line.model_vector_space().module_generators()

    assert line in EuclideanSpaces()
    assert line.model_vector_space().dimension() == 1
    assert line.model_inner_product()(generator, generator) == RR.one()

    affine_space = space.underlying_affine_space()
    (first, second) = vector_space.module_generators()
    linear_part = vector_space.Mor(vector_space)(lambda label: -first if label == 0 else second)
    affine_reflection = RealAffineSpaces().Mor(affine_space, affine_space)(
        linear_part,
        Sets().Mor(space.point_set(), space.point_set())(lambda point: linear_part(point)),
    )
    with pytest.raises(ValueError):
        space.is_an_isometry(affine_reflection)


def test_the_placed_square_admits_its_reflection_and_it_has_order_two() -> None:
    r"""The reflection in the `y`-axis is an arrow of the placed square, of order two.

    It carries the corner `(-1,-1)` to `(1,-1)` and `(-1,1)` to `(1,1)`, so the
    left edge goes to the right one and back, and the bottom and top edges stay.
    Being its own inverse it is of order two, and not of order one: it moves a
    corner of the square.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    polygon = _square()
    placed = category.on(
        ("vertices", polygon.vertices()), _placement(polygon, space, vector_space)
    )
    (first, second) = vector_space.module_generators()
    reflection = _euclidean_arrow(space, vector_space, (-first, second))
    lower_left = vector_space((-1, -1))
    lower_right = vector_space((1, -1))
    upper_left = vector_space((-1, 1))
    upper_right = vector_space((1, 1))
    left_edge = _edge_spanning(polygon, ((-1, -1), (-1, 1)))
    right_edge = _edge_spanning(polygon, ((1, -1), (1, 1)))
    bottom_edge = _edge_spanning(polygon, ((-1, -1), (1, -1)))
    top_edge = _edge_spanning(polygon, ((-1, 1), (1, 1)))
    faces = tuple(placed.abstract_automorphisms())
    face_map = next(
        candidate
        for candidate in faces
        if candidate(left_edge) == right_edge
        and candidate(right_edge) == left_edge
        and candidate(bottom_edge) == bottom_edge
    )

    arrow = category.Mor(placed, placed)(reflection, face_map)

    assert arrow.ambient_isometric_embedding()(lower_left) == lower_right
    assert arrow(lower_left) == lower_right
    assert arrow(upper_left) == upper_right
    assert arrow(lower_right) == lower_left
    assert (arrow * arrow)(lower_left) == lower_left
    assert (arrow * arrow)(upper_right) == upper_right
    assert arrow.face_poset_map()(left_edge) == right_edge
    assert arrow.face_poset_map()(bottom_edge) == bottom_edge
    assert arrow.face_poset_map()(top_edge) == top_edge


def test_the_placed_square_refuses_the_shear_the_affine_lane_admits() -> None:
    r"""The shear is no isometry, and the affine lane's answer is not the metric one.

    `(x,y) \mapsto (x+y,y)` is an affine automorphism of the plane and not an
    isometry of `dx^2 + dy^2`, so the placed Euclidean square refuses it.  The
    same map, forgotten to the affine space the square is placed in, is an arrow
    of the placed affine polytope on the same vertices and with the same faces'
    map: the refusal is the metric decision and not the affine one.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    polygon = _square()
    placed = category.on(
        ("vertices", polygon.vertices()), _placement(polygon, space, vector_space)
    )
    affine_space = space.underlying_affine_space()
    affine_category = ConvexPolytopesIn(affine_space)
    affine_placed = affine_category.on(
        ("vertices", polygon.vertices()),
        _placement(polygon, affine_space, vector_space),
    )
    (first, second) = vector_space.module_generators()
    shear = _euclidean_arrow(space, vector_space, (first + second, second))
    faces = tuple(placed.abstract_automorphisms())
    left_edge = _edge_spanning(polygon, ((-1, -1), (-1, 1)))
    right_edge = _edge_spanning(polygon, ((1, -1), (1, 1)))
    face_map = next(
        candidate
        for candidate in faces
        if candidate(left_edge) == right_edge and candidate(right_edge) == left_edge
    )

    with pytest.raises(ValueError):
        category.Mor(placed, placed)(shear, face_map)

    admitted = affine_category.Mor(affine_placed, affine_placed)(
        space.category().forget_metric()(shear), face_map
    )
    assert admitted(vector_space((-1, -1))) == vector_space((-1, -2))
    assert space.is_an_isometry(shear) is False


def test_the_placed_square_answers_its_geometric_automorphisms() -> None:
    r"""``Aut(P)`` on the Euclidean lane: eight arrows, each admitted by the metric owner.

    The square's isometry group is the dihedral group of order eight, and every
    one of its eight moves is an arrow of the placed Euclidean square: the place
    the arrows are admitted is ``MetricPolytopeMor``, which asks the Euclidean
    space whether the ambient map preserves `dx^2 + dy^2`.  The eight arrows are
    eight different isometries, and the reflection among them is the one no
    other isometry agrees with on the four corners.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    polygon = _square()
    placed = category.on(
        ("vertices", polygon.vertices()), _placement(polygon, space, vector_space)
    )
    geometric = placed.geometric_automorphisms()
    lower_left = vector_space((-1, -1))
    lower_right = vector_space((1, -1))
    upper_left = vector_space((-1, 1))
    upper_right = vector_space((1, 1))
    elements = tuple(geometric)
    reflection = next(
        element
        for element in elements
        if element(lower_left) == lower_right
        and element(lower_right) == lower_left
        and element(upper_left) == upper_right
        and element(upper_right) == upper_left
    )

    assert geometric.order() == 8
    assert placed.abstract_automorphisms().order() == 8
    assert all(space.is_an_isometry(element.ambient_map()) is True for element in elements)
    assert reflection(lower_left) == lower_right
    assert (reflection * reflection)(lower_left) == lower_left
    assert reflection(lower_left) != lower_left


def test_the_metric_lane_counts_the_isometries_and_not_the_affine_candidates() -> None:
    r"""A sheared square: its affine group has eight moves and its isometry group two.

    `\operatorname{conv}\{(0,0),(1,0),(2,1),(1,1)\}` is the unit square carried
    by the shear `(x,y) \mapsto (x+y,y)`.  A parallelogram has eight affine
    automorphisms, which is what the polytope's own lattice group answers, and
    its isometries are the identity and the half-turn: the shear conjugated
    moves of the square are not isometries of the plane.  The metric lane counts
    the two, since the six the ambient space refuses are not arrows of it.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    polygon = LatticePolygons(ZZ.free_module(2))(((0, 0), (1, 0), (2, 1), (1, 1)))
    placed = category.on(
        ("vertices", polygon.vertices()), _placement(polygon, space, vector_space)
    )
    corners = tuple(placed.vertices())
    geometric = placed.geometric_automorphisms()

    assert polygon.geometric_automorphisms().order() == 8
    assert geometric.order() == 2

    elements = tuple(geometric)
    (half_turn,) = tuple(
        element for element in elements if element(corners[0]) != corners[0]
    )
    assert all(element(corner) in corners for element in elements for corner in corners)
    assert half_turn(corners[0]) in corners
    assert (half_turn * half_turn)(corners[0]) == corners[0]


def test_a_face_of_a_placed_euclidean_polytope_answers_its_own_group() -> None:
    r"""Faces of the placed square: an edge has two moves, a vertex one.

    A face that does not span the ambient plane determines no ambient affine map
    of its own, so the plane's isometry decision is not asked about it, and its
    group is the polytope's own affine group read on the face's vertices: the
    identity and one swap for an edge, the identity alone for a vertex.  The
    reflection lifts to the edge it fixes -- the bottom one -- and to no other,
    the left edge going to the right one.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    polygon = _square()
    placed = category.on(
        ("vertices", polygon.vertices()), _placement(polygon, space, vector_space)
    )
    lower_left = vector_space((-1, -1))
    lower_right = vector_space((1, -1))
    upper_left = vector_space((-1, 1))
    upper_right = vector_space((1, 1))
    edges = tuple(placed.faces(1))
    vertices = tuple(placed.faces(0))
    reflection = next(
        element
        for element in tuple(placed.geometric_automorphisms())
        if element(lower_left) == lower_right and element(upper_left) == upper_right
    )
    bottom = _edge_spanning(polygon, ((-1, -1), (1, -1)))
    left = _edge_spanning(polygon, ((-1, -1), (-1, 1)))
    placed_bottom = next(face for face in edges if face.underlying_polytope() is bottom)
    placed_left = next(face for face in edges if face.underlying_polytope() is left)

    lift = placed.geometric_lifts_of_face_automorphism(reflection, placed_bottom)

    assert all(edge.Aut().order() == 2 for edge in edges)
    assert all(vertex.Aut().order() == 1 for vertex in vertices)
    assert lift.ambient_map()(lower_left) == lower_right
    assert lift.ambient_map()(lower_right) == lower_left
    assert placed.geometric_lifts_of_face_automorphism(reflection, placed_left) is None


def test_the_spherical_owner_decides_an_isometry_both_ways() -> None:
    r"""The round circle's decision is the circle's, and not the plane's.

    A half-turn about the centre is an isometry of the circle.  A half-turn about
    the point `(1,0)` is a Euclidean isometry which carries the circle to another
    one, so the plane admits it and the circle refuses it: that is the check no
    affine or Euclidean decision stands in for.  The shear is neither.
    """
    vector_space, space = _plane()
    (first, second) = vector_space.module_generators()
    centre = space.an_element()
    circle = _circle(space, centre, RR.one())
    about_centre = SphericalSpaces().Mor(circle, circle)(
        _euclidean_arrow(space, vector_space, (-first, -second))
    )
    about_one = SphericalSpaces().Mor(circle, circle)(
        _euclidean_arrow(
            space, vector_space, (-first, -second), offset=vector_space((2, 0))
        )
    )
    shear = SphericalSpaces().Mor(circle, circle)(
        _euclidean_arrow(space, vector_space, (first + second, second))
    )

    assert circle.radius() == RR.one()
    assert circle.center() == centre
    assert circle.point_set()(vector_space((1, 0))) in circle.point_set()
    assert circle.is_an_isometry(about_centre) is True
    assert space.is_an_isometry(about_one.ambient_isometry()) is True
    assert circle.is_an_isometry(about_one) is False
    assert circle.is_an_isometry(shear) is False

    with pytest.raises(AssertionError):
        SphericalSpaces().in_space(space, centre, RR.zero(), circle.inclusion())


def test_the_placed_circle_diamond_answers_its_eight_isometries() -> None:
    r"""The diamond on the unit circle: the dihedral group of order eight.

    `\operatorname{conv}\{(1,0),(0,1),(-1,0),(0,-1)\}` placed on the unit circle
    has the four reflections and the four rotations of the square as its
    isometries, and each of the eight is an arrow of the placed spherical
    polytope, admitted by the circle's decision.  The reflection in the `x`-axis
    is one of them and is of order two; the shear is no isometry of the circle
    and is refused there, though it is an affine automorphism of the plane.
    """
    vector_space, space = _plane()
    (first, second) = vector_space.module_generators()
    centre = space.an_element()
    circle = _circle(space, centre, RR.one())
    category = SphericalGeodesicPolytopesIn(circle)
    diamond = LatticePolygons(ZZ.free_module(2))(
        ((1, 0), (0, 1), (-1, 0), (0, -1))
    )
    placed = category.on(
        ("vertices", diamond.vertices()),
        Sets().Mor(diamond, circle.point_set())(
            lambda point: circle.point_set()(
                vector_space(
                    tuple(
                        RR(point.to_vector()(label))
                        for label in vector_space.module_generating_set()
                    )
                )
            )
        ),
    )
    east = vector_space((1, 0))
    north = vector_space((0, 1))
    south = vector_space((0, -1))
    geometric = placed.geometric_automorphisms()
    elements = tuple(geometric)
    reflection = next(
        element
        for element in elements
        if element(east) == east and element(north) == south and element(south) == north
    )

    assert geometric.order() == 8
    assert all(circle.is_an_isometry(element.ambient_map()) is True for element in elements)
    assert (reflection * reflection)(east) == east
    assert reflection(north) == south
    assert reflection(east) == east

    with pytest.raises(ValueError):
        category.Mor(placed, placed)(
            SphericalSpaces().Mor(circle, circle)(
                _euclidean_arrow(space, vector_space, (first + second, second))
            ),
            placed.face_poset().Aut().one(),
        )


def test_the_zero_sphere_states_an_inhabitant_and_decides_its_isometries() -> None:
    r"""`S^0`: the pair `\{-1,1\}` of the line, its swap admitted, a shift refused.

    The sphere family states one of its spaces without being handed one: the pair
    of points at distance one from the line's origin.  Its points are that pair,
    its isometries the two permutations of it, and the swap is one of them, of
    order two.  The translation `x \\mapsto x + 2` is an isometry of the line that
    moves the centre, so the line admits it and the sphere refuses it: that is the
    difference between this decision and the affine or Euclidean one.
    """
    sphere = SphericalSpaces().an_object()
    line = sphere.euclidean_space()
    model = line.model_vector_space()
    affine_space = line.underlying_affine_space()
    one = sphere.point_set()(model((1,)))
    minus_one = sphere.point_set()(model((-1,)))
    swap = SphericalSpaces().Mor(sphere, sphere)(
        _line_arrow(line, model, affine_space, -1, 0)
    )
    shift = SphericalSpaces().Mor(sphere, sphere)(
        _line_arrow(line, model, affine_space, 1, 2)
    )

    assert sphere in SphericalSpaces()
    assert sphere.radius() == RR.one()
    assert one in sphere.point_set()
    assert minus_one in sphere.point_set()
    assert (model((2,)) in sphere.point_set()) is False
    assert sphere.is_an_isometry(swap) is True
    assert line.is_an_isometry(shift.ambient_isometry()) is True
    assert sphere.is_an_isometry(shift) is False
    assert swap(minus_one) == one
    assert (swap * swap)(one) == one


def test_the_placed_euclidean_category_states_an_inhabitant() -> None:
    r"""The one-point polytope at the plane's origin: one vertex, one automorphism.

    A placed category states one of its objects without being handed one: the
    point at the Euclidean plane's own selected point.  Its only vertex is that
    point, its placement lands in the plane, and its geometric automorphism group
    is the identity alone.  That one element is not read back as an ambient map:
    a point does not affinely span the plane, so it determines none, and the frame
    refuses rather than choosing a map on a complement the point does not meet.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    pointed = category.an_object()
    origin = space.an_element()
    geometric = pointed.geometric_automorphisms()

    assert pointed.ambient_space() is space
    assert tuple(pointed.vertices()) == (origin,)
    assert geometric.order() == 1

    with pytest.raises(AssertionError):
        tuple(geometric)[0]


def _face_correspondence(first, second, polytope, shifted, permutation):
    r"""The faces' map a permutation of two congruent placed polygons induces.

    A face is determined by the vertices it contains, so the face carrying each
    vertex at position ``i`` to the vertex at ``permutation[i]`` is the face whose
    vertex set is that image: this is the correspondence the same ambient map
    induces on the faces, read off the two face objects.
    """
    first_lattice = tuple(polytope.vertices())
    second_lattice = tuple(shifted.vertices())

    def image_of(face):
        signature = tuple(bool(face.contains_point(vertex)) for vertex in first_lattice)
        return next(
            candidate
            for candidate in second.face_poset()
            if tuple(
                bool(candidate.contains_point(second_lattice[position]))
                for position in permutation
            )
            == signature
        )

    return FiniteGradedPosets().Mor(first.face_poset(), second.face_poset())(image_of)


def test_an_isometry_between_two_placed_euclidean_polytopes_is_an_arrow() -> None:
    r"""The translation carrying the square onto its shift: an arrow, not an automorphism.

    Two placed squares, `\operatorname{conv}\{(\pm1,\pm1)\}` and its translate by
    `(2,2)`, are two objects of one placed Euclidean category.  The translation
    is an isometry of the plane, and the faces' map it induces is the
    correspondence its vertex permutation gives, so the pair is an arrow between
    them and the metric owner admits it.  The dilation by two is no isometry of
    the plane, and the very same faces' map with it is refused: the difference is
    the metric decision, and not the shape of the faces' map.
    """
    vector_space, space = _plane()
    category = EuclideanPolytopesIn(space)
    (first_direction, second_direction) = vector_space.module_generators()
    square = _square()
    shifted = LatticePolygons(ZZ.free_module(2))(((1, 1), (1, 3), (3, 3), (3, 1)))
    first = category.on(
        ("vertices", square.vertices()), _placement(square, space, vector_space)
    )
    second = category.on(
        ("vertices", shifted.vertices()), _placement(shifted, space, vector_space)
    )
    translation = _euclidean_arrow(
        space, vector_space, (first_direction, second_direction), offset=vector_space((2, 2))
    )
    dilation = _euclidean_arrow(
        space,
        vector_space,
        (first_direction + first_direction, second_direction + second_direction),
    )
    position_of = second.vertices().ranking_map()
    permutation = tuple(int(position_of(translation(point))) for point in first.vertices())
    faces = _face_correspondence(first, second, square, shifted, permutation)
    arrow = category.Mor(first, second)(translation, faces)

    assert first.ambient_space() is second.ambient_space()
    assert space.is_an_isometry(translation) is True
    assert tuple(first.vertices())[0] != tuple(second.vertices())[0]
    assert arrow(tuple(first.vertices())[0]) == tuple(second.vertices())[0]
    assert faces(square) == shifted

    assert space.is_an_isometry(dilation) is False
    with pytest.raises(ValueError):
        category.Mor(first, second)(dilation, faces)


def test_the_hyperbolic_owner_decides_an_isometry() -> None:
    r"""`HH^1`: the lattice's isometries are the hyperboloid's, a map of points is not one.

    An arrow of a hyperbolic space is induced by an isometry of its lattice, and
    the space decides that from the arrow's own datum: the identity of the lattice
    and the sign change of the timelike generator both preserve the pairing, so
    both are admitted.  A map of the point set carries no lattice isometry at all,
    so the decision refuses it rather than answering.
    """
    space = HyperbolicSpaces(1).an_object()
    lattice = space.lattice()
    labels = tuple(lattice.module_generating_set())
    family = space.category().Mor(space, space)
    identity = family.identity()
    images = {
        labels[0]: -lattice.module_generator(labels[0]),
        labels[1]: lattice.module_generator(labels[1]),
    }
    reflection = family(lattice.Mor(lattice)(lambda label: images[label]))

    assert space.is_an_isometry(identity) is True
    assert space.is_an_isometry(reflection) is True
    assert reflection.lattice_isometry()(
        lattice.module_generator(labels[0])
    ) == -lattice.module_generator(labels[0])

    with pytest.raises(ValueError):
        space.is_an_isometry(Sets().Mor(space, space)(lambda point: point))


def test_the_placed_hyperbolic_polygon_admits_its_isometry() -> None:
    r"""A square of the disc placed on `HH^2`: the antipodal isometry is an arrow.

    The points of a hyperboloid model are the rays of its positive rational
    vectors, so a rational point `x` of the disc is placed at the ray of
    `(-1, x_1, x_2)` scaled to integers, and `\operatorname{conv}\{(\pm
    \frac12,\pm\frac12)\}` lands on four points of `HH^2`.  The sign change of
    the timelike generator is an isometry of the lattice, so it is an arrow of the
    hyperbolic space, and it carries those four points among themselves -- it is
    the antipodal map of the disc -- so it is an arrow of the placed polygon,
    admitted by the space's own decision.  A placed vertex is a point of the
    space's own point set -- the rays of the component's positive rational
    vectors -- so the space takes it as it is, and the arrow carries a ray to the
    ray of its representative's image without a chart: the antipodal map sends the
    first placed corner to the third and is its own inverse.
    """
    space = HyperbolicSpaces(2).an_object()
    lattice = space.lattice()
    half = QQ(1) / QQ(2)
    square = ConvexPolytopes(ZZ.free_module(2))(
        ((-half, -half), (-half, half), (half, half), (half, -half))
    )
    polytope_labels = tuple(ZZ.free_module(2).module_generating_set())

    def placement(point):
        coordinates = tuple(QQ(point.to_vector()(label)) for label in polytope_labels)
        denominator = max(coordinate.denominator() for coordinate in coordinates)
        return space.rational_point(
            lattice((-denominator, *(denominator * value for value in coordinates)))
        )

    category = HyperbolicGeodesicPolytopesIn(space)
    placed = category.on(
        ("vertices", square.vertices()), Sets().Mor(square, space.point_set())(placement)
    )
    labels = tuple(lattice.module_generating_set())
    family = space.category().Mor(space, space)
    images = {
        label: (
            -lattice.module_generator(label)
            if label == labels[0]
            else lattice.module_generator(label)
        )
        for label in labels
    }
    sign_flip = family(lattice.Mor(lattice)(lambda label: images[label]))
    vertex_faces = tuple(placed.face_poset().faces(0))
    face_of = [
        next(face for face in vertex_faces if face.contains_point(corner))
        for corner in square.vertices()
    ]
    antipode = (3, 2, 1, 0)
    face_map = next(
        candidate
        for candidate in tuple(placed.abstract_automorphisms())
        if all(candidate(face_of[index]) == face_of[antipode[index]] for index in range(4))
    )
    arrow = category.Mor(placed, placed)(sign_flip, face_map)

    assert placed.dimension() == 2
    assert placed.face_poset().faces(0).cardinality() == 4
    corners = tuple(placed.vertices())

    assert space.is_an_isometry(sign_flip) is True
    assert arrow.ambient_map() is sign_flip
    assert space(corners[0]) is corners[0]
    assert arrow(corners[0]) == corners[3]
    assert (arrow * arrow)(corners[0]) == corners[0]
