r"""Finite groups expose conjugation characters, and subgroup categories are parameterized by groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_two_conjugation_and_trivial_character_have_expected_values() -> None:
    group = Groups.C(2)
    conjugation = group.conjugation_g_set()
    characters = group.character_set()
    trivial = group.trivial_character()
    representatives = group.conjugacy_classes_representatives()

    assert conjugation.orbits().cardinality() == cardinal(2)
    assert trivial in characters
    assert all(trivial(representative) == trivial.codomain().one() for representative in representatives)


def test_subgroup_categories_are_parameterized_by_groups_and_retain_generators() -> None:
    group = Groups.C(4)
    subgroup = group.subgroup((group.group_generators()[0] ** 2,))

    assert Subgroups(group).parameter_category() is Groups()
    assert GeneratedSubgroups(group).parameter_category() is Groups()
    assert subgroup.selected_subgroup_generators().cardinality() == cardinal(1)
