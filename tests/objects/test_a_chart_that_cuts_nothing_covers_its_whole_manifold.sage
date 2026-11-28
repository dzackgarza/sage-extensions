r"""A chart cut by a condition that vanishes nowhere is the chart it was cut from, whatever else is registered.

A chart of a manifold is defined on an open subset, and a chart cut out by
$\{g \ne 0\}$ is read on the points where $g$ does not vanish (Lee, *Introduction to
Smooth Manifolds*, 2nd ed., Ch. 1).  When $g$ vanishes nowhere, that subset is the chart
it was cut from: the cut chart is the same chart, and a family containing it covers what
that chart covers.  Whether some other chart has since been registered on the manifold is
no part of the question -- a family that covers must not stop covering because an
unrelated chart appeared.

The specimen is the plane: the chart cut by $x^2 + 1$ is the whole plane, and registering
the chart cut by $y$ afterwards does not change that.
"""

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, and the two coordinates."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    return plane, chart, chart.coordinate(0), chart.coordinate(1)


def test_a_chart_cut_by_a_nowhere_vanishing_condition_covers_the_manifold() -> None:
    r"""$x^2 + 1 \ne 0$ for every real $x$, so the cut chart is the plane, and a section stated on it is admitted."""
    plane, _chart, x, _y = _the_plane()
    never_zero = plane.chart_on_open_subset("W1", "x y", "U", (x**2 + 1,), same_coordinates=True)

    section = plane.tangent_bundle().sections().section(
        {"W1": (never_zero.function_ring().one(), never_zero.function_ring().zero())}
    )

    assert section.parent() is plane.tangent_bundle().sections()
    assert section.components()["W1"][0](plane((3, 4))) == RR(1)


def test_registering_another_chart_does_not_take_the_cover_away() -> None:
    r"""The same section is still admitted after the chart cut by $y$ is registered on the plane.

    That second chart leaves out the line $y = 0$; it is a chart of the same manifold, and
    it is covered by the first -- which is the whole plane -- so the family still covers.
    """
    plane, _chart, x, y = _the_plane()
    never_zero = plane.chart_on_open_subset("W2", "x y", "U", (x**2 + 1,), same_coordinates=True)
    plane.chart_on_open_subset("W3", "x y", "U", (y,), same_coordinates=True)

    section = plane.tangent_bundle().sections().section(
        {"W2": (never_zero.function_ring().one(), never_zero.function_ring().zero())}
    )

    assert section.components()["W2"][0](plane((3, 0))) == RR(1)
