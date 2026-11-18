r"""A numeral is the constant function, so it is a section of a chart's function ring.

The ring of functions on a chart's domain is an algebra over the field its values lie
in, and its unit is the constant function taking the value one; the constants are
therefore sections of it, and a numeral -- the session's own integer, or a value of the
coordinate field -- is the constant section with that value (Lee, *Introduction to
Smooth Manifolds*, 2nd ed., Ch. 2, where the smooth functions on a manifold form an
algebra over ``R`` with the constant functions as the image of ``R``).  So a sum written
in a session, ``1 + x^2``, is a section of the same ring as its summand ``x^2``, and it
takes at a point the sum of the values there.

The specimen is the smallest that decides it: one chart of the plane, a coordinate, and
the numeral ``1`` of the session.
"""

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart ``x y``, and the two coordinates."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    return plane, chart, chart.coordinate(0), chart.coordinate(1)


def test_a_numeral_adds_to_a_chart_coordinate_as_the_constant_section() -> None:
    r"""``1 + x^2`` and ``x^2 + 1`` are sections of the chart's function ring, taking ``10`` at ``(3, -2)``.

    The numeral is the constant function with that value, and the ring's sum is the
    pointwise sum, so both orders of the sum are the section ``x^2 + 1``.
    """
    plane, chart, x, y = _the_plane()
    point = plane((3, -2))

    left = 1 + x**2
    right = x**2 + 1

    assert left.parent() is chart.function_ring()
    assert right.parent() is chart.function_ring()
    assert left(point) == RR(10)
    assert right(point) == RR(10)
    assert (1 + x**2 + y)(point) == RR(8)


def test_a_numeral_scales_a_chart_coordinate_from_either_side() -> None:
    r"""``2 x`` and ``x 2`` are the section ``x + x``, taking ``6`` at ``(3, -2)``, and ``-(1 + y^2)`` takes ``-5``."""
    plane, chart, x, y = _the_plane()
    point = plane((3, -2))

    assert (2 * x)(point) == RR(6)
    assert (x * 2)(point) == RR(6)
    assert (2 * x)(point) == (x + x)(point)
    assert (-(1 + y**2))(point) == RR(-5)
    assert (2 * x + 1)(point) == RR(7)


def test_a_value_of_the_coordinate_field_is_the_constant_section_with_that_value() -> None:
    r"""``RR(2) x`` is ``x + x``, and ``(1/2) x`` takes ``3/2`` at ``(3, -2)``: the constants are the coordinate field's image."""
    plane, chart, x, _y = _the_plane()
    point = plane((3, -2))

    assert (RR(2) * x)(point) == RR(6)
    assert ((QQ(1) / QQ(2)) * x)(point) == RR(3) / RR(2)
    assert (((QQ(1) / QQ(2)) * x) + (QQ(1) / QQ(2)))(point) == RR(2)
