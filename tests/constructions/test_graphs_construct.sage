r"""Finite undirected graphs as symmetric directed graphs.

The two-vertex edge has adjacency in both directions although its defining edge
is listed once.  Its morphisms are ordinary graph homomorphisms, inherited from
the directed-graph owner because symmetry is a property of the same adjacency
data rather than additional chosen structure.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _edge_graph():
    return Graphs().from_edges((0, 1), ((0, 1),))


def _loop_point():
    return Graphs().from_edges(("*",), (("*", "*"),))


def _two_isolated_vertices():
    return Graphs().from_edges(("a", "b"), ())


def test_graph_retains_vertices_edges_and_symmetric_adjacency() -> None:
    graph = _edge_graph()

    assert graph in Graphs()
    assert graph in Digraphs()
    assert graph in Sets()
    assert graph.cardinality() == cardinal(2)
    assert graph.vertices().cardinality() == cardinal(2)
    assert graph.edges().cardinality() == cardinal(1)
    assert graph.edge_space().cardinality() == cardinal(4)
    assert graph.has_edge(graph(0), graph(1))
    assert graph.has_edge(graph(1), graph(0))
    assert not graph.is_directed()
    assert graph.is_symmetric()
    assert isinstance(graph(0), graph.ElementType)
    with pytest.raises(ValueError):
        graph.vertex_label(graph(0))
    with pytest.raises(ValueError):
        graph.edge_label(graph(0), graph(1))


def test_graph_inherits_set_constructions_on_its_vertex_set() -> None:
    graph = _edge_graph()
    two = Sets.Δ[1]
    point = Sets.Δ[0]

    assert graph.counting_well_order().cardinality() == cardinal(2)
    assert graph.condition_set(lambda vertex: vertex == graph(0)).cardinality() == cardinal(1)
    assert graph.power_set().cardinality() == cardinal(4)
    assert graph.exponential(point).cardinality() == cardinal(2)
    assert graph.product_with(two).cardinality() == cardinal(4)
    assert graph.coproduct_with(two).cardinality() == cardinal(4)
    assert graph.subsets_of_size(1).cardinality() == cardinal(2)
    assert graph.finite_subsets().cardinality() == cardinal(4)
    assert graph.finite_words().cardinality() == aleph0
    assert graph.finite_multisets().cardinality() == aleph0


def test_graph_image_set_uses_an_explicit_underlying_set_map() -> None:
    source = _edge_graph()
    target = _loop_point()
    underlying = source.Mor(target, category=Sets())(lambda _vertex: target("*"))
    image = source.image_set(underlying)

    assert underlying in Sets().Mor(source, target)
    assert image.cardinality() == cardinal(1)
    assert target("*") in image


def test_graph_endpoint_mor_preserves_adjacency_unless_sets_are_requested() -> None:
    source = _edge_graph()
    target = _loop_point()
    isolated = _two_isolated_vertices()
    graph_mor = source.Mor(target)
    coarse = source.Mor(isolated, category=Sets())
    collapse = graph_mor(lambda _vertex: target("*"))
    separates_edge = lambda vertex: isolated("a") if vertex == source(0) else isolated("b")

    assert graph_mor is Graphs().Mor(source, target)
    assert graph_mor is Digraphs().Mor(source, target)
    assert collapse(source(1)) == target("*")
    assert coarse(separates_edge)(source(0)) == isolated("a")
    with pytest.raises(ValueError):
        source.Mor(isolated)(separates_edge)


def test_graph_morphisms_retain_underlying_maps_identity_and_composition() -> None:
    source = _edge_graph()
    target = _loop_point()
    collapse = source.Mor(target)(lambda _vertex: target("*"))
    source_identity = source.Mor(source).identity()
    target_identity = target.Mor(target).identity()

    assert collapse.underlying_set_morphism().domain() is source
    assert collapse.underlying_set_morphism().codomain() is target
    assert source_identity(source(1)) == source(1)
    assert target_identity * collapse == collapse
    assert collapse * source_identity == collapse
