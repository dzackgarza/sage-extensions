r"""Arithmetic genus of plane curves and the curve category.

Source: Hartshorne, *Algebraic Geometry*, Exercise I.7.2 (checked): ``p_a(Y) = (-1)^r (P_Y(0) - 1)``,
``p_a(P^n) = 0``, and a plane curve of degree ``d`` has ``p_a = (d - 1)(d - 2)/2``.  So the Fermat
cubic has ``p_a = 1`` and the Fermat quartic ``p_a = 3``; the cuspidal cubic ``y^2 z = x^3`` also
has ``p_a = 1`` and is not smooth.
"""

from sage_extensions.all import *


def _projective_plane():
    plane = ProjectiveSpaces(QQ)(2)
    ring = QQ["x0,x1,x2"]
    return plane, ring.algebra_generator("x0"), ring.algebra_generator("x1"), ring.algebra_generator("x2")


def test_the_fermat_cubic_is_a_plane_curve_of_arithmetic_genus_one() -> None:
    r"""``d = 3`` gives ``p_a = 1``."""
    plane, x0, x1, x2 = _projective_plane()
    cubic = plane.closed_subscheme(x0**3 + x1**3 + x2**3)

    assert cubic.inclusion().codomain() is plane
    assert cubic.dimension() == 1
    assert cubic.arithmetic_genus() == 1


def test_the_fermat_quartic_has_arithmetic_genus_three() -> None:
    r"""``d = 4`` gives ``p_a = 3``."""
    plane, x0, x1, x2 = _projective_plane()

    assert plane.closed_subscheme(x0**4 + x1**4 + x2**4).arithmetic_genus() == 3


def test_the_projective_plane_has_arithmetic_genus_zero() -> None:
    r"""``p_a(P^n) = 0`` (Exercise I.7.2(a)), here for ``P^1`` as a curve."""
    assert ProjectiveSpaces(QQ)(1).arithmetic_genus() == 0


def test_the_cuspidal_cubic_is_singular_of_arithmetic_genus_one() -> None:
    r"""``y^2 z = x^3`` has degree 3, so ``p_a = 1``, and it is singular at ``(0 : 0 : 1)``."""
    plane, x0, x1, x2 = _projective_plane()
    cusp = plane.closed_subscheme(x1**2 * x2 - x0**3)

    assert cusp.arithmetic_genus() == 1
    assert not cusp.is_smooth()


def test_a_parabola_is_an_affine_curve() -> None:
    r"""``V(y - x^2)`` in ``A^2``: the ideal is prime and the quotient ``Q[x]`` has dimension one."""
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    parabola = Curves(QQ).from_equation(y - x**2)

    assert parabola in Curves(QQ)
    assert parabola.dimension() == 1
