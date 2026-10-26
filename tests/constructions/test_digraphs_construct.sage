r"""Finite directed graphs and their adjacency-preserving morphisms.

The specimen is the directed path ``0 -> 1 -> 2``.  Direction matters: neither
reverse arrow occurs.  A constant graph morphism lands in a one-vertex graph
with a loop, so the image of every source edge is still an edge.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _directed_path():
    return Digraphs().from_edges((0, 1, 2), ((0, 1), (1, 2)))


def _loop_point():
    return Digraphs().from_edges(("*",), (("*", "*"),))


def test_digraph_retains_vertices_edges_and_direction() -> None:
    graph = _directed_path()

    assert graph in Digraphs()
    assert graph in Sets()
    assert graph.cardinality() == cardinal(3)
    assert graph.vertices().cardinality() == cardinal(3)
    assert graph.edges().cardinality() == cardinal(2)
    assert graph.edge_space().cardinality() == cardinal(9)
    assert graph.has_edge(graph(0), graph(1))
    assert graph.has_edge(graph(1), graph(2))
    assert not graph.has_edge(graph(1), graph(0))
    assert graph.is_directed()
    assert not graph.is_symmetric()
    with pytest.raises(ValueError):
        graph.vertex_label(graph(0))
    with pytest.raises(ValueError):
        graph.edge_label(graph(0), graph(1))


def test_digraph_inherits_set_constructions_on_its_vertex_set() -> None:
    graph = _directed_path()
    two = Sets.Δ[1]
    point = Sets.Δ[0]

    assert graph.counting_well_order().cardinality() == cardinal(3)
    assert graph.condition_set(lambda vertex: vertex != graph(2)).cardinality() == cardinal(2)
    assert graph.power_set().cardinality() == cardinal(8)
    assert graph.exponential(point).cardinality() == cardinal(3)
    assert graph.product_with(two).cardinality() == cardinal(6)
    assert graph.coproduct_with(two).cardinality() == cardinal(5)
    assert graph.subsets_of_size(2).cardinality() == cardinal(3)
    assert graph.finite_subsets().cardinality() == cardinal(8)
    assert graph.finite_words().cardinality() == aleph0
    assert graph.finite_multisets().cardinality() == aleph0


def test_digraph_image_set_uses_an_explicit_underlying_set_map() -> None:
    source = _directed_path()
    target = _loop_point()
    underlying = source.Mor(target, category=Sets())(lambda _vertex: target("*"))
    image = source.image_set(underlying)

    assert underlying in Sets().Mor(source, target)
    assert image.cardinality() == cardinal(1)
    assert target("*") in image


def test_digraph_endpoint_mor_preserves_adjacency_unless_sets_are_requested() -> None:
    source = _directed_path()
    target = _loop_point()
    structured_mor = source.Mor(target)
    coarse_mor = source.Mor(target, category=Sets())
    collapse = structured_mor(lambda _vertex: target("*"))

    assert structured_mor is Digraphs().Mor(source, target)
    assert coarse_mor is Sets().Mor(source, target)
    assert collapse.underlying_set_morphism().domain() is source
    assert collapse.underlying_set_morphism().codomain() is target
    assert collapse(source(2)) == target("*")


def test_digraph_morphisms_have_identity_and_composition() -> None:
    source = _directed_path()
    target = _loop_point()
    collapse = source.Mor(target)(lambda _vertex: target("*"))
    source_identity = source.Mor(source).identity()
    target_identity = target.Mor(target).identity()

    assert source_identity(source(1)) == source(1)
    assert target_identity * collapse == collapse
    assert collapse * source_identity == collapse
