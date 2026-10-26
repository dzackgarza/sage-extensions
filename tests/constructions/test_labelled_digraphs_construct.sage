r"""Finite directed graphs with selected vertex and edge labels.

The source has one labelled arrow ``0 -> 1``.  The target has arrows in both
directions, so swapping its two vertices still preserves adjacency but changes
both endpoint labels and the selected edge label.  It therefore separates an
ordinary digraph morphism from a labelled-digraph morphism.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _labelled_arrow():
    return LabelledDigraphs().from_labels(
        (0, 1),
        ((0, 1),),
        {0: "source", 1: "target"},
        {(0, 1): "arrow"},
    )


def _labelled_two_cycle():
    return LabelledDigraphs().from_labels(
        ("a", "b"),
        (("a", "b"), ("b", "a")),
        {"a": "source", "b": "target"},
        {("a", "b"): "arrow", ("b", "a"): "back"},
    )


def test_labelled_digraph_retains_vertices_edges_direction_and_labels() -> None:
    graph = _labelled_arrow()

    assert graph in LabelledDigraphs()
    assert graph in Digraphs()
    assert graph.cardinality() == cardinal(2)
    assert graph.vertices().cardinality() == cardinal(2)
    assert graph.edges().cardinality() == cardinal(1)
    assert graph.edge_space().cardinality() == cardinal(4)
    assert graph.has_edge(graph(0), graph(1))
    assert not graph.has_edge(graph(1), graph(0))
    assert graph.is_directed()
    assert not graph.is_symmetric()
    assert graph.vertex_label(graph(0)) == "source"
    assert graph.vertex_label(graph(1)) == "target"
    assert graph.edge_label(graph(0), graph(1)) == "arrow"


def test_labelled_digraph_inherits_set_constructions_on_its_vertex_set() -> None:
    graph = _labelled_arrow()
    two = Sets.Δ[1]
    point = Sets.Δ[0]

    assert graph.counting_well_order().cardinality() == cardinal(2)
    assert graph.condition_set(lambda vertex: vertex == graph(0)).cardinality() == cardinal(1)
    assert graph.power_set().cardinality() == cardinal(4)
    assert graph.exponential(point).cardinality() == cardinal(2)
    assert graph.product_with(two).cardinality() == cardinal(4)
    assert graph.coproduct_with(two).cardinality() == cardinal(4)
    assert graph.subsets_of_size(2).cardinality() == cardinal(1)
    assert graph.finite_subsets().cardinality() == cardinal(4)
    assert graph.finite_words().cardinality() == aleph0
    assert graph.finite_multisets().cardinality() == aleph0


def test_labelled_digraph_image_set_uses_an_explicit_underlying_set_map() -> None:
    source = _labelled_arrow()
    target = _labelled_two_cycle()
    underlying = source.Mor(target, category=Sets())(
        lambda vertex: target("a") if vertex == source(0) else target("b")
    )
    image = source.image_set(underlying)

    assert underlying in Sets().Mor(source, target)
    assert image.cardinality() == cardinal(2)
    assert target("a") in image
    assert target("b") in image


def test_labelled_digraph_endpoint_mor_preserves_labels_by_default() -> None:
    source = _labelled_arrow()
    target = _labelled_two_cycle()
    labelled_mor = source.Mor(target)
    digraph_mor = source.Mor(target, category=Digraphs())
    set_mor = source.Mor(target, category=Sets())
    preserving = labelled_mor(
        lambda vertex: target("a") if vertex == source(0) else target("b")
    )
    label_swapping = lambda vertex: target("b") if vertex == source(0) else target("a")

    assert labelled_mor is LabelledDigraphs().Mor(source, target)
    assert digraph_mor is Digraphs().Mor(source, target)
    assert set_mor is Sets().Mor(source, target)
    assert preserving(source(0)) == target("a")
    assert digraph_mor(label_swapping)(source(0)) == target("b")
    with pytest.raises(ValueError):
        labelled_mor(label_swapping)


def test_labelled_digraph_morphisms_retain_underlying_maps_identity_and_composition() -> None:
    source = _labelled_arrow()
    target = _labelled_two_cycle()
    morphism = source.Mor(target)(
        lambda vertex: target("a") if vertex == source(0) else target("b")
    )
    source_identity = source.Mor(source).identity()
    target_identity = target.Mor(target).identity()

    assert morphism.underlying_set_morphism().domain() is source
    assert morphism.underlying_set_morphism().codomain() is target
    assert source_identity(source(1)) == source(1)
    assert target_identity * morphism == morphism
    assert morphism * source_identity == morphism
