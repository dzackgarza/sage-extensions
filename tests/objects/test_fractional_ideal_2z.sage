from sage_extensions.all import *


def two_z():
    return ZZ.fractional_ideal(2)


def test_the_category_construction_agrees() -> None:
    assert FractionalIdeals(ZZ)(2) == two_z()


def test_the_categories_of_2z() -> None:
    assert two_z() in FractionalIdeals(ZZ)
    assert two_z() in Modules(ZZ)


def test_2z_is_principal_and_free_of_rank_one() -> None:
    assert two_z().is_principal()
    assert two_z().module_rank() == 1
    assert two_z().is_projective()


def test_the_inverse_of_2z() -> None:
    r"""$(2)^{-1} = \tfrac12\mathbb Z$, $(2) + (\tfrac12) = (\tfrac12)$, $(2)\cap(\tfrac12) = (2)$."""
    ideal = two_z()
    inverse = ideal.inverse()
    assert inverse == ZZ.fractional_ideal(1/2)
    assert inverse.inverse() == ideal
    assert ideal.sum(inverse) == inverse
    assert ideal.intersection(inverse) == ideal


def test_2z_has_one_endomorphism_category() -> None:
    ideal = two_z()
    endomorphisms = ideal.Mor(ideal)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert ideal.Mor(ideal) is endomorphisms
    assert identity * identity == identity
