r"""A family whose coverage is not certified is *undecided*, and the refusal says so.

The charts of an atlas cover it, and a family of them covers it when no point lies outside
all of them (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  A decision that
finds no certificate has not decided **that the family does not cover** -- it has decided
nothing -- and reporting the second as the first is a false claim about the mathematics.
The two answers are therefore distinct calls, and a caller that cannot certify a cover
refuses with the undecided answer rather than the negative one.

The specimen is the plane's chart cut by $g = x^6 - 2x^3 + 2 = (x^3-1)^2 + 1$, which is at
least one and so vanishes nowhere: that chart is the whole plane and the family covers it.
No certificate at hand decides the sixth-degree $g$, so the answer must be undecided.
"""

import pytest

from sage_extensions.all import *


def _the_plane_with_a_positive_sixth_degree_cut():
    r"""The plane, its chart, and the chart cut by $(x^3-1)^2 + 1$, which vanishes nowhere."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    whole = plane.chart_on_open_subset("K1", "x y", "U", ((x**3 + (-1)) ** 2 + 1,))
    return plane, whole


def test_a_family_whose_cover_is_not_certified_is_undecided() -> None:
    r"""The section is refused because coverage is *undecided*, not because the family fails to cover.

    $(x^3-1)^2 + 1 \ge 1$, so the chart is the whole plane; the sixth degree is outside
    what the certificates decide, and the refusal is the undecided one.
    """
    plane, whole = _the_plane_with_a_positive_sixth_degree_cut()
    sections = plane.tangent_bundle().sections()

    with pytest.raises(CoverageUndecided):
        sections.section(
            {"K1": (whole.function_ring().one(), whole.function_ring().zero())}
        )


def test_a_family_that_is_decided_to_miss_a_point_is_refused_as_such() -> None:
    r"""The chart cut by $x^2+y^2$ misses the origin, and the squares' sum $x^2+y^2$ decides that: the refusal is the decided one.

    Here the certificate decides the other way, and the refusal is the one that says the
    family does not cover -- not the undecided one.
    """
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    punctured = plane.chart_on_open_subset("K2", "x y", "U", (x**2 + y**2,))
    sections = plane.tangent_bundle().sections()

    with pytest.raises(AssertionError):
        sections.section({"K2": (punctured.function_ring().one(), punctured.function_ring().zero())})
