from sage_extensions.all import *


def positive():
    return ZZ.condition_set(lambda n: n > 0)


def test_the_categories_of_the_positive_integers() -> None:
    assert positive() in Sets()
    assert positive() in CountablyInfiniteSets()


def test_membership_and_cardinality() -> None:
    subset = positive()
    assert subset.cardinality() == aleph0
    assert 1 in subset
    assert 0 not in subset
    assert -1 not in subset
    assert subset.inclusion().codomain() is ZZ


def test_the_positive_integers_have_one_endomorphism_category() -> None:
    subset = positive()
    endomorphisms = subset.Mor(subset)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert subset.Mor(subset) is endomorphisms
    assert identity * identity == identity
