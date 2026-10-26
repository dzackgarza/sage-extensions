from sage_extensions.all import *


def characters():
    r"""$\{e^{inx} : n \in \mathbb Z\}$."""
    return FourierCharacters()


def test_the_characters_are_indexed_by_the_integers() -> None:
    assert characters().index_set() is ZZ


def test_the_categories_of_the_characters() -> None:
    assert characters() in Sets()
    assert characters() in CountablyInfiniteSets()


def test_the_characters_are_countably_many_and_distinct() -> None:
    family = characters()
    assert family.cardinality() == aleph0
    assert family.function(0) in family
    assert family.function(1) != family.function(-1)
    assert family.function(0) != family.function(1)
