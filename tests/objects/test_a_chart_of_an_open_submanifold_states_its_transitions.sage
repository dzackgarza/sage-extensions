r"""A chart of an open submanifold states its transitions to the other charts it carries.

An open submanifold carries the ambient charts read on it (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Example 1.4), so two of its charts are two ambient charts read on
two subsets of it, and the coordinate change between them is the ambient coordinate
change read there: on the overlaps where both charts are defined, the same expression
(Lee, Ch. 1).  A manifold whose charts are not related by transitions cannot decide the
agreement of anything stated on them, so a section, a form or a frame on such a
submanifold is unchecked.

The specimen is the stereographic chart domain of $S^2$ -- $S^2$ minus the north pole,
with the north chart and the south chart read on it.  A point of the north chart with
coordinates $(2, 3)$ is the point of the south chart with coordinates
$(2/13, 3/13)$, since $y = x/\lvert x\rvert^2$; the pole $x = 0$ is not in the south
chart's domain and the transition refuses it.
"""

import pytest

from sage_extensions.all import *


def _the_chart_domain():
    r"""$S^2$ minus the north pole, as an open submanifold with the north and south charts on it."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    domain = north.domain()
    return sphere, sphere.open_submanifold(sphere.open_submanifold_inclusion(domain))


def test_the_submanifold_states_the_transition_between_the_charts_it_carries() -> None:
    r"""$y = x/\lvert x\rvert^2$ reads $(2, 3)$ as $(2/13, 3/13)$ on the submanifold, in both directions.

    The two charts of the open submanifold are the ambient north and south charts read
    on it, so their coordinate change is the ambient one: the same expression, on the
    same overlap, and the inverse transition is its inverse.
    """
    _sphere, submanifold = _the_chart_domain()
    transition = submanifold.transition("U_N", "U_S")

    coordinates = tuple(transition(RR(2), RR(3)))

    assert coordinates[0] == RR(2) / RR(13)
    assert coordinates[1] == RR(3) / RR(13)
    back = tuple(transition.inverse()(*coordinates))
    assert back[0] == RR(2)
    assert back[1] == RR(3)


def test_the_transition_refuses_a_point_outside_the_overlap_it_states() -> None:
    r"""The south pole is in the north chart and not in the south chart, so the change from $x = 0$ is refused."""
    _sphere, submanifold = _the_chart_domain()
    transition = submanifold.transition("U_N", "U_S")

    with pytest.raises(AssertionError):
        tuple(transition(RR.zero(), RR.zero()))
