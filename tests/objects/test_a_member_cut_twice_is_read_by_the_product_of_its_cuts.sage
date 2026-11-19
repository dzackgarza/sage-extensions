r"""A member cut by several conditions leaves out the union of their zero sets, which is one zero set: that of their product.

A chart read where $g$ and $h$ both do not vanish leaves a point out where $g$ vanishes or
$h$ does, and a product vanishes exactly where one of its factors does.  So a member cut by
several conditions contributes the single condition $g \cdot h$, and a family's uncovered
set is the intersection of those products (Lee, *Introduction to Smooth Manifolds*, 2nd
ed., Ch. 1).  A condition that vanishes nowhere selects nothing and is dropped first.

The specimens are the plane's two families that separate the readings: the charts cut by
$\{x^2+1, x\}$ and $\{y^2+1, x-1\}$, whose products are $x$ and $x-1$ and which cover the
plane, and the charts cut by $\{x, y\}$ and $\{x-1, y\}$, whose products are $xy$ and
$(x-1)y$ and which miss the origin.
"""

import pytest

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, and the two coordinates."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    return plane, chart, chart.coordinate(0), chart.coordinate(1)


def test_redundant_cuts_are_dropped_and_the_cover_is_decided() -> None:
    r"""$\{x^2+1, x\}$ is $\{x \ne 0\}$ and $\{y^2+1, x-1\}$ is $\{x \ne 1\}$, and the two cover the plane.

    Every point has $x \ne 0$ or $x \ne 1$; a section stated on the two charts is admitted.
    """
    plane, _chart, x, y = _the_plane()
    first = plane.chart_on_open_subset("F1", "x y", "U", (x**2 + 1, x))
    second = plane.chart_on_open_subset("F2", "x y", "U", (y**2 + 1, x + (-1)))
    sections = plane.tangent_bundle().sections()

    section = sections.section(
        {
            "F1": (first.function_ring().one(), first.function_ring().zero()),
            "F2": (second.function_ring().one(), second.function_ring().zero()),
        }
    )

    assert section.components()["F1"][0](plane((1, 4))) == RR(1)
    assert section.components()["F2"][0](plane((0, 4))) == RR(1)


def test_two_doubly_cut_charts_that_miss_the_origin_still_do_not_cover() -> None:
    r"""$\{x, y\}$ and $\{x-1, y\}$ contribute $xy$ and $(x-1)y$, which both vanish at the origin.

    The origin is outside both charts, so the family does not cover and the section is
    refused -- the reading the products give, and the one the whole intersection fails to
    give.
    """
    plane, _chart, x, y = _the_plane()
    first = plane.chart_on_open_subset("G1", "x y", "U", (x, y))
    second = plane.chart_on_open_subset("G2", "x y", "U", (x + (-1), y))
    sections = plane.tangent_bundle().sections()

    with pytest.raises(AssertionError):
        sections.section(
            {
                "G1": (first.function_ring().one(), first.function_ring().zero()),
                "G2": (second.function_ring().one(), second.function_ring().zero()),
            }
        )


def test_a_member_whose_cuts_all_vanish_nowhere_covers_on_its_own() -> None:
    r"""$\{x^2+1, y^2+1\}$ selects nothing away, so that chart is the plane."""
    plane, _chart, x, y = _the_plane()
    whole = plane.chart_on_open_subset("H1", "x y", "U", (x**2 + 1, y**2 + 1))

    section = plane.tangent_bundle().sections().section(
        {"H1": (whole.function_ring().one(), whole.function_ring().zero())}
    )

    assert section.components()["H1"][0](plane((7, 8))) == RR(1)
