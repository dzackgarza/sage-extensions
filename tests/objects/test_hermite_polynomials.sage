from sage_extensions.all import *


def hermite():
    r"""$\{H_n : n \in \mathbb N\}$."""
    return HermitePolynomials()


def test_the_polynomials_are_indexed_by_the_naturals() -> None:
    assert hermite().index_set() is NN


def test_the_categories_of_the_hermite_polynomials() -> None:
    assert hermite() in Sets()
    assert hermite() in CountablyInfiniteSets()


def test_the_hermite_polynomials() -> None:
    r"""$H_0 = 1$ in both the physicists' and the probabilists' normalization."""
    family = hermite()
    assert family.cardinality() == aleph0
    assert family.function(0) == 1
    assert family.function(2) in family
    assert family.function(1) != family.function(2)
