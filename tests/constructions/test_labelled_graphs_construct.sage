r"""Finite undirected graphs with selected vertex and edge labels.

The selected edge is symmetric, so its label is read in either direction.
Swapping the two vertices preserves the underlying undirected graph but not the
chosen vertex labels; it is therefore accepted only after explicitly forgetting
the labels to the graph category.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _labelled_edge():
    return LabelledGraphs().from_labels(
        (0, 1),
        ((0, 1),),
        {0: "left", 1: "right"},
        {(0, 1): "bond"},
    )


def _renamed_labelled_edge():
    return LabelledGraphs().from_labels(
        ("a", "b"),
        (("a", "b"),),
        {"a": "left", "b": "right"},
        {("a", "b"): "bond"},
    )


def test_labelled_graph_retains_symmetric_adjacency_and_labels() -> None:
    graph = _labelled_edge()

    assert graph in LabelledGraphs()
    assert graph in LabelledDigraphs()
    assert graph in Graphs()
    assert graph.cardinality() == cardinal(2)
    assert graph.vertices().cardinality() == cardinal(2)
    assert graph.edges().cardinality() == cardinal(1)
    assert graph.edge_space().cardinality() == cardinal(4)
    assert graph.has_edge(graph(0), graph(1))
    assert graph.has_edge(graph(1), graph(0))
    assert not graph.is_directed()
    assert graph.is_symmetric()
    assert graph.vertex_label(graph(0)) == "left"
    assert graph.vertex_label(graph(1)) == "right"
    assert graph.edge_label(graph(0), graph(1)) == "bond"
    assert graph.edge_label(graph(1), graph(0)) == "bond"
    assert isinstance(graph(0), graph.ElementType)


def test_labelled_graph_inherits_set_constructions_on_its_vertex_set() -> None:
    graph = _labelled_edge()
    two = Sets.Δ[1]
    point = Sets.Δ[0]

    assert graph.counting_well_order().cardinality() == cardinal(2)
    assert graph.condition_set(lambda vertex: vertex == graph(1)).cardinality() == cardinal(1)
    assert graph.power_set().cardinality() == cardinal(4)
    assert graph.exponential(point).cardinality() == cardinal(2)
    assert graph.product_with(two).cardinality() == cardinal(4)
    assert graph.coproduct_with(two).cardinality() == cardinal(4)
    assert graph.subsets_of_size(1).cardinality() == cardinal(2)
    assert graph.finite_subsets().cardinality() == cardinal(4)
    assert graph.finite_words().cardinality() == aleph0
    assert graph.finite_multisets().cardinality() == aleph0


def test_labelled_graph_image_set_uses_an_explicit_underlying_set_map() -> None:
    source = _labelled_edge()
    target = _renamed_labelled_edge()
    underlying = source.Mor(target, category=Sets())(
        lambda vertex: target("a") if vertex == source(0) else target("b")
    )
    image = source.image_set(underlying)

    assert underlying in Sets().Mor(source, target)
    assert image.cardinality() == cardinal(2)
    assert target("a") in image
    assert target("b") in image


def test_labelled_graph_endpoint_mor_preserves_labels_by_default() -> None:
    source = _labelled_edge()
    target = _renamed_labelled_edge()
    labelled_mor = source.Mor(target)
    graph_mor = source.Mor(target, category=Graphs())
    set_mor = source.Mor(target, category=Sets())
    preserving = labelled_mor(
        lambda vertex: target("a") if vertex == source(0) else target("b")
    )
    label_swap = lambda vertex: target("b") if vertex == source(0) else target("a")

    assert labelled_mor is LabelledGraphs().Mor(source, target)
    assert labelled_mor is LabelledDigraphs().Mor(source, target)
    assert graph_mor is Graphs().Mor(source, target)
    assert set_mor is Sets().Mor(source, target)
    assert preserving(source(1)) == target("b")
    assert graph_mor(label_swap)(source(0)) == target("b")
    with pytest.raises(ValueError):
        labelled_mor(label_swap)


def test_labelled_graph_morphisms_retain_underlying_maps_identity_and_composition() -> None:
    source = _labelled_edge()
    target = _renamed_labelled_edge()
    morphism = source.Mor(target)(
        lambda vertex: target("a") if vertex == source(0) else target("b")
    )
    source_identity = source.Mor(source).identity()
    target_identity = target.Mor(target).identity()

    assert morphism.underlying_set_morphism().domain() is source
    assert morphism.underlying_set_morphism().codomain() is target
    assert source_identity(source(0)) == source(0)
    assert target_identity * morphism == morphism
    assert morphism * source_identity == morphism
