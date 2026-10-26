from sage_extensions.all import *


def test_square_voronoi_cell_retains_facets_incidence_and_stabilizers() -> None:
    lattice = Lattices(ZZ)(ZZ ** 2)
    cell = lattice.voronoi_cell()

    assert cell.ambient_lattice() is lattice
    assert cell.n_vertices() == 4
    assert cell.facets().cardinality() == 4
    facets = lattice.voronoi_facets()
    assert sum(facet.vertices().cardinality() for facet in facets) == 8
    # Every isometry acts on the actual rational vertices.  This retains
    # the full-O(L) stabilizer requirement without a Voronoi-only wrapper.
    labels = tuple(lattice.module_generating_set())
    vertices = {tuple(vertex) for vertex in cell.vertices()}
    for isometry in lattice.O():
        images = [isometry(lattice.module_generator(label)).to_vector() for label in labels]
        for vertex in vertices:
            image = tuple(
                sum(coordinate * column(label) for coordinate, column in zip(vertex, images))
                for label in labels
            )
            assert image in vertices

    for normal in facets.index_set():
        facet = facets[normal]
        assert normal.parent() is lattice
        assert normal != lattice.zero()
        assert facet.vertices().cardinality() == 2
        stabilizer = lattice.O().stabilizer(normal)
        assert stabilizer.supergroup() is lattice.O()
        assert stabilizer.stabilized_object() is normal
        # The action is BG -> Modules(R), not a descriptive string.
        action = stabilizer.stabilizer_action()
        assert action.domain() is lattice.O().classifying_category()
        assert action.codomain() is Modules(lattice.base_ring())
        point = action.domain().an_object()
        identity = action.domain().Mor(point, point)(lattice.O().one())
        assert action(identity)(normal) == normal


def test_a2_voronoi_facets_are_indexed_by_the_six_relevant_vectors() -> None:
    lattice = Lattices(ZZ)("A2")
    cell = lattice.voronoi_cell()
    facet_normals = Set(lattice.voronoi_facets().index_set())
    relevant = Set(lattice.voronoi_relevant_vectors())

    assert cell.n_vertices() == 6
    assert cell.facets().cardinality() == 6
    assert facet_normals == relevant
