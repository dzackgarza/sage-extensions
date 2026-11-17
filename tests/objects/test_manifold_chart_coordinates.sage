r"""A chart coordinate of a real manifold is the function it is.

A chart ``phi : U -> RR^n`` is a homeomorphism of an open subset ``U`` of the
manifold onto an open subset of ``RR^n`` (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 1), so each of its coordinates is a real-valued
function on ``U``: a section of the ring of functions the manifold assigns to
that open set.  Evaluating such a section at a point of ``U`` gives the point's
coordinate, an exact real number.

The SageManifolds chart is the private realization.  It supplies the
coordinate *symbols* that the chart, transition and point adapters speak about a
coordinate by, and the symbolic engine is no owned ring: it is the private
representation of a coordinate, never a parent of one.
"""

from sage_extensions.all import *


def test_a_chart_coordinate_evaluated_at_a_point_is_the_point_coordinate() -> None:
    r"""On ``R^2`` with the chart ``x, y``, the point ``(3, -3)`` has first coordinate 3 and second -3, and ``(-1, 4)`` has its own."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")

    assert chart.coordinate(0)(plane((3, -3))) == RR(3)
    assert chart.coordinate(1)(plane((3, -3))) == RR(-3)
    assert chart.coordinate(0)(plane((-1, 4))) == RR(-1)
    assert chart.coordinate(1)(plane((-1, 4))) == RR(4)
    assert tuple(chart(plane((3, -3)))) == (RR(3), RR(-3))


def test_a_chart_coordinate_is_a_section_of_the_ring_of_functions_on_the_chart_domain() -> None:
    r"""The chart ``U`` of ``R^2`` is defined on the whole plane, and its coordinates are elements of one ring of real-valued functions on that domain, which is a ring of functions and not a ring of symbols."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    functions = chart.function_ring()

    assert chart.domain() is plane
    assert functions.domain() is plane
    assert functions in Algebras(RR)
    assert chart.coordinate(0).parent() is functions
    assert chart.coordinate(1).parent() is functions
