r"""A chart cut by two conditions leaves out the union of their zero sets, and coverage must not read it as one intersection.

A chart read where $g$ and $h$ both do not vanish is the set $\{g \ne 0\} \cap \{h \ne 0\}$,
so a point is *outside* it where $g$ vanishes **or** $h$ does (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 1).  A family's uncovered set is therefore an intersection of
unions, and reading it as the intersection of all the conditions at once makes it smaller
than it is: the plane's charts $\{x \ne 0, y \ne 0\}$ and $\{x \ne 1, y \ne 0\}$ would then
"cover" the plane, while the origin lies in neither of them.

Two things follow, and both are asserted here: such a family does **not** cover, and a
member all of whose conditions vanish nowhere does cover, since cutting by a condition that
never vanishes selects nothing.
"""

import pytest

from sage_extensions.all import *


def _the_plane_with_two_cut_charts():
    r"""The plane, its chart, and the two charts each cut by two conditions."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    return plane, (
        plane.chart_on_open_subset("E1", "x y", "U", (x, y)),
        plane.chart_on_open_subset("E2", "x y", "U", (x + (-1), y)),
    )


def test_two_doubly_cut_charts_that_miss_the_origin_do_not_cover() -> None:
    r"""$\{x \ne 0, y \ne 0\}$ and $\{x \ne 1, y \ne 0\}$ both miss the origin, so the family does not cover.

    The origin has $y = 0$, which is a condition of both charts: it is outside each of them,
    and no other point of the family reaches it.  A section stated on the two charts is
    refused.
    """
    plane, (first, second) = _the_plane_with_two_cut_charts()
    sections = plane.tangent_bundle().sections()

    with pytest.raises(AssertionError):
        sections.section(
            {
                "E1": (first.function_ring().one(), first.function_ring().zero()),
                "E2": (second.function_ring().one(), second.function_ring().zero()),
            }
        )


def test_a_chart_whose_conditions_all_vanish_nowhere_covers_the_plane() -> None:
    r"""$\{x^2+1 \ne 0, y^2+1 \ne 0\}$ is the whole plane, so a section stated on it alone is admitted.

    Neither condition has a zero, so the chart is not a proper subset of the plane and it
    covers it on its own.
    """
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    whole = plane.chart_on_open_subset("E3", "x y", "U", (x**2 + 1, y**2 + 1))

    section = plane.tangent_bundle().sections().section(
        {"E3": (whole.function_ring().one(), whole.function_ring().zero())}
    )

    assert section.components()["E3"][0](plane((4, 5))) == RR(1)
