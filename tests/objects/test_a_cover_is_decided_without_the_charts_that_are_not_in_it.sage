r"""A family's coverage does not depend on the charts that are not in it.

A family of charts covers a manifold when no point of it lies outside all of them, and the
condition a chart contributes is where the functions cutting it vanish (Lee, *Introduction
to Smooth Manifolds*, 2nd ed., Ch. 1).  A chart that is *not* in the family is a point of
the manifold like any other: the family must cover it too, and it does so exactly when no
point of that chart lies outside every member.  A member's cutting condition is read in
that chart by composing it with the coordinate change the atlas states, so coverage does
not need one chart to contain another.

The specimen is the plane with four charts on it: the chart cut by $x^2+1$, the chart cut
by $y$, and the complements of two distinct points.  The two punctured charts cover the
plane -- and so cover the chart cut by $y$ and the one cut by $x^2+1$ -- although neither
contains the other.
"""

import pytest

from sage_extensions.all import *


def _the_plane_with_four_charts():
    r"""The plane, its chart, and the four cut charts, registered on the one manifold."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    cuts = {
        label: plane.chart_on_open_subset(label, "x y", "U", condition)
        for label, condition in (
            ("N1", (x**2 + 1,)),
            ("N2", (y,)),
            ("N3", (x**2 + y**2,)),
            ("N4", ((x + (-1)) ** 2 + (y + (-1)) ** 2,)),
        )
    }
    return plane, cuts


def test_two_punctured_charts_cover_the_plane_though_other_charts_are_registered() -> None:
    r"""The complements of two distinct points cover the plane, and a section stated on them is admitted.

    The point each punctured chart cuts out is covered by the other, so the intersection of
    the two zero sets is empty; the other two charts on the manifold change nothing.
    """
    plane, cuts = _the_plane_with_four_charts()
    sections = plane.tangent_bundle().sections()
    first, second = cuts["N3"], cuts["N4"]

    section = sections.section(
        {
            "N3": (first.function_ring().one(), first.function_ring().zero()),
            "N4": (second.function_ring().one(), second.function_ring().zero()),
        }
    )

    assert section.parent() is sections
    assert section.components()["N3"][0](plane((0, 1))) == RR(1)
    assert section.components()["N4"][0](plane((0, 0))) == RR(1)


def test_one_punctured_chart_still_does_not_cover() -> None:
    r"""The complement of one point misses that point, which no chart of the family reaches."""
    plane, cuts = _the_plane_with_four_charts()
    sections = plane.tangent_bundle().sections()
    punctured = cuts["N3"]

    with pytest.raises(AssertionError):
        sections.section({"N3": (punctured.function_ring().one(), punctured.function_ring().zero())})
