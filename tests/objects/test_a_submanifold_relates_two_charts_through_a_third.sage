r"""Two charts of an open submanifold are related through a third one when the ambient atlas does not relate them.

An atlas states the coordinate changes between the charts it has them for, and two charts
of one atlas are related by composing changes through a third wherever the intermediate
chart meets both: $\varphi_t \circ \varphi_s^{-1} = (\varphi_t \circ \varphi_c^{-1}) \circ
(\varphi_c \circ \varphi_s^{-1})$ (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).
An open submanifold carries the ambient charts read on it, and a chart cut on a subset of
one of them meets a chart the ambient atlas does not relate to it; the composition is then
the coordinate change the submanifold has, and without it a section stated on both charts
cannot be checked at all.

The specimen is $S^2$ minus the north pole with a chart cut on the north chart: the south
chart and the cut chart meet through the north chart, and the change from the south chart
to the cut chart is the stereographic change followed by the identity.
"""

import pytest

from sage_extensions.all import *


def _the_submanifold_with_a_cut_chart(label):
    r"""$S^2$ minus the north pole, with the north chart, the south chart, and a chart cut on the north one."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    norm_squared = north.coordinate(0) ** 2 + north.coordinate(1) ** 2
    sphere.chart_on_open_subset(label, "x1 x2", "U_N", (norm_squared,), same_coordinates=True)
    domain = north.domain()
    return sphere.open_submanifold(sphere.open_submanifold_inclusion(domain))


def test_the_submanifold_relates_the_cut_chart_to_the_south_chart() -> None:
    r"""The change from the south chart to the cut chart sends $(2/13, 3/13)$ to $(2, 3)$: the stereographic change, then the identity.

    The ambient atlas states no change between the south chart and the cut chart, but it
    states both legs through the north chart, and the composition is the change the
    submanifold has.
    """
    submanifold = _the_submanifold_with_a_cut_chart("CUT1")

    transition = submanifold.transition("U_S", "CUT1")
    coordinates = tuple(transition(RR(2) / RR(13), RR(3) / RR(13)))

    assert coordinates[0] == RR(2)
    assert coordinates[1] == RR(3)
    back = tuple(transition.inverse()(RR(2), RR(3)))
    assert back[0] == RR(2) / RR(13)
    assert back[1] == RR(3) / RR(13)


def test_the_composed_change_is_the_composition_of_its_two_legs() -> None:
    r"""$\varphi_{CUT} \circ \varphi_S^{-1} = (\varphi_{CUT} \circ \varphi_N^{-1}) \circ (\varphi_N \circ \varphi_S^{-1})$ on a point.

    The composition is checked against the two changes the ambient atlas states, which is
    what makes it the composition rather than a second guess at it.
    """
    submanifold = _the_submanifold_with_a_cut_chart("CUT2")
    at_south = (RR(1) / RR(2), RR(-1) / RR(3))

    through_north = tuple(
        submanifold.transition("U_N", "CUT2")(
            *tuple(submanifold.transition("U_S", "U_N")(*at_south))
        )
    )
    direct = tuple(submanifold.transition("U_S", "CUT2")(*at_south))

    assert direct[0] == through_north[0]
    assert direct[1] == through_north[1]


def test_the_composed_change_is_stated_where_both_legs_are() -> None:
    r"""The change from the south chart to the cut chart is not stated at the pole, which the cut chart does not contain.

    The overlap of the composition is the overlap of its source leg read in the source
    chart: the south chart's coordinates at the pole are outside the stereographic overlap,
    and the change is refused there rather than composed into a formula that is not
    defined.  The refusal arrives from the realization that holds the chart -- the
    coordinate is not on the chart, which the engine states -- and the owned overlap is
    what the transition carries for the points the chart admits.
    """
    submanifold = _the_submanifold_with_a_cut_chart("CUT3")
    transition = submanifold.transition("U_S", "CUT3")

    with pytest.raises((AssertionError, ValueError)):
        tuple(transition(RR.zero(), RR.zero()))


def test_restriction_retains_stated_transition_edges_without_redundant_composites() -> None:
    r"""Restriction preserves the given graph; composing a path adds no new stated edge."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    norm_squared = sum(x*x for x in north.coordinates())
    for label in ("SPARSE_A", "SPARSE_B", "SPARSE_C"):
        sphere.chart_on_open_subset(label, "x1 x2", "U_N", (norm_squared,), same_coordinates=True)
    domain = north.domain()
    restricted = sphere.open_submanifold(sphere.open_submanifold_inclusion(domain))
    edges = tuple(restricted.transitions().keys())
    assert set(edges) == set(sphere.transitions().keys())
    change = restricted.transition("U_S", "SPARSE_C")
    assert tuple(change(RR(2)/RR(13), RR(3)/RR(13))) == (RR(2), RR(3))
    assert tuple(change.inverse()(RR(2), RR(3))) == (RR(2)/RR(13), RR(3)/RR(13))
    assert tuple(restricted.transitions().keys()) == edges
