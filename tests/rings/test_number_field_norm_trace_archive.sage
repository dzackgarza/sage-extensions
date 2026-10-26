r"""Archive reconciliation for number-field norm and trace."""

from sage_extensions.all import *


def _quadratic_field():
    polynomial_ring = QQ.polynomial_ring("x")
    x = polynomial_ring.algebra_generator("x")
    return (x**2 - 2).number_field("a")


def test_norm_and_trace_are_invariants_of_the_live_multiplication_map() -> None:
    field = _quadratic_field()
    element = field.one() + field.primitive_element()
    multiplication = element.multiplication_morphism()

    assert element.norm() == multiplication.determinant() == QQ(-1)
    assert element.trace() == multiplication.trace() == QQ(2)


def test_norm_and_trace_use_the_full_field_degree_for_a_rational_element() -> None:
    field = _quadratic_field()
    element = field(QQ(3))

    assert element.norm() == QQ(9)
    assert element.trace() == QQ(6)
    assert element.characteristic_polynomial().degree() == field.degree()
    assert element.minimal_polynomial().degree() == 1
