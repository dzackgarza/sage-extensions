r"""Chosen finite presentations retain their free group, relators, and comparison to the source group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_s3_presentation_remembers_its_source_group() -> None:
    source = Groups.S(3)
    presented = source.presentation()
    comparison = presented.presentation_isomorphism()

    assert presented in GroupsWithChosenFinitePresentation()
    assert presented.presentation_source_group() is source
    assert comparison.domain() is presented
    assert comparison.codomain() is source
    assert presented.presenting_free_group() in GroupsWithChosenFinitePresentation()
    assert presented.defining_relations().cardinality() >= cardinal(1)


def test_free_group_quotient_by_relators_gives_symmetric_three() -> None:
    free = Groups.Free(2)
    a, b = free.group_generators()
    quotient = free.quotient_by_relators((a**2, b**3, (a * b) ** 2))

    assert free in GroupsWithChosenFinitePresentation()
    assert quotient in GroupsWithChosenFinitePresentation()
    assert quotient.presenting_free_group() is free
    assert quotient.defining_relations().cardinality() == cardinal(3)
    assert quotient.is_isomorphic_to(Groups.S(3))

