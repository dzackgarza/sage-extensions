r"""Subobjects of a fixed object form the monic part of its slice category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_subset_subobject_category_retains_slice_and_monomorphism_owners() -> None:
    three = Sets.Δ[2]
    subobjects = Sets().Subobjects(three)
    singleton = three.power_set()((three(0),))
    pair = three.power_set()((three(0), three(1)))
    morphisms = subobjects.Mor(singleton, pair)

    assert subobjects.slice_category() is Sets().SliceOver(three)
    assert subobjects.monomorphism_category() is Sets().MonomorphismArrowCategory()
    assert morphisms.subobject_category() is subobjects
    assert subobjects.leq(singleton, pair)
    assert not subobjects.leq(pair, singleton)
