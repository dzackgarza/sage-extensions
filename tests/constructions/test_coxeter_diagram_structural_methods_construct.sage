r"""Finite type A3 exposes its connected Coxeter graph and presented group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a3_diagram_has_three_vertices_and_one_connected_component() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 3])

    assert diagram.num_vertices() == 3
    assert diagram.connected_components().cardinality() == cardinal(1)


def test_a3_coxeter_graph_has_the_same_vertices_as_the_diagram() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 3])
    graph = diagram.graph()

    assert graph in Graphs()
    assert graph.cardinality() == diagram.cardinality()


def test_a3_finitely_presented_coxeter_group_is_the_selected_coxeter_group() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 3])

    assert diagram.finitely_presented_coxeter_group() is diagram.coxeter_group()
