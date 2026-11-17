r"""The expressions of a chart and of an atlas transition are sections on the open sets they are defined on.

A chart ``phi : U -> K^n`` is a homeomorphism of an open subset ``U`` of the
manifold onto an open subset of ``K^n`` (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 1), so each of its coordinates is a section of the
ring of functions the manifold assigns to ``U``, valued in the field ``K`` its
coordinates lie in.  A transition ``phi_t o phi_s^{-1}`` is the coordinate
change of two charts, defined on the overlap ``phi_s(U_s cap U_t)``, and its
forward and inverse coordinate functions are functions of those coordinates.

The real specimen is the unit shear ``(x, y) |-> (x + y, y)``, the transition
of the general integral-affine structure on a selected lattice (Alexeev--Engel,
*Compactifications of moduli spaces of K3 surfaces with a nonsymplectic
involution*, arXiv:2208.10383v2, Definition 6.11, p. 30), which carries
``(3, -1)`` to ``(2, -1)``.  The two charts are then cut out on proper open
subsets: the second is defined where ``x + y`` does not vanish, so the point
``(3, -3)``, which lies on ``x + y = 0``, is outside its domain and the shear's
transition refuses it.

The complex specimens are the exact complex line -- where a coordinate takes a
nonreal value, an element of ``CC`` -- and the projective plane, whose charts
are the standard ones with coordinate change ``x_k/x_j = (x_k/x_i)/(x_j/x_i)``
(Griffiths--Harris, *Principles of Algebraic Geometry*, Ch. 0, Sec. 1).
"""

import pytest

from sage_extensions.all import *


def _shear_of_two_charts(plane):
    r"""The charts ``U`` and ``V`` of the plane and the shear between their coordinates.

    ``U`` has the coordinates ``x, y`` and ``V`` the coordinates ``u, v``; the
    transition carries ``(x, y)`` to ``(u, v) = (x + y, y)``, and its inverse
    carries ``(u, v)`` to ``(u - v, v)``.
    """
    source = plane.chart("U", "x y")
    target = plane.chart("V", "u v")
    shear = (source.coordinate(0) + source.coordinate(1), source.coordinate(1))
    inverse = (target.coordinate(0) - target.coordinate(1), target.coordinate(1))
    return source, target, shear, inverse


def test_the_transition_of_two_charts_of_the_plane_evaluates_forward_and_inverse_on_points() -> None:
    r"""The shear's transition carries the source coordinates ``(3, -1)`` to ``(2, -1)`` and back, on a chart whose coordinates are sections of its function ring."""
    plane = SmoothManifolds()(2, "R^2")
    source, target, shear, inverse = _shear_of_two_charts(plane)
    transition = plane.transition_map("U", "V", shear, inverse)

    assert source.coordinate(0).parent() is source.function_ring()
    assert source.coordinate(0)(plane((3, -1), "U")) == RR(3)
    assert transition.source() is source
    assert transition.target() is target
    assert tuple(transition(3, -1)) == (RR(2), RR(-1))
    assert tuple(transition.inverse()(2, -1)) == (RR(3), RR(-1))
    assert tuple(transition.inverse()(*tuple(transition(3, -1)))) == (RR(3), RR(-1))


def test_a_chart_of_a_proper_open_subset_is_a_section_of_the_functions_on_that_subset() -> None:
    r"""The chart ``U`` of the plane cut out where ``x`` does not vanish is defined on an open submanifold of the plane, and its coordinates are sections there, not on the plane."""
    plane = SmoothManifolds()(2, "R^2")
    base = plane.chart("base", "x y")
    chart = plane.chart_on_open_subset("U", "x y", "base", (base.coordinate(0),))
    functions = chart.function_ring()
    point = plane((3, -1), "base")

    assert chart.domain() is not plane
    assert chart.domain().containing_manifold() is plane
    assert chart.domain().dimension() == plane.dimension()
    assert functions.domain() is chart.domain()
    assert chart.coordinate(0).parent() is functions
    assert chart.coordinate(1).parent() is functions
    assert chart.coordinate(0)(point) == RR(3)
    assert chart.coordinate(1)(point) == RR(-1)
    assert tuple(chart(point)) == (RR(3), RR(-1))


def test_the_overlap_of_two_charts_on_proper_open_subsets_is_where_the_transition_is_defined() -> None:
    r"""The shear's transition of the charts ``{x != 0}`` and ``{x + y != 0}`` is defined where both hold: it carries ``(3, -1)`` to ``(2, -1)``, and refuses ``(3, -3)``, which lies outside the second chart."""
    plane = SmoothManifolds()(2, "R^2")
    base = plane.chart("base", "x y")
    source = plane.chart_on_open_subset("U", "x y", "base", (base.coordinate(0),))
    target = plane.chart_on_open_subset(
        "V", "u v", "base", (base.coordinate(0) + base.coordinate(1),)
    )
    transition = plane.transition_map(
        "U",
        "V",
        (source.coordinate(0) + source.coordinate(1), source.coordinate(1)),
        (target.coordinate(0) - target.coordinate(1), target.coordinate(1)),
        source_overlap=(source.coordinate(0), source.coordinate(0) + source.coordinate(1)),
        target_overlap=(target.coordinate(0), target.coordinate(0) - target.coordinate(1)),
    )

    assert source.domain() is not plane
    assert target.domain() is not plane
    assert source.domain() is not target.domain()
    assert tuple(
        section.parent() is source.function_ring()
        for section in transition.source_overlap()
    ) == (True, True)
    assert tuple(
        section.parent() is target.function_ring()
        for section in transition.target_overlap()
    ) == (True, True)
    assert tuple(transition(3, -1)) == (RR(2), RR(-1))
    assert tuple(transition.inverse()(2, -1)) == (RR(3), RR(-1))
    with pytest.raises(AssertionError):
        transition(3, -3)


def test_a_coordinate_of_a_complex_chart_is_a_section_valued_in_the_complex_field() -> None:
    r"""The coordinate of the complex line takes the nonreal value ``2i``, an element of the complex field ``CC``, at the point of the line with coordinate ``2i``."""
    line = ComplexManifolds().affine_space(1, name="C")
    chart = line.atlas()["standard"]
    functions = chart.function_ring()
    point = line((2 * I,), chart_label="standard")

    assert functions.domain() is chart.domain()
    assert chart.coordinate(0).parent() is functions
    assert chart.coordinate(0)(point) == 2 * I
    assert chart.coordinate(0)(point).parent() is CC
    assert tuple(chart(point)) == (2 * I,)


def test_the_charts_of_the_complex_projective_plane_change_coordinates_by_ratios() -> None:
    r"""On ``CP^2`` the chart ``U_0`` is defined on a proper open subset, and the transition to ``U_2`` carries the coordinates ``(2i, 3i)`` to ``(1/(3i), 2i/(3i))`` and back."""
    plane = ComplexManifolds().projective_space(2, name="CP^2")
    transition = plane.transition("U0", "U2")
    source = transition.source()
    target = transition.target()

    assert source.domain() is not plane
    assert target.domain() is not plane
    assert source.domain().containing_manifold() is plane
    assert source.function_ring().domain() is source.domain()
    assert all(
        coordinate.parent() is source.function_ring()
        for coordinate in tuple(source.coordinates())
    )
    assert tuple(transition(2 * I, 3 * I)) == (CC(1) / (3 * I), (2 * I) / (3 * I))
    assert tuple(transition.inverse()(2 * I, 3 * I)) == (CC(3) / 2, -(CC(1) / 2) * I)
