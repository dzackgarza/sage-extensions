r"""A chart with no cutting conditions covers its own domain, not the manifold.

A chart is defined on an open subset $U$ of $M$ (Lee, *Introduction to Smooth Manifolds*,
2nd ed., Ch. 1); when $U$ is a proper subset the chart selects no points outside it, and it
says nothing about the points of $M \setminus U$.  A family containing such a chart
therefore covers $M$ only when the chart is the whole manifold or the family covers the
rest; reading a chart with no conditions as covering everything accepts a function or a
section that has no value at the points it never reaches.

The specimen is the circle, presented by two charts: a function stated on the north chart
alone leaves every point of the south chart without a value.
"""

import pytest

from sage_extensions.all import *


def _the_circle():
    r"""$S^1$, its two stereographic charts, and the north coordinate."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    return circle, north, north.coordinate(0)


def test_a_function_on_the_north_chart_alone_is_refused() -> None:
    r"""The chart $U_N$ misses the north pole, so a function stated only there is not a function on $S^1$.

    The refusal is one of the two the tree states: the family does not cover, or coverage is
    undecided.  What it must not be is acceptance.
    """
    circle, north, x = _the_circle()

    with pytest.raises((AssertionError, CoverageUndecided)):
        circle.smooth_function({"U_N": x})


def test_a_section_on_the_north_chart_alone_is_refused() -> None:
    r"""The same for a section of the tangent bundle: one chart of the circle is no cover of it."""
    circle, north, x = _the_circle()
    sections = circle.tangent_bundle().sections()

    with pytest.raises((AssertionError, CoverageUndecided)):
        sections.section({"U_N": (x,)})


def test_the_two_charts_together_are_a_cover() -> None:
    r"""Both charts of the circle stated together are admitted: every point is in one of them.

    The function is $x$ on $U_N$ and $1/y$ on $U_S$, which is the same function under
    $y = 1/x$, and it takes the same value at the same point.
    """
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]

    function = circle.smooth_function(
        {
            "U_N": north.coordinate(0),
            "U_S": south.section_ratio(south.function_ring().one(), south.coordinate(0)),
        }
    )

    at = circle.point((2,), "U_N")
    assert function(at) == RR(2)
