r"""A chart on a proper open subset of a smooth manifold presents that open submanifold's inclusion.

A chart ``phi : U -> RR^n`` is a homeomorphism of an open subset ``U`` of the
manifold onto an open subset of ``RR^n`` (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 1), and ``U`` with the restricted atlas is a smooth
manifold of the same dimension (Lee, Example 1.4).  Its inclusion
``iota : U -> M`` is therefore a smooth map, and the chart presents it: read in
the chart of ``U`` and in the chart of ``M`` that ``U`` is the domain of, the
coordinates of a point of ``U`` and of its image are the same.  The inclusion
is an arrow of the smooth manifolds' own Mor, its value at a point of ``U`` is
that same intrinsic point of ``M``, it admits no point outside ``U``, and a map
of the open submanifold composes with it by substituting its coordinate
sections.

The specimen is the real plane ``R^2`` cut out where its first coordinate does
not vanish: the proper open subset ``{x != 0}``, with the chart ``x, y`` it is
the domain of.  The point ``(3, -1)`` lies in it, and ``(0, 1)`` does not.
"""

import pytest

from sage_extensions.all import *


def _the_plane_on_its_nonvanishing_open_subset():
    r"""The plane, its chart ``x, y`` on ``{x != 0}``, and that open submanifold."""
    plane = SmoothManifolds()(2, "R^2")
    base = plane.chart("base", "x y")
    chart = plane.chart_on_open_subset("U", "x y", "base", (base.coordinate(0),))
    return plane, chart, chart.domain()


def test_the_proper_chart_domain_includes_smoothly_into_its_plane() -> None:
    r"""The inclusion of ``{x != 0}`` into ``R^2`` is an arrow of the smooth manifolds' Mor, and it carries ``(3, -1)`` to the same point of the plane.

    The point is given in the plane's chart ``base`` and its image in the chart
    ``U`` the open subset is the domain of; they are the same point of ``R^2``,
    and the inclusion's coordinate sections on the chart ``U`` are sections of
    the functions on that open submanifold, not on the plane.
    """
    plane, chart, domain = _the_plane_on_its_nonvanishing_open_subset()
    point = plane((3, -1), "base")
    inner = domain(point)
    inclusion = plane.open_submanifold_inclusion(domain)

    assert inclusion in domain.Mor(plane)
    assert domain is not plane
    assert chart.domain() is domain
    assert inclusion.domain() is domain
    assert inclusion.codomain() is plane
    assert inclusion(inner) == point
    assert tuple(plane.atlas()["U"](inclusion(inner))) == (RR(3), RR(-1))
    coordinates = inclusion.chart_map("U", "U")
    assert tuple(
        section.parent() is domain.atlas()["U"].function_ring() for section in coordinates
    ) == (True, True)
    assert tuple(section(inner) for section in coordinates) == (RR(3), RR(-1))


def test_the_inclusion_admits_no_point_outside_the_proper_chart_domain() -> None:
    r"""The point ``(0, 1)`` of the plane lies on ``x = 0``, outside the open subset, and the inclusion refuses it."""
    plane, _chart, domain = _the_plane_on_its_nonvanishing_open_subset()
    inclusion = plane.open_submanifold_inclusion(domain)

    assert inclusion in domain.Mor(plane)
    with pytest.raises(ValueError):
        inclusion(plane((0, 1), "base"))


def test_a_map_of_the_open_subset_composes_with_the_inclusion_into_the_plane() -> None:
    r"""The map ``(x, y) |-> (x, y^2)`` of ``{x != 0}`` composed with the inclusion carries ``(3, -1)`` to ``(3, 1)``, a different point of the plane.

    The composite is the smooth map whose coordinate sections on the chart are
    the substituted coordinates of the map of the open subset, so its value is
    the coordinate-wise square of the second coordinate at a point of ``R^2``
    and its source is the open submanifold, not the plane.
    """
    plane, chart, domain = _the_plane_on_its_nonvanishing_open_subset()
    point = plane((3, -1), "base")
    inner = domain(point)
    squaring = domain.Mor(domain)(
        {("U", "U"): (chart.coordinate(0), chart.coordinate(1) ** 2)}
    )
    inclusion = plane.open_submanifold_inclusion(domain)
    composite = inclusion * squaring

    assert squaring in domain.Mor(domain)
    assert composite in domain.Mor(plane)
    assert (composite.domain() is domain, composite.codomain() is plane) == (True, True)
    assert composite(inner) == plane((3, 1), "base")
    assert composite(inner) != point
    assert tuple(section(inner) for section in composite.chart_map("U", "U")) == (
        RR(3),
        RR(1),
    )


def test_a_map_of_the_plane_restricts_to_the_proper_chart_domain() -> None:
    r"""The map ``(x, y) |-> (x, 2y)`` of the plane composed with the inclusion is its restriction to ``{x != 0}``, carrying ``(3, -1)`` to ``(3, -2)``.

    The plane's atlas is what states the change of coordinates between the chart
    ``U`` of the open subset and the chart ``base`` of the plane; the composite
    is then the map of the open subset whose coordinate sections on ``U`` are
    ``base``'s coordinates with that change substituted, and its source is the
    open submanifold, not the plane.
    """
    plane, chart, domain = _the_plane_on_its_nonvanishing_open_subset()
    base = plane.atlas()["base"]
    point = plane((3, -1), "base")
    inner = domain(point)
    inclusion = plane.open_submanifold_inclusion(domain)
    doubling = plane.Mor(plane)(
        {("base", "base"): (base.coordinate(0), base.coordinate(1) + base.coordinate(1))}
    )
    change = plane.transition_map(
        "U", "base", chart.coordinates(), base.coordinates(), target_overlap=(base.coordinate(0),)
    )
    restriction = doubling * inclusion

    assert tuple(change.source_overlap()) == ()
    assert restriction in domain.Mor(plane)
    assert (restriction.domain() is domain, restriction.codomain() is plane) == (True, True)
    assert restriction(inner) == plane((3, -2), "base")
    assert tuple(section(inner) for section in restriction.chart_map("U", "base")) == (
        RR(3),
        RR(-2),
    )


def test_a_map_of_the_plane_is_not_restated_on_the_open_subsets_chart_by_assumption() -> None:
    r"""Until the atlas states the change of coordinates, the plane's map is not restricted: an unstated change is not read as the identity.

    The chart ``U`` of ``{x != 0}`` is a chart of the plane, and the plane's own
    chart ``base`` is another; a map written on ``base`` states nothing about the
    coordinates of ``U``, so composing it with the inclusion is refused rather
    than assuming the two charts agree.
    """
    plane, _chart, domain = _the_plane_on_its_nonvanishing_open_subset()
    base = plane.atlas()["base"]
    inclusion = plane.open_submanifold_inclusion(domain)
    doubling = plane.Mor(plane)(
        {("base", "base"): (base.coordinate(0), base.coordinate(1) + base.coordinate(1))}
    )

    assert tuple(plane.transitions().keys()) == ()
    with pytest.raises(AssertionError):
        doubling * inclusion
