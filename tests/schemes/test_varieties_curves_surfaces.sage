r"""Varieties, curves and surfaces: integral separated schemes of finite type.

A variety is integral, separated and of finite type over its base; a curve and a
surface are the varieties of relative dimension one and two.
"""

from sage_extensions.all import *


def test_two_crossing_lines_are_reducible_while_the_parabola_is_a_curve() -> None:
    r"""`V(xy) = V(x) \cup V(y)` is one-dimensional with two irreducible components, so
    it is not a variety; `V(y - x^2) \cong \mathbb{A}^1` is a curve."""
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    two_lines = plane.closed_subscheme(x * y)
    parabola = plane.closed_subscheme(y - x**2)

    assert two_lines.relative_dimension() == 1
    assert two_lines.irreducible_components().cardinality() == 2
    assert not two_lines.is_integral()
    assert two_lines not in Varieties(QQ)
    assert parabola.is_integral()
    assert parabola in Curves(QQ)


def test_the_finite_type_hypothesis_excludes_the_spectrum_of_a_function_field() -> None:
    rational_functions = QQ.polynomial_ring("t").fraction_field()
    point = (rational_functions).affine_spectrum(base_ring=QQ)

    assert point in IntegralSchemes(QQ)
    assert point in Schemes(QQ).Separated()
    assert point not in Schemes(QQ).FiniteType()
    assert point not in Varieties(QQ)


def test_the_affine_line_over_the_integers_has_relative_dimension_one_and_absolute_dimension_two() -> None:
    r"""`\dim \mathbb{Z}[x] = \dim \mathbb{Z} + 1 = 2`, so `\mathbb{A}^1_{\mathbb{Z}}` has
    relative dimension 1 over `\operatorname{Spec} \mathbb{Z}`."""
    line = AffineSpaces(ZZ)(1)

    assert line.relative_dimension() == 1
    assert line.coordinate_ring().krull_dimension() == 2
    assert line in Curves(ZZ)


def test_the_cuspidal_cubic_has_arithmetic_genus_one_and_geometric_genus_zero() -> None:
    r"""A plane cubic has arithmetic genus `(3-1)(3-2)/2 = 1`; the cusp `y^2 z = x^3`
    is the image of `\mathbb{P}^1` under `(s:t) \mapsto (s^2 t : s^3 : t^3)`, so its
    geometric genus is 0 (Hartshorne, *Algebraic Geometry*, I.7.2 and Ex. IV.1.8)."""
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    x, y, z = plane.homogeneous_coordinate_generators()
    cusp = plane.closed_subscheme(y**2 * z - x**3)

    assert cusp.arithmetic_genus() == 1
    assert cusp.geometric_genus() == 0
    assert cusp.singular_locus().point_count() == 1
