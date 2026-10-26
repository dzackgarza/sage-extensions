r"""Archive reconciliation for univariate polynomial-ring algorithms."""

from sage_extensions.all import *


def test_archive_euclidean_algorithms_return_owned_polynomial_elements() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    cubic = x**3 - 6 * x**2 + 11 * x - 6
    quadratic = x**2 - 3 * x + 2

    quotient_remainder = cubic.quo_rem(quadratic)
    quotient, remainder = quotient_remainder
    assert quotient_remainder.parent().factor(0) is polynomials
    assert quotient_remainder.parent().factor(1) is polynomials
    assert quotient_remainder.parent().projection(0)(quotient_remainder) == quotient
    assert quotient_remainder.parent().projection(1)(quotient_remainder) == remainder
    assert quotient.parent() is polynomials
    assert remainder.parent() is polynomials
    assert quotient * quadratic + remainder == cubic
    assert remainder == polynomials.zero()
    assert cubic.gcd(quadratic) == quadratic

    bezout = cubic.xgcd(quadratic)
    common, left, right = bezout
    assert all(bezout.parent().factor(index) is polynomials for index in bezout.parent().index_set())
    assert common.parent() is polynomials
    assert left.parent() is polynomials
    assert right.parent() is polynomials
    assert left * cubic + right * quadratic == common


def test_archive_factorization_retains_owned_factors_multiplicities_and_unit() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    cubic = (x - 1) * (x - 2) * (x - 3)
    factorization = cubic.factor()

    assert factorization.parent_ring() is polynomials
    assert factorization.unit().parent() is polynomials
    assert factorization.cardinality() == 3
    assert all(
        factor.parent() is polynomials and multiplicity == 1
        for factor, multiplicity in factorization.items()
    )
    assert factorization.reconstruct() == cubic
    assert not ((x - 1) * (x - 2)).is_irreducible()
    assert (x**2 + 1).is_irreducible()


def test_archive_discriminant_resultant_roots_and_splitting_field_cross_back_owned() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    quadratic = x**2 - 3 * x + 2
    cubic = (x - 1) * (x - 2) * (x - 3)

    assert quadratic.discriminant() == 1
    assert cubic.resultant(quadratic) == 0
    assert quadratic.roots().cardinality() == 2
    assert (x**2 + 1).roots().cardinality() == 0
    assert (x**2 + 1).roots(QQbar).cardinality() == 2
    assert (x**3 - 2).splitting_field().degree() == 6
