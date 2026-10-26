from sage_extensions.all import *


def translates():
    r"""$\{\operatorname{sinc}(\cdot - n) : n \in \mathbb Z\}$."""
    return SincTranslates()


def test_the_translates_are_indexed_by_the_integers() -> None:
    assert translates().index_set() is ZZ


def test_the_categories_of_the_sinc_translates() -> None:
    assert translates() in Sets()
    assert translates() in CountablyInfiniteSets()


def test_the_translates_are_countably_many_and_distinct() -> None:
    family = translates()
    assert family.cardinality() == aleph0
    assert family.function(0) in family
    assert family.function(0) != family.function(1)
