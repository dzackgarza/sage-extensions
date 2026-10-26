r"""Finite-length presented modules use their selected relation module."""

from sage_extensions.all import *


def test_square_of_rational_origin_has_length_three() -> None:
    ring = QQ.polynomial_ring("x,y")
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    maximal = ring.ideal(x, y)
    module = maximal.power(2).inclusion().cokernel()
    point = ring.spectrum()(maximal)

    assert module.finite_length_at_closed_point(point) == ZZ(3)


def test_nonrational_closed_point_divides_base_dimension_by_residue_degree() -> None:
    ring = QQ.polynomial_ring("x,y")
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    maximal = ring.ideal(x**2 + 1, y)
    module = maximal.inclusion().cokernel()
    point = ring.spectrum()(maximal)

    assert point.residue_degree() == ZZ(2)
    assert module.finite_length_at_closed_point(point) == ZZ(1)
