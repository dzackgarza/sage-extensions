r"""Normalization, conductor, and delta for represented affine curve domains."""

import pytest

from sage_extensions.all import *


def _cusp_ring():
    polynomial = QQ.polynomial_ring(("x", "y"))
    x, y = (polynomial.algebra_generator(name) for name in ("x", "y"))
    return polynomial.quotient_ring(polynomial.ideal(y**2 - x**3))


def test_cusp_normalization_retains_the_actual_finite_birational_map() -> None:
    cusp = _cusp_ring()
    normalization = cusp.normalization()
    normalization_map = cusp.normalization_map()

    assert normalization_map.domain() is cusp
    assert normalization_map.codomain() is normalization
    assert normalization.is_normal()
    assert not cusp.is_normal()
    assert cusp.delta_invariant() == 1


def test_cusp_conductor_is_the_maximal_ideal_at_the_cusp() -> None:
    r"""A = Q[t^2, t^3] = Q[x,y]/(y^2 - x^3) inside its normalization Q[t]: the
    conductor {a : a Q[t] in A} is t^2 Q[t] = (x, y) (Serre, Algebraic Groups and
    Class Fields, IV.11)."""
    polynomial = QQ.polynomial_ring(("x", "y"))
    x, y = (polynomial.algebra_generator(name) for name in ("x", "y"))
    cusp = polynomial.quotient_ring(polynomial.ideal(y**2 - x**3))
    to_cusp = cusp.quotient_map()

    assert cusp.conductor_ideal() == cusp.ideal(to_cusp(x), to_cusp(y))


def test_a_smooth_affine_line_is_its_own_normalization() -> None:
    polynomial = QQ.polynomial_ring(("x", "y"))
    x, y = (polynomial.algebra_generator(name) for name in ("x", "y"))
    line = polynomial.quotient_ring(polynomial.ideal(y - x))

    assert line.is_normal()
    assert line.delta_invariant() == 0
    assert line.conductor_ideal() == line.ideal(line.one())


def test_normalization_rejects_a_non_polynomial_quotient_at_its_frontier() -> None:
    quotient = ZZ.quotient_ring(ZZ.ideal(ZZ(6)))

    with pytest.raises(AssertionError):
        quotient.normalization()
