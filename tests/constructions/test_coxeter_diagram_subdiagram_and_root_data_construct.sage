r"""Rooted A2 exposes its subdiagram poset, Cartan data, and root realization maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_subdiagram_api_recovers_the_four_vertex_subsets() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])
    vertex = next(iter(diagram.vertices()))

    assert diagram.subdiagram((vertex,)) == diagram.induced_subdiagram((vertex,))
    assert diagram.subdiagram_poset().cardinality() == cardinal(4)


def test_connected_a2_has_one_component_scaled_cartan_type() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])

    assert diagram.component_scaled_cartan_types().cardinality() == cardinal(1)
    assert diagram.scaled_cartan_type() in diagram.component_scaled_cartan_types()


def test_rooted_a2_root_realization_and_morphism_have_canonical_endpoints() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2], rooted=True)
    realization = diagram.root_realization()
    abstract = diagram.root_lattice()
    root_map = diagram.root_morphism()
    vertex = next(iter(diagram.vertices()))

    assert root_map.domain() is abstract
    assert root_map.codomain() is realization
    assert root_map(abstract.module_generator(0)) in realization
    assert diagram.root(vertex) in realization
