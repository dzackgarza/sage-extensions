r"""A finite action retains its permutation morphism under restriction.

Restriction is precomposition of group morphisms. The two double cosets
of a transposition subgroup in S3 have point-orbits of sizes one and two.
"""

import pytest

from sage_extensions.all import *


def test_a_permutation_morphism_retains_its_actual_named_point_set() -> None:
    group = Groups.S(3)
    points = Sets()(("z", "a", "m"))
    ranking = points.ranking_map()

    def action(element, point):
        image = element(ZZ(int(ranking(point)) + 1))
        return ranking.inverse()(int(image) - 1)

    original = FiniteGSets(group)(points, action)
    representation = original.permutation_representation()
    retained = FiniteGSets(group).from_permutation_representation(representation)

    assert retained.point_set() is points
    assert retained.permutation_representation() is representation
    assert all(retained.act(g, point) == original.act(g, point) for g in group for point in points)


def test_restriction_along_c4_to_c2_keeps_the_kernel_and_the_action() -> None:
    four, two = Groups.C(4), Groups.C(2)
    s, t = next(iter(four.group_generators())), next(iter(two.group_generators()))
    projection = four.Mor(two)({s: t})
    points = Sets()(("left", "right"))
    original = FiniteGSets(two)(
        points,
        lambda g, point: point if g == two.one() else "right" if point == "left" else "left",
    )
    restricted = original.restrict_action(projection)

    assert restricted.point_set() is points
    assert restricted.acting_group() is four
    assert restricted.permutation_representation().kernel().cardinality() == cardinal(2)
    assert restricted.orbits().cardinality() == cardinal(1)
    assert all(restricted.act(g, point) == original.act(projection(g), point) for g in four for point in points)


def test_the_transposition_double_cosets_partition_s3_modulo_c2() -> None:
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    cosets = group.left_cosets(subgroup)
    classes = cosets.double_cosets(subgroup)

    assert classes.cardinality() == cardinal(2)
    assert {int(orbit.points().cardinality()) for orbit in classes} == {1, 2}
    assert set().union(*(set(orbit.points()) for orbit in classes)) == set(cosets)


def test_a_permutation_morphism_requires_its_actual_acting_group() -> None:
    group = Groups.S(3)
    other = Groups.C(2)

    with pytest.raises(ValueError):
        FiniteGSets(other).from_permutation_representation(group.Mor(group).identity())


def test_a_finite_action_requires_a_group_morphism() -> None:
    group = Groups.S(3)
    constant_transposition = Sets().Mor(group, group)(lambda _g: group((1, 2)))

    with pytest.raises(TypeError):
        FiniteGSets(group).from_permutation_representation(constant_transposition)
