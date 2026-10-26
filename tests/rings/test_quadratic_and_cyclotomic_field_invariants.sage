r"""Invariants of small quadratic fields and of the fifth cyclotomic field.

Values from the LMFDB (checked 2026-09-24): ``Q(sqrt(-5))`` is 2.0.20.1 with class
number 2; ``Q(sqrt(-23))`` is 2.0.23.1 with class number 3; ``Q(sqrt(-47))`` is
2.0.47.1 with class number 5; ``Q(sqrt(5))`` is 2.2.5.1 with class number 1, ramified
only at 5; ``Q(sqrt(10))`` is 2.2.40.1 with class number 2; ``Q(zeta_5)`` is 4.0.125.1,
signature (0, 2), discriminant 125, ramified only at 5, Galois with group ``C_4``.

The element relations hold by definition: ``sqrt(5)`` has minimal polynomial
``x^2 - 5``, norm ``-5`` and trace ``0``; ``(1 + sqrt(5))/2`` is a root of
``x^2 - x - 1`` and so integral, while ``sqrt(5)/2`` is a root of ``x^2 - 5/4`` and
is not; ``Z[sqrt(5)]`` has index 2 in the maximal order and is not maximal.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_class_numbers_of_small_quadratic_fields() -> None:
    assert QuadraticField(-1).class_number() == 1
    assert QuadraticField(-5).class_number() == 2
    assert QuadraticField(-23).class_number() == 3
    assert QuadraticField(-47).class_number() == 5
    assert QuadraticField(5).class_number() == 1
    assert QuadraticField(10).class_number() == 2


def test_discriminants_signatures_and_ramification_of_quadratic_fields() -> None:
    imaginary = QuadraticField(-5)
    real = QuadraticField(5)

    assert imaginary.degree() == 2
    assert imaginary.discriminant() == -20
    assert real.discriminant() == 5
    assert QuadraticField(10).discriminant() == 40
    assert ZZ(2) in imaginary.ramified_primes()
    assert ZZ(5) in imaginary.ramified_primes()
    assert ZZ(3) not in imaginary.ramified_primes()
    assert ZZ(5) in real.ramified_primes()
    assert ZZ(2) not in real.ramified_primes()


def test_the_fifth_cyclotomic_field() -> None:
    field = CyclotomicField(5)

    assert field.degree() == 4
    assert field.discriminant() == 125
    assert ZZ(5) in field.ramified_primes()
    assert ZZ(2) not in field.ramified_primes()
    assert field.class_number() == 1
    assert field.is_galois()
    assert field.galois_group().order() == 4


def test_a_quadratic_field_is_galois_of_order_two() -> None:
    field = QuadraticField(-5)

    assert field.is_galois()
    assert field.galois_group().order() == 2


def test_norm_trace_and_minimal_polynomial_of_root_five() -> None:
    field = QuadraticField(5)
    root = field.primitive_element()
    x = QQ["x"].algebra_generator("x")

    assert root * root == 5
    assert root.norm() == -5
    assert root.trace() == 0
    assert root.minimal_polynomial() == x**2 - 5
    assert root.characteristic_polynomial() == x**2 - 5
    assert field.defining_polynomial() == x**2 - 5
    assert root.inverse() * root == 1
    assert root.inverse() == root / 5


def test_the_golden_ratio_is_integral_and_half_root_five_is_not() -> None:
    field = QuadraticField(5)
    root = field.primitive_element()

    assert root.is_integral()
    assert ((1 + root) / 2).is_integral()
    assert not (root / 2).is_integral()


def test_the_order_generated_by_root_five_is_not_maximal() -> None:
    field = QuadraticField(5)
    root = field.primitive_element()
    maximal = field.ring_of_integers()
    order = field.order_generated_by(root)

    assert maximal.is_maximal()
    assert not order.is_maximal()


def test_a_relative_quadratic_extension_of_q_root_two() -> None:
    field = QuadraticField(2)
    y = field["y"].algebra_generator("y")
    extension = field.extension(y**2 - 3, "b")

    root = extension.primitive_element()

    assert root * root == 3
    assert root.minimal_polynomial().degree() == 2


def test_the_real_quadratic_field_has_two_real_embeddings() -> None:
    assert QuadraticField(5).embeddings(RR).cardinality() == 2


def test_two_ramifies_in_q_root_minus_five() -> None:
    primes = QuadraticField(-5).primes_above(ZZ(2))

    assert primes.cardinality() == 1


def test_the_real_cube_root_of_two_generates_a_non_galois_cubic_field() -> None:
    x = QQ["x"].algebra_generator("x")
    field = NumberFields()(x**3 - 2)

    assert field.degree() == 3
    assert field.discriminant() == -108
    assert not field.is_galois()
    assert field.normal_closure().degree() == 6


def test_signatures_count_real_and_complex_places() -> None:
    assert QuadraticField(-5).signature() == (0, 1)
    assert QuadraticField(5).signature() == (2, 0)
    assert CyclotomicField(5).signature() == (0, 2)


def test_the_ring_of_integers_of_a_quadratic_field_has_rank_two() -> None:
    assert QuadraticField(5).ring_of_integers().module_rank() == 2
