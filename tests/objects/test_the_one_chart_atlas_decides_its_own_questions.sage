r"""An atlas answers the questions its retained maps decide, and only those.

A chart of a manifold is a homeomorphism of an open subset of it onto an open
subset of ``R^n`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  The
real line's atlas is one chart on the whole space: its domain covers the line,
and it has no pair of charts, so there is no coordinate change that could fail
to be a homeomorphism or a ``C^k`` diffeomorphism, and the cocycle has no
instance.  Those answers are decided by the maps the atlas retains and not by the
name of the space: an atlas whose one chart is cut out on a proper open
submanifold does not decide that its domains cover the plane, and says so.
"""

from sage_extensions.all import *


def test_the_one_chart_of_the_real_line_covers_it() -> None:
    r"""The chart's domain is the line itself, so the chart domains cover the line."""
    assert RR.standard_topological_atlas().chart_domains_cover() is True
    assert RR.standard_smooth_atlas().chart_domains_cover() is True


def test_an_atlas_of_one_chart_has_no_transition_to_check() -> None:
    r"""One chart has no pair, so every statement about the coordinate changes holds of it vacuously."""
    topological = RR.standard_topological_atlas()
    smooth = RR.standard_smooth_atlas()

    assert topological.transitions_are_homeomorphisms() is True
    assert topological.transition_cocycle_holds() is True
    assert smooth.transitions_are_ck() is True
    assert smooth.transition_cocycle_holds() is True


def test_a_chart_on_a_proper_open_submanifold_does_not_decide_that_it_covers() -> None:
    r"""The chart ``{x != 0}`` of the plane is not the plane, so coverage is the proposition, not an answer."""
    plane = SmoothManifolds()(2, "R^2")
    base = plane.chart("base", "x y")
    chart = plane.chart_on_open_subset("U", "x y", "base", (base.coordinate(0),))
    domain = chart.domain()
    model = RR.free_module(2)
    atlas = RealCkAtlases(oo).on(
        plane,
        {domain: domain},
        {domain: Sets().Mor(domain, plane)(lambda point: plane(tuple(point.coordinates())))},
        {domain: Sets().Mor(domain, model)(lambda point: model(tuple(point.coordinates())))},
        {},
        {},
    )

    assert domain is not plane
    assert atlas.chart_domains_cover() in Propositions
    assert atlas.transitions_are_ck() is True
