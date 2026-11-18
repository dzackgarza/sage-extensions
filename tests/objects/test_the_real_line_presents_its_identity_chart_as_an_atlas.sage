r"""The real line presents its identity chart as a topological and a smooth atlas.

A chart of a manifold is a homeomorphism of an open subset of it onto an open
subset of ``R^n`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).
The real line's charts are the identity ``x: R -> R`` on the whole space, so its
atlas is one chart: the domain is the field itself, its inclusion into the line
is the identity, and the chart carries a point to its own coordinate.  One chart
has no pair of charts, so the atlas has no overlap and no transition.
"""

from sage_extensions.all import *


def test_the_real_line_presents_one_topological_chart_on_the_whole_space() -> None:
    r"""The topological atlas of ``RR`` is the identity chart on the field itself."""
    atlas = RR.standard_topological_atlas()

    assert atlas in TopologicalAtlases()
    assert atlas.underlying_topological_space() is RR
    assert atlas.chart_domains()[RR] is RR
    assert atlas.chart_domain_inclusion(RR).domain() is RR
    assert atlas.chart_domain_inclusion(RR).codomain() is RR
    assert atlas.chart(RR)(RR(3)) == RR(3)
    assert atlas.chart(RR)(RR(-3)) == RR(-3)


def test_the_real_line_presents_the_same_chart_as_a_smooth_atlas() -> None:
    r"""The smooth atlas of ``RR`` is that one chart at degree infinity, of ``RR`` as a smooth manifold."""
    atlas = RR.standard_smooth_atlas()

    assert atlas in RealCkAtlases(oo)
    assert atlas.category().degree() is oo
    assert atlas.underlying_topological_manifold() is RR
    assert atlas.chart_domains()[RR] is RR
    assert atlas.chart(RR)(RR(3)) == RR(3)


def test_the_atlas_chart_and_the_manifold_chart_read_a_point_the_same_way() -> None:
    r"""The chart the atlas presents and the chart of ``RR`` read one point to one coordinate: the point itself."""
    chart = RR.identity_chart()

    assert RR.standard_smooth_atlas().chart(RR)(RR(3)) == chart.coordinate(0)(RR(3))
    assert RR.standard_topological_atlas().chart(RR)(RR(3)) == chart.coordinate(0)(RR(3))
