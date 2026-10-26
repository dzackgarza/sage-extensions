r"""Represented sets lie in the object-set category of discrete categories."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_set_is_an_object_set_of_a_discrete_category() -> None:
    three = Set((1, 2, 3))

    assert three in ObjectSetsOfDiscreteCategories()
    assert three.cardinality() == cardinal(3)
