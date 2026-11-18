r"""The stereographic transition of the sphere divides the coordinates by their squared norm, on the overlap where that norm does not vanish.

A chart ``phi : U -> K^n`` of a manifold is a homeomorphism of an open subset
``U`` onto an open subset of ``K^n`` (Lee, *Introduction to Smooth Manifolds*,
2nd ed., Ch. 1), so its coordinates are sections of the ring of functions on
``U``, and their products, powers and sums are sections of that same ring,
taking at a point the products, powers and sums of the coordinates there.  A
sum written in the session starts from the integer ``0``, so the ring reads that
integer as the constant section with value zero.

The stereographic atlas of ``S^n`` is the pair of charts ``U_N = S^n - {N}`` and
``U_S = S^n - {S}``, with the coordinate change ``y = x/|x|^2`` on the overlap,
where ``|x|^2 != 0`` (Lee, Ch. 1).  The squared norm is the sum of the squares
of the source coordinates, a section of the source chart's function ring, and
the coordinate change divides by it: a quotient of two sections is a function
on the open subset where the second does not vanish, which is the overlap the
transition states.  ``S^1`` and ``S^2`` are the smallest of these: one and two
coordinates, the same norm and the same quotient.
"""

import pytest

from sage_extensions.all import *


def test_a_sum_of_squares_of_chart_coordinates_is_a_section_of_the_chart_function_ring() -> None:
    r"""On ``R^2`` with the chart ``x, y``, the sum ``x^2 + y^2`` written as a session sum is a section of the chart's function ring, of the same domain, and takes ``13`` at ``(3, -2)``."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    functions = chart.function_ring()
    x = chart.coordinate(0)
    y = chart.coordinate(1)
    point = plane((3, -2))

    norm_squared = sum(coordinate**2 for coordinate in chart.coordinates())

    assert norm_squared.parent() is functions
    assert norm_squared.parent().domain() is functions.domain()
    assert norm_squared(point) == RR(13)
    assert norm_squared(point) == (x**2 + y**2)(point)
    assert (norm_squared + x)(point) == RR(16)
    assert (norm_squared * y)(point) == RR(-26)


def test_the_squared_norm_of_a_chart_of_the_two_sphere_is_a_section_of_that_chart_function_ring() -> None:
    r"""The coordinates of the chart ``U_N`` of ``S^2`` have squared norm ``13`` at the point with coordinates ``(3, -2)``, and that norm is a section of the ring of functions on that chart's domain."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    point = sphere((3, -2), "U_N")

    norm_squared = sum(coordinate**2 for coordinate in north.coordinates())

    assert norm_squared.parent() is north.function_ring()
    assert norm_squared.parent().domain() is north.domain()
    assert norm_squared(point) == RR(13)


def test_the_stereographic_transition_of_the_two_sphere_divides_the_coordinates_by_their_squared_norm() -> None:
    r"""On ``S^2`` the transition ``U_N -> U_S`` carries ``(3, -2)`` to ``(3/13, -2/13)`` -- ``y = x/|x|^2`` -- and back, and it refuses the pole, where the squared norm vanishes."""
    sphere = SmoothManifolds().sphere(2)
    transition = sphere.transition("U_N", "U_S")

    image = tuple(transition(3, -2))

    assert image == (RR(3) / RR(13), RR(-2) / RR(13))
    assert tuple(transition.inverse()(*image)) == (RR(3), RR(-2))
    with pytest.raises(AssertionError):
        transition(0, 0)


def test_the_stereographic_transition_of_the_circle_is_the_reciprocal_of_its_coordinate() -> None:
    r"""On ``S^1``, the smallest sphere, the transition ``U_N -> U_S`` carries the coordinate ``2`` to ``1/2``, ``y = x/x^2``, and back."""
    circle = SmoothManifolds().sphere(1)
    transition = circle.transition("U_N", "U_S")

    assert tuple(transition(2)) == (RR(1) / RR(2),)
    assert tuple(transition.inverse()(RR(1) / RR(2))) == (RR(2),)
    with pytest.raises(AssertionError):
        transition(0)


def test_a_quotient_of_sections_is_a_function_on_the_open_subset_where_its_denominator_does_not_vanish() -> None:
    r"""On ``R^2`` the quotient ``y/x`` is a function on the open subset ``{x != 0}``: there it is the quotient of the two restricted sections, read at the point the open subset's own chart gives, and at ``x = 0`` it is refused."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x = chart.coordinate(0)
    y = chart.coordinate(1)
    nonzero = plane.chart_on_open_subset("V", "x y", "U", (x,))
    domain = nonzero.domain()
    inner = domain(plane((3, -2), "U"))
    quotient = chart.section_ratio(y, x)
    restricted_x = nonzero.function_ring()(x)
    restricted_y = nonzero.function_ring()(y)

    assert quotient.numerator().parent() is chart.function_ring()
    assert quotient.denominator().parent() is chart.function_ring()
    assert domain is not plane
    assert nonzero.function_ring().domain() is domain
    assert plane.open_submanifold_inclusion(domain)(inner) == plane((3, -2), "U")
    assert restricted_x.parent() is nonzero.function_ring()
    assert (restricted_x(inner), restricted_y(inner)) == (RR(3), RR(-2))
    assert quotient(inner) == restricted_y(inner) / restricted_x(inner)
    assert quotient(inner) == RR(-2) / RR(3)
    with pytest.raises(AssertionError):
        quotient(plane((0, -2), "U"))


def test_the_stereographic_overlap_is_an_open_subset_of_the_chart_the_quotient_divides_by() -> None:
    r"""``U_N cap U_S`` is the open subset of the chart ``U_N`` where the squared norm of the coordinates does not vanish, and the coordinate change there is the quotient of the restricted sections."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    norm_squared = sum(coordinate**2 for coordinate in north.coordinates())
    overlap = sphere.chart_on_open_subset("U_N_overlap", "x1 x2", "U_N", (norm_squared,))
    domain = overlap.domain()
    inner = domain(sphere((3, -2), "U_N"))
    quotient = north.section_ratio(north.coordinate(0), norm_squared)

    assert domain is not sphere
    assert north.domain() is not sphere
    assert overlap.function_ring().domain() is domain
    assert tuple(overlap.coordinate(index)(inner) for index in (0, 1)) == (RR(3), RR(-2))
    assert overlap.function_ring()(norm_squared)(inner) == RR(13)
    assert quotient(inner) == (
        overlap.function_ring()(north.coordinate(0))(inner)
        / overlap.function_ring()(norm_squared)(inner)
    )
    assert quotient(inner) == RR(3) / RR(13)
