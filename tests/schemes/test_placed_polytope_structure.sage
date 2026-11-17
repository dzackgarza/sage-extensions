r"""The structure of a placed polytope: faces, boundary, triangulation, face lifts.

A face of a placed polytope is a placed polytope: the geometric automorphisms of
the parent act on the faces with the parent's ambient map, so a face carries the
parent's placement restricted to it and is an object of the same placed category.
``face_inclusion`` is then an arrow of that category whose ambient map is the
identity of the ambient space the parent is placed in, and it is the identity on
the face's points because the face is already where the parent places it.

The specimens are the placed square `\operatorname{conv}\{(\pm 1, \pm 1)\}`, the
placed irregular quadrangle `\operatorname{conv}\{(0,0),(1,0),(0,1),(2,3)\}` and
the placed stored Sterk2 hull; the six operations are read on each of them.
"""

from sage_extensions.all import *


def _placed_category():
    r"""Placed lattice polygons in `\mathbf{R}^2` over the lattice `\mathbf{Z}^2`."""
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


def _quadrangle():
    return LatticePolygons(ZZ.free_module(2))(((0, 0), (1, 0), (0, 1), (2, 3)))


def _foundation(polygon):
    r"""The placed ``polygon`` and the number of its vertices and of its edges."""
    category = _placed_category()
    placed = _placed(category, polygon)
    return placed, int(polygon.n_vertices()), int(polygon.n_vertices())


def _check_the_faces(placed, vertices, edges):
    r"""Faces of each dimension, and the inclusions of those of dimension at most one.

    The faces of a placed polygon are its placed vertices, its placed edges and
    itself; the empty face is placed too and has no vertex.  An inclusion carries
    the ambient space's identity, so it fixes the face's own points, and the top
    face's inclusion is the polytope's identity arrow.
    """
    category = placed.category()

    assert placed.faces(0).cardinality() == vertices
    assert placed.faces(1).cardinality() == edges
    assert placed.faces(2).cardinality() == 1
    assert placed.faces(-1).cardinality() == 1
    assert tuple(placed.faces(2))[0] is placed
    assert all(face in category for face in tuple(placed.faces(0)))
    assert all(face in category for face in tuple(placed.faces(1)))
    for face in tuple(placed.faces(0)) + tuple(placed.faces(1)):
        inclusion = placed.face_inclusion(face)
        assert inclusion.domain() is face
        assert inclusion.codomain() is placed
        assert all(inclusion(point) == point for point in face.vertices())
        assert all(
            inclusion.face_poset_map()(inner) == inner
            for inner in tuple(face.face_poset())
        )
        assert inclusion * face.Aut().one() == inclusion
    top_inclusion = placed.face_inclusion(placed)
    assert top_inclusion.domain() is placed
    assert all(
        top_inclusion.face_poset_map()(face) == face for face in placed.face_poset()
    )
    assert all(top_inclusion(point) == point for point in placed.vertices())


def _check_the_boundary(placed, edges):
    r"""The boundary is exactly the codimension-one faces, and its inclusions compose.

    The boundary's faces are the facets, and each of them includes into the
    polytope by an arrow of this category that fixes its own points.
    """
    boundary = tuple(placed.boundary())
    inclusions = tuple(placed.boundary_inclusion().values())

    assert placed.boundary().cardinality() == edges
    assert frozenset(boundary) == frozenset(placed.faces(1))
    assert placed.boundary_inclusion().index_set().cardinality() == edges
    assert all(inclusion.codomain() is placed for inclusion in inclusions)
    for face, inclusion in zip(boundary, inclusions, strict=True):
        assert inclusion.domain() is face
        assert all(inclusion(point) == point for point in face.vertices())


def _check_the_triangulation(placed, polygon):
    r"""A triangulation's cells are placed simplices on the placed vertices, covering it.

    Each cell is an object of the placed category whose vertices are vertices of
    the polytope, each lies in the polytope, and the cells' normalized volumes add
    up to the polytope's: a finite union of closed cells of the polytope's own
    volume is the polytope.
    """
    cells = tuple(placed.triangulate())
    placed_vertices = frozenset(placed.vertices())
    total = polygon.normalized_volume()

    assert cells
    assert all(cell in placed.category() for cell in cells)
    for cell in cells:
        assert frozenset(cell.vertices()) <= placed_vertices
        assert int(cell.underlying_polytope().dimension()) == 2
        assert cell.underlying_polytope().is_contained_in(polygon) is True
    assert sum(int(cell.underlying_polytope().normalized_volume()) for cell in cells) == int(
        total
    )


def _check_the_geometric_lifts(placed):
    r"""A parent automorphism lifts to a face exactly when it preserves that face.

    The lift is an element of the face's own geometric automorphism group whose
    ambient map is the parent's, and whose faces' map agrees with the parent's on
    the face's faces.  A face the parent's automorphism moves has no lift: its
    ambient map does not carry the face onto itself, and the operation says so
    rather than returning an automorphism of something else.
    """
    automorphisms = tuple(placed.geometric_automorphisms())
    faces = tuple(placed.faces(0)) + tuple(placed.faces(1))

    assert automorphisms
    preserved = 0
    moved = 0
    for element in automorphisms:
        for face in faces:
            lift = placed.geometric_lifts_of_face_automorphism(element, face)
            image = element.face_poset_map()(face.underlying_polytope())
            keeps = image == face.underlying_polytope()
            assert (lift is None) != keeps
            if keeps:
                preserved += 1
                assert lift in face.geometric_automorphisms()
                assert all(
                    lift.face_poset_map()(inner) == element.face_poset_map()(inner)
                    for inner in tuple(face.face_poset())
                )
                assert all(lift(point) == element(point) for point in face.vertices())
            else:
                moved += 1
    assert preserved > 0


def test_the_placed_square_carries_its_faces_boundary_cells_and_lifts() -> None:
    r"""The square: four vertices, four edges, two cells, and the reflection's lifts.

    Its vertical reflection keeps the bottom and the top edge and exchanges the
    left and the right one, so the lift is defined on the first two, where the
    ambient map's lattice part is the diagonal matrix of `-1` and `1`, and not on
    the last two.
    """
    polygon = _square()
    placed, vertices, edges = _foundation(polygon)

    _check_the_faces(placed, vertices, edges)
    _check_the_boundary(placed, edges)
    _check_the_triangulation(placed, polygon)
    _check_the_geometric_lifts(placed)

    lattice = placed.category().ambient_space().affine_lattice()
    labels = tuple(lattice.module_generating_set())
    first = lattice.module_generator(labels[0])
    second = lattice.module_generator(labels[1])
    vertical = next(
        element
        for element in tuple(placed.geometric_automorphisms())
        if element.ambient_map().lattice_map()(first) == -first
        and element.ambient_map().lattice_map()(second) == second
        and element != placed.geometric_automorphisms().one()
    )
    kept_edges = placed.faces(1).filtered(
        lambda face: placed.geometric_lifts_of_face_automorphism(vertical, face)
        is not None
    )
    moved_edges = placed.faces(1).filtered(
        lambda face: placed.geometric_lifts_of_face_automorphism(vertical, face) is None
    )

    assert kept_edges.cardinality() == 2
    assert moved_edges.cardinality() == 2
    assert kept_edges.cardinality() + moved_edges.cardinality() == placed.faces(
        1
    ).cardinality()
    for face in kept_edges:
        lift = placed.geometric_lifts_of_face_automorphism(vertical, face)
        assert lift.ambient_map().lattice_map()(first) == -first
        assert lift.ambient_map().lattice_map()(second) == second
    moved_cores = tuple(face.underlying_polytope() for face in moved_edges)
    assert all(
        vertical.face_poset_map()(core) in frozenset(moved_cores)
        for core in moved_cores
    )
    assert vertical.face_poset_map()(moved_cores[0]) == moved_cores[1]
    assert all(
        vertical.face_poset_map()(face.underlying_polytope())
        == face.underlying_polytope()
        for face in kept_edges
    )


def test_the_placed_quadrangle_carries_its_faces_boundary_cells_and_lifts() -> None:
    r"""The irregular quadrangle: the same structure, with only the identity lifting.

    Its placed faces are four vertices and four edges and its boundary is those
    edges; its geometric group is trivial, so every face is preserved by the only
    geometric automorphism there is and each lift is that face's own identity.
    """
    polygon = _quadrangle()
    placed, vertices, edges = _foundation(polygon)

    _check_the_faces(placed, vertices, edges)
    _check_the_boundary(placed, edges)
    _check_the_triangulation(placed, polygon)
    _check_the_geometric_lifts(placed)

    assert tuple(placed.geometric_automorphisms()) == (
        placed.geometric_automorphisms().one(),
    )
    for face in tuple(placed.faces(1)):
        lift = placed.geometric_lifts_of_face_automorphism(
            placed.geometric_automorphisms().one(), face
        )
        assert lift == face.geometric_automorphisms().one()


def test_the_placed_sterk2_hull_carries_its_faces_boundary_cells_and_lifts() -> None:
    r"""The stored Sterk2 hull: seventeen edges, fifteen cells, two automorphisms.

    Its boundary is its seventeen edges and its triangulation's cells have its own
    placed vertices; its two geometric automorphisms are the identity and the
    reflection, and the reflection's lifts are defined exactly on the faces it
    keeps.
    """
    polygon = Sterk.sterk2_polygon(ZZ.free_module(2))
    placed, vertices, edges = _foundation(polygon)

    assert vertices == 17
    assert placed.geometric_automorphisms().order() == 2
    _check_the_faces(placed, vertices, edges)
    _check_the_boundary(placed, edges)
    _check_the_triangulation(placed, polygon)
    _check_the_geometric_lifts(placed)
