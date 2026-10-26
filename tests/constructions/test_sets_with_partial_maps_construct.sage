r"""Represented sets lie in the supercategory allowing partial set maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_set_lies_in_sets_with_partial_maps() -> None:
    partial_sets = ObjectSetsOfDiscreteCategories().super_categories()[0]
    three = Set((1, 2, 3))

    assert three in partial_sets
    assert three in ObjectSetsOfDiscreteCategories()
