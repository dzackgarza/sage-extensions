r"""Limits and colimits of a discrete diagram of finite sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_discrete_diagram_rejects_invalid_finite_object_images() -> None:
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
    from sage_extensions.categories.sets.indexed_families import indexed_family

    labels = Sets.Δ[1]
    index = DiscreteCategory(labels)
    diagrams = Cat().Mor(index, Sets())
    valid = diagrams.discrete_diagram(lambda _point: labels)
    assert valid(index.object(labels(0))) is labels
    try:
        diagrams.discrete_diagram(lambda _point: object())
    except ValueError:
        pass
    else:
        raise AssertionError("an object outside Set was admitted to a set-valued diagram")

    different_labels = Sets.Δ[2]
    try:
        diagrams.discrete_diagram(indexed_family(different_labels, lambda _point: labels))
    except ValueError:
        pass
    else:
        raise AssertionError("a discrete diagram admitted an unrelated indexing set")


def test_empty_discrete_diagram_has_terminal_limit_and_initial_colimit() -> None:
    index = DiscreteCategory(Sets.Δ[-1])
    diagram = Cat().Mor(index, Sets()).discrete_diagram(lambda _index: Sets.Δ[0])
    assert Sets().Limits(index).object(diagram).cardinality() == 1
    assert Sets().Colimits(index).object(diagram).cardinality() == 0


def test_limit_and_colimit_of_a_discrete_diagram_are_product_and_disjoint_union() -> None:
    r"""For the discrete diagram ``{0 ↦ [1], 1 ↦ [2]}`` (sets of 2 and 3 elements),
    the limit is the product, of cardinality ``2 · 3 = 6``, and the colimit is
    the disjoint union, of cardinality ``2 + 3 = 5``; cones from a point are
    pairs of elements, so there are 6 of them."""
    index = DiscreteCategory(Sets.Δ[1])
    two, three = Sets.Δ[1], Sets.Δ[2]
    diagram = Cat().Mor(index, Sets()).discrete_diagram(lambda position: two if position == 0 else three)

    selected_limit = Sets().Limits(index).construction(diagram)
    assert selected_limit.object().cardinality() == 6
    selected_colimit = Sets().Colimits(index).construction(diagram)
    assert selected_colimit.object().cardinality() == 5
    point = Sets.Δ[0]
    assert Sets().Mor(point, selected_limit.object()).cardinality() == 6
    for left in two:
        for right in three:
            cone = diagram.Cones().cone(
                point,
                lambda object_, left=left, right=right: Sets().Mor(point, diagram(object_))(
                    lambda _: left if object_ is index.object(Sets.Δ[1](0)) else right
                ),
            )
            factor = selected_limit.factor(cone)
            assert selected_limit.structure_morphism(index.object(Sets.Δ[1](0))) * factor.apex_map() == cone.structure_morphism(index.object(Sets.Δ[1](0)))
            assert selected_limit.structure_morphism(index.object(Sets.Δ[1](1))) * factor.apex_map() == cone.structure_morphism(index.object(Sets.Δ[1](1)))
    for first in two:
        for second in three:
            target = Sets.Δ[1]
            cocone = diagram.Cocones().cocone(
                target,
                lambda object_, first=first, second=second: Sets().Mor(diagram(object_), target)(
                    lambda value: target(0) if object_ is index.object(Sets.Δ[1](0)) and value == first else target(1)
                ),
            )
            factor = selected_colimit.factor(cocone)
            for position in Sets.Δ[1]:
                selected = index.object(position)
                assert factor.apex_map() * selected_colimit.costructure_morphism(selected) == cocone.costructure_morphism(selected)
