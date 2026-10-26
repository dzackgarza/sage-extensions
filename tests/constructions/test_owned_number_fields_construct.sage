r"""The Gaussian rationals expose the standard arithmetic of an owned number field."""

from sage_extensions.all import *  # noqa: F401,F403


def _gaussian_field():
    return QuadraticField(-1, "i")


def test_gaussian_field_has_degree_discriminant_signature_and_class_number() -> None:
    field = _gaussian_field()

    assert field in OwnedNumberFields()
    assert field.degree() == 2
    assert field.discriminant() == -4
    assert field.signature() == signature_pair(0, 1)
    assert field.class_number() == 1
    assert field.is_galois()
    assert field.embeddings(CC).cardinality() == cardinal(2)
    assert field.Mor(field).cardinality() == cardinal(2)
    assert field.galois_group().order() == 2
    assert field.normal_closure().degree() == 2
    assert field.normal_closure_galois_group().order() == 2
    assert field.ramified_primes().cardinality() == cardinal(1)
    assert ZZ(2) in field.ramified_primes()
    assert field.primes_above(5).cardinality() == cardinal(2)
    assert field.ring_of_integers().is_maximal()
    assert field.maximal_order() == field.ring_of_integers()
    assert field.as_algebra() in Algebras(QQ).Associative().Unital().Commutative()
    assert field.underlying_algebra() in Algebras(QQ).Associative().Unital().Commutative()


def test_gaussian_integer_order_generated_by_i_is_maximal() -> None:
    field = _gaussian_field()
    order = field.order_generated_by(field.primitive_element())

    assert order in OwnedOrders()
    assert order.is_maximal()
    assert order.fraction_field() is field


def test_gaussian_primitive_element_has_expected_linear_algebra_invariants() -> None:
    field = _gaussian_field()
    i = field.primitive_element()
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    multiplication = i.multiplication_morphism()
    matrix = i.multiplication_matrix()

    assert i.minimal_polynomial() == x**2 + 1
    assert i.characteristic_polynomial() == x**2 + 1
    assert i.conjugates(CC).cardinality() == cardinal(2)
    assert i.inverse() == -i
    assert i.is_integral()
    assert i.norm() == QQ.one()
    assert i.trace() == QQ.zero()
    assert matrix.determinant() == QQ.one()
    assert matrix.trace() == QQ.zero()
    assert multiplication(field.one()) == i


def test_gaussian_field_extends_by_a_quadratic_polynomial() -> None:
    field = _gaussian_field()
    polynomials = field.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    extension = field.extension(x**2 - field(2), "a")

    assert extension.degree() == 4

