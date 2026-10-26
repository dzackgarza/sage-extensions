r"""Supported local intersections use Serre's alternating Tor lengths."""

from sage_extensions.all import *


def test_self_intersection_of_origin_on_affine_line_has_cancelling_tor_one() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))
    ring = line.coordinate_algebra()
    x = ring.algebra_generator("x")
    origin = line.closed_subscheme(x)
    point = line.underlying_space()(ring.ideal(x))

    intersection = origin.serre_intersection(origin, point)

    assert intersection.tor_length(0) == ZZ(1)
    assert intersection.tor_length(1) == ZZ(1)
    assert not intersection.tor_module(1).is_zero()
    assert intersection.multiplicity() == ZZ(0)
    assert origin.serre_intersection_multiplicity(origin, point) == ZZ(0)


def test_proper_tangent_intersection_agrees_with_surface_colength_specialization() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    tangent = plane.closed_subscheme(y)
    parabola = plane.closed_subscheme(y - x**2)
    point = plane.underlying_space()(ring.ideal(x, y))

    intersection = tangent.serre_intersection(parabola, point)

    assert intersection.tor_length(0) == ZZ(2)
    assert intersection.tor_length(1) == ZZ(0)
    assert intersection.multiplicity() == ZZ(2)
    assert tangent.intersection_multiplicity(parabola, point) == ZZ(2)
