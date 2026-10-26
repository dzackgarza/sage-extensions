r"""Closed subschemes of the affine plane over QQ cut out by equations."""

from sage_extensions.all import *


def _plane():
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_ring()
    return plane, ring.algebra_generator("x"), ring.algebra_generator("y")


def test_the_parabola_y_equals_x_squared_is_isomorphic_to_the_affine_line() -> None:
    r"""`\mathbb{Q}[x, y]/(y - x^2) \cong \mathbb{Q}[x]`."""
    plane, x, y = _plane()
    parabola = plane.closed_subscheme(y - x**2)

    assert parabola.is_isomorphic(AffineSpaces(QQ)(1))
    assert parabola.codimension() == 1


def test_the_tangent_line_meets_the_parabola_in_a_double_point() -> None:
    r"""`V(y - x^2) \cap V(y) = \operatorname{Spec} \mathbb{Q}[x]/(x^2)`: one point, of
    length 2 and not reduced, while `V(y - x^2) \cap V(y - 1)` is two reduced points."""
    plane, x, y = _plane()
    parabola = plane.closed_subscheme(y - x**2)
    tangent = parabola.intersection(plane.closed_subscheme(y))
    secant = parabola.intersection(plane.closed_subscheme(y - 1))

    assert tangent.relative_dimension() == 0
    assert tangent.coordinate_ring().dimension() == 2
    assert not tangent.is_reduced()
    assert secant.coordinate_ring().dimension() == 2
    assert secant.is_reduced()
