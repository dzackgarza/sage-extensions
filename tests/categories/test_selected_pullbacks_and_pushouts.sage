r"""Selected finite cospan limits and span colimits with universal maps.

The diagrams, both structural legs and their universal factorizations are
source-only specimens for execution at terminal T.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_set_pullback_retains_both_maps_to_the_cospan() -> None:
    source = Sets.Δ[1]
    target = Sets.Δ[1]
    identity = Sets().Mor(source, target)(lambda x: target(x))
    constant = Sets().Mor(source, target)(lambda _x: target(0))
    construction = Sets().pullback_construction(identity, constant)
    shape = construction.diagram().domain()
    left, right, tip = (shape(0), shape(1), shape(2))
    left_map = construction.structure_morphism(left)
    right_map = construction.structure_morphism(right)
    tip_map = construction.structure_morphism(tip)

    assert construction.object().cardinality() == cardinal(2)
    assert identity * left_map == constant * right_map == tip_map
    point = Sets.Δ[0]
    zero = Sets().Mor(point, source)(lambda _p: source(0))
    one = Sets().Mor(point, source)(lambda _p: source(1))
    cone = construction.diagram().Cones().cone(
        point, lambda index: zero if index is left else one if index is right else identity * zero
    )
    factor = construction.factor(cone).apex_map()
    assert left_map(factor(point(0))) == source(0)
    assert right_map(factor(point(0))) == source(1)


def test_set_pushout_retains_both_maps_from_the_span() -> None:
    common, two = Sets.Δ[0], Sets.Δ[1]
    first = Sets().Mor(common, two)(lambda _p: two(0))
    second = Sets().Mor(common, two)(lambda _p: two(1))
    construction = Sets().pushout_construction(first, second)
    shape = construction.diagram().domain()
    left, right, tip = shape(0), shape(1), shape(2)
    injection_left = construction.costructure_morphism(left)
    injection_right = construction.costructure_morphism(right)
    source_map = construction.costructure_morphism(tip)

    assert construction.object().cardinality() == cardinal(3)
    assert injection_left * first == injection_right * second == source_map
    image = Sets.Δ[1]
    left_leg = Sets().Mor(two, image)(lambda point: image(point))
    right_leg = Sets().Mor(two, image)(lambda _point: image(0))
    # Both legs agree on the common point.
    cocone = construction.diagram().Cocones().cocone(
        image,
        lambda index: left_leg if index is left else right_leg if index is right else left_leg * first,
    )
    factor = construction.factor(cocone).apex_map()
    assert factor * injection_left == left_leg
    assert factor * injection_right == right_leg


def test_group_pullback_contains_diagonal_c4_and_has_compatible_projections() -> None:
    four, two = Groups.C(4), Groups.C(2)
    g, h = next(iter(four.group_generators())), next(iter(two.group_generators()))
    reduction = four.Mor(two)({g: h})
    construction = Groups().pullback_construction(reduction, reduction)
    shape = construction.diagram().domain()
    left, right, tip = shape(0), shape(1), shape(2)
    left_projection = construction.structure_morphism(left)
    right_projection = construction.structure_morphism(right)
    assert construction.object() in Groups()
    assert reduction * left_projection == reduction * right_projection
    diagonal = construction.diagram().Cones().cone(
        four,
        lambda index: four.Mor(four).identity() if index is left or index is right else reduction,
    )
    factor = construction.factor(diagonal).apex_map()
    assert left_projection(factor(g)) == g
    assert right_projection(factor(g)) == g
