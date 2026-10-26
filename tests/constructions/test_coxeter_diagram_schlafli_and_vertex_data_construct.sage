r"""Rooted A2 exposes its Schlaefli tensor, root graph, and vertex metadata."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_schlafli_tensor_has_positive_determinant() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])

    assert diagram.schlaflian() > 0
    assert diagram.schlafli_tensor().is_nondegenerate()


def test_rooted_a2_root_intersection_graph_has_two_vertices() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2], rooted=True)

    assert diagram.root_intersection_graph().cardinality() == cardinal(2)


def test_a2_vertex_accessors_recover_the_selected_vertices() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])
    vertices = tuple(diagram.vertices())

    assert diagram.vertex(0) == vertices[0]
    assert diagram.vertex(1) == vertices[1]
    assert diagram.vertex_names().cardinality() == cardinal(2)
    assert diagram.vertex_weight(vertices[0]) == diagram.vertex_label(vertices[0])
