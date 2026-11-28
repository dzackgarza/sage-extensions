r"""A cover whose charts meet without containing one another is decided, not refused.

A family of open subsets covers a manifold when no point of the manifold lies outside all
of them, and for charts cut by nonvanishing conditions $\{g_i \ne 0\}$ that is the
statement $\bigcap_i \{g_i = 0\} = \varnothing$ (Lee, *Introduction to Smooth Manifolds*,
2nd ed., Ch. 1, for the chart domains).  One certificate is exact and needs no real
algebraic geometry: when $\sum_i g_i$ takes no zero, no point has every $g_i$ zero, so the
family covers.  The plane is the smallest manifold where charts meet without one containing
the other: the plane minus the origin and the plane minus $(1,1)$ cover it, and neither
contains the plane.

A section stated on such a cover is fixed by its components there, so the certificate is
what decides whether such a section can be stated at all.
"""

from sage_extensions.all import *


def _the_plane_with_two_punctures():
    r"""The plane, its chart, and the charts on the complements of the origin and of $(1,1)$."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    origin = plane.chart_on_open_subset("P0", "x y", "U", (x**2 + y**2,), same_coordinates=True)
    other = plane.chart_on_open_subset(
        "P1", "x y", "U", ((x + (-1)) ** 2 + (y + (-1)) ** 2,), same_coordinates=True
    )
    return plane, chart, x, y, origin, other


def test_two_punctured_planes_cover_the_plane_and_admit_a_section() -> None:
    r"""The complements of two distinct points cover the plane: every point misses at least one of them.

    Neither chart is contained in the other, and neither is the whole plane, so no chart
    of the atlas is contained in a single one of them; the certificate is that
    $x^2 + y^2 + (x-1)^2 + (y-1)^2$ is positive definite and so takes no zero.
    """
    plane, _chart, _x, _y, origin, other = _the_plane_with_two_punctures()
    sections = plane.tangent_bundle().sections()
    first = sections.section(
        {"P0": (origin.function_ring().one(), origin.function_ring().zero())}
        | {"P1": (other.function_ring().one(), other.function_ring().zero())}
    )

    assert first in sections
    at_origin = plane((0, 0))
    assert first.components()["P1"][0](at_origin) == RR(1)
    assert first.components()["P1"][1](at_origin) == RR(0)


def test_the_cover_is_not_accepted_without_the_certificate() -> None:
    r"""One punctured plane alone does not cover: the punctured point lies outside it, and the sum $x^2 + y^2$ takes zero there.

    The refusal is the decision, not a want of one: the point the chart cuts out is a
    common zero of the conditions, and the section is not stated.
    """
    import pytest

    plane, _chart, _x, _y, origin, _other = _the_plane_with_two_punctures()
    sections = plane.tangent_bundle().sections()

    with pytest.raises(AssertionError):
        sections.section(
            {"P0": (origin.function_ring().one(), origin.function_ring().zero())}
        )
