r"""A homomorphism out of a free group is determined freely by generator images."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_free_group_has_four_maps_to_c2() -> None:
    free = Groups.Free(2)
    target = Groups.C(2)
    morphisms = free.Mor(target)
    generator = target.group_generator()
    selected = morphisms({0: generator, 1: target.one()})
    first, second = free.group_generators()

    assert morphisms.cardinality() == cardinal(4)
    assert selected(first) == generator
    assert selected(second) == target.one()


def test_free_group_morphism_exposes_generator_map_and_postcomposition() -> None:
    free = Groups.Free(2)
    target = Groups.C(2)
    generator = target.group_generator()
    selected = free.Mor(target)({0: generator, 1: target.one()})
    generator_map = selected.generator_morphism()
    identity = target.Mor(target).identity()

    assert generator_map(0) == generator
    assert generator_map(1) == target.one()
    assert selected.postcompose(identity) == selected
