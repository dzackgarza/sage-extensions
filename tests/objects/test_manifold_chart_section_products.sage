r"""A product of chart sections is a section of the same ring, of the same domain and value field.

A chart ``phi : U -> K^n`` is a homeomorphism of an open subset ``U`` of the
manifold onto an open subset of ``K^n`` (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 1), so its coordinates are functions on ``U``, and the
real-valued functions on ``U`` of the manifold's class form a ring under the
pointwise product: ``(f g)(p) = f(p) g(p)``.  The product of two coordinate
sections is therefore a section of that same ring -- the same domain, the same
regularity and the same value field -- and its value at a point is the product
of the coordinates there, not a symbolic expression.

Writing such a section into an atlas transition is the same operation: the
coordinate change is a tuple of functions of the source coordinates, and a
transition whose coordinates are squares and products of the source coordinates
is those functions.
"""

from sage_extensions.all import *


def test_the_product_and_power_of_chart_coordinates_are_sections_of_the_same_ring() -> None:
    r"""On ``R^2`` with the chart ``x, y``, the products ``x y``, ``x^2`` and ``x^2 + y^2`` are sections of the chart's function ring and take the products of the coordinates at the point ``(3, -2)``."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    functions = chart.function_ring()
    x = chart.coordinate(0)
    y = chart.coordinate(1)
    point = plane((3, -2))

    assert (x * y).parent() is functions
    assert (x**2).parent() is functions
    assert (x**2 + y**2).parent() is functions
    assert (x * y).parent().domain() is functions.domain()
    assert (x * y)(point) == RR(-6)
    assert (x**2)(point) == RR(9)
    assert (y**2)(point) == RR(4)
    assert (x**2 + y**2)(point) == RR(13)
    assert (x * y * x)(point) == RR(-18)


def test_a_transition_written_with_squares_and_products_of_coordinates_is_those_functions() -> None:
    r"""The coordinate change ``(x, y) |-> (x^2, x y)`` carries ``(3, -2)`` to ``(9, -6)``: the squares and products of chart sections are coordinate expressions of the atlas."""
    plane = SmoothManifolds()(2, "R^2")
    source = plane.chart("U", "x y")
    target = plane.chart("V", "u v")
    transition = plane.transition_map(
        "U",
        "V",
        (source.coordinate(0) ** 2, source.coordinate(0) * source.coordinate(1)),
        (target.coordinate(0), target.coordinate(1)),
    )

    assert tuple(transition(3, -2)) == (RR(9), RR(-6))
    assert tuple(transition(-2, 3)) == (RR(4), RR(-6))
