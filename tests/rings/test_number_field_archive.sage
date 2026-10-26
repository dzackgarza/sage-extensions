r"""Multiplication endomorphisms, norms, traces and units of ``QQ(sqrt 2)``."""

from sage_extensions.all import *  # noqa: F401,F403


def _quadratic_field():
    polynomial_ring = QQ.polynomial_ring("x")
    x = polynomial_ring.algebra_generator("x")
    return (x**2 - 2).number_field("a")


def test_number_field_element_retains_its_multiplication_endomorphism() -> None:
    field = _quadratic_field()
    element = field.primitive_element() + field.one()
    morphism = element.multiplication_morphism()

    assert morphism.domain().base_ring() is QQ
    assert morphism.domain().module_rank() == field.degree()
    assert morphism.codomain() is morphism.domain()
    assert morphism.matrix() == element.multiplication_matrix()
    matrix = element.multiplication_matrix()
    assert matrix[0, 0] == 1
    assert matrix[1, 0] == 1
    assert matrix[0, 1] == 2
    assert matrix[1, 1] == 1


def test_multiplication_matrix_recovers_norm_and_trace() -> None:
    field = _quadratic_field()
    element = field.primitive_element() + field.one()
    matrix = element.multiplication_matrix()

    assert matrix.determinant() == element.norm()
    assert matrix.trace() == element.trace()


def test_one_plus_root_two_is_a_unit_of_norm_minus_one_with_inverse_root_two_minus_one() -> None:
    r"""``(1 + sqrt 2)(sqrt 2 - 1) = 2 - 1 = 1``, so ``1 + sqrt 2`` is a unit of
    ``ZZ[sqrt 2]``, of norm ``1 - 2 = -1`` (the fundamental unit; Neukirch,
    *Algebraic Number Theory*, I.7)."""
    field = _quadratic_field()
    a = field.primitive_element()
    unit = field.one() + a

    assert unit.norm() == -1
    assert unit.trace() == 2
    assert unit.inverse() == a - field.one()
    assert unit.inverse().norm() == -1
    assert unit.inverse() in field.ring_of_integers()
