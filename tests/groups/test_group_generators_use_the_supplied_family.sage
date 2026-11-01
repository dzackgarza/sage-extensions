r"""A finite group states the generators it was given; it does not enumerate itself.

``group_generators`` reads the group's retained resolution, and a group whose
construction supplied a generating family — a generated subgroup its generators,
a finite-form engine group the generators its engine was built from — resolves
through exactly those.  The alternative is the canonical free cover ``F(U(G))`` on
the whole underlying set, which costs the group's order: correct as a universal
construction, and unusable as a way to ask for generators of a group with
``46998591897600`` elements.

These tests make whole-group enumeration *fail* rather than merely slow, so a
change that routes generator enumeration back through the underlying set fails
here instead of hanging the consumer that calls it.
"""

from unittest import mock

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def _split_four_space_form():
    return (Lattices(ZZ)([[0, 2], [2, 0]]) ** 2).discriminant_group()


def _anti_invariant_form():
    from sage_extensions.catalogue import Involutions

    coinvariant = (
        Involutions.I_En.primitive_extension().orthogonal_complement_inclusion().domain()
    )
    return coinvariant.discriminant_group()


def _poison_whole_group_iteration(group):
    r"""Make enumerating ``group``'s underlying set raise, and return the patcher."""

    def refuse(self):
        raise AssertionError(
            f"{group} was enumerated to obtain its generators; the retained "
            "generating family must be used instead"
        )

    return mock.patch.object(type(group), "__iter__", refuse)


def test_the_small_orthogonal_group_states_generators_that_generate_it() -> None:
    r"""Order 72, from two supplied generators, and each one is an isometry."""
    form = _split_four_space_form()
    group = form.orthogonal_group()
    generators = tuple(group.group_generators())

    assert group.cardinality() == 72
    assert len(generators) == len(group._engine_group().gens())
    assert group.subgroup_on(generators).cardinality() == group.cardinality()
    for generator in generators:
        for left in form.module_generators():
            for right in form.module_generators():
                assert generator(left).b(generator(right)) == left.b(right)


def test_a_generated_subgroup_states_the_generators_it_was_given() -> None:
    form = _split_four_space_form()
    group = form.orthogonal_group()
    supplied = tuple(group.group_generators())[:1]
    subgroup = group.subgroup_on(supplied)

    assert tuple(subgroup.selected_subgroup_generators()) == supplied
    with _poison_whole_group_iteration(subgroup):
        assert tuple(subgroup.group_generators()) == supplied


def test_the_large_orthogonal_group_states_generators_without_enumerating() -> None:
    r"""``|O(A_N)| = 46998591897600``, and its four supplied generators are read directly.

    Enumerating this group is not slow, it is impossible; the assertion is that the
    generator datum, the generating set and the generating morphism are all
    available with the underlying set made uniterable.
    """
    group = _anti_invariant_form().orthogonal_group()
    supplied = tuple(group.group_generators())

    assert group.cardinality() == 46998591897600
    assert len(supplied) == len(group._engine_group().gens())
    assert group.subgroup_on(supplied).cardinality() == group.cardinality()

    with _poison_whole_group_iteration(group):
        assert tuple(group.group_generators()) == supplied
        assert tuple(group.group_generating_set()) == tuple(
            group.group_generating_set()
        )
        morphism = group.group_generator_morphism()
        assert morphism.codomain() is group
        assert tuple(morphism(generator) for generator in morphism.domain()) == supplied
