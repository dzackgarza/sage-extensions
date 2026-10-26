r"""Finite generation and finite presentation of groups have resolution classifiers."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finitely_generated_group_refinement_has_degree_zero_classifier() -> None:
    groups = Groups()
    category = groups.FinitelyGeneratedAsMagma()
    resolutions = category.resolution_category()
    classifier = category.resolution_classifier()

    assert category is groups.FinitelyGenerated()
    assert classifier.domain() is resolutions
    assert classifier.codomain() is groups


def test_finitely_presented_group_refinement_has_degree_one_classifier() -> None:
    groups = Groups()
    category = groups.FinitelyPresentedAsGroup()
    resolutions = category.resolution_category()
    classifier = category.resolution_classifier()

    assert category is groups.FinitelyPresented()
    assert classifier.domain() is resolutions
    assert classifier.codomain() is groups
