r"""The natural S3-set is a represented S3-object in Sets."""

from sage_extensions.all import *  # noqa: F401,F403


def _natural_s3_set():
    group = Groups.S(3)
    action = FiniteGSets(group)((1, 2, 3), lambda g, point: g(point))
    return group, action


def test_natural_s3_set_exposes_its_action_and_action_functor() -> None:
    group, acted = _natural_s3_set()
    generator = group.group_generators()[0]
    action = acted.action()
    functor = acted.action_functor()

    assert acted in GObjects(group, Sets())
    assert acted.acting_group() is group
    assert acted.underlying_category() == Sets()
    assert acted.act(generator, 1) == generator(1)
    assert acted.action_of(generator)(1) == generator(1)
    assert action(generator)(1) == generator(1)
    assert functor.domain() == group.classifying_category()
    assert functor.codomain() == Sets()
    assert not acted.action_is_free()
    assert not acted.is_invariant(1)


def test_fixed_subobject_and_restricted_action_have_the_expected_points() -> None:
    group, acted = _natural_s3_set()
    transposition = next(g for g in group.group_generators() if g.order() == 2)
    subgroup = group.subgroup((transposition,))
    fixed = acted.fixed_subobject_of(transposition)
    restricted = acted.restrict_action(subgroup.inclusion())

    assert fixed.cardinality() == cardinal(1)
    assert restricted.acting_group() is subgroup
    assert restricted.point_set() == acted.point_set()
    assert restricted.action_of(transposition)(1) == acted.action_of(transposition)(1)

