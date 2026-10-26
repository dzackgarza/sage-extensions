from sage_extensions.all import *


def monomials():
    r"""$\{z^n : n \in \mathbb Z\}$."""
    return LaurentMonomials()


def test_the_monomials_are_indexed_by_the_integers() -> None:
    assert monomials().index_set() is ZZ


def test_the_categories_of_the_laurent_monomials() -> None:
    assert monomials() in Sets()
    assert monomials() in CountablyInfiniteSets()


def test_the_laurent_monomials_multiply_by_adding_exponents() -> None:
    r"""$z^{-1} z = 1 = z^0$ and $z^2 = z \cdot z$."""
    family = monomials()
    assert family.cardinality() == aleph0
    assert family.function(0) == 1
    assert family.function(-1) * family.function(1) == family.function(0)
    assert family.function(2) == family.function(1) ^ 2
