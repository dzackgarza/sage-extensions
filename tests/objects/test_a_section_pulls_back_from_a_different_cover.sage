r"""Pullback sections use the actual map and section domains.

Lee, Introduction to Smooth Manifolds, second edition, Proposition 2.5 and
Corollary 2.8 (p. 35), use actual coordinate representation domains.  His
Lemma 10.5 (pp. 252--253) and Proposition 10.22 (p. 260) give the section
transition law.  Tu, Differential Geometry, Theorem 20.6 and Proposition
20.7 (pp. 178--179), give the pullback bundle and its pulled-back transitions.
"""

from sage_extensions.all import *

import pytest


def test_a_constant_map_reads_a_rank_two_section_on_another_cover() -> None:
    r"""For V=(u,v)=(x,y+x^2), the V-field (B,0) is (B,-2xB) in U.

    Both U and V cover the plane.  The constant map from the line to
    U-coordinates (1,0) therefore pulls this field back to (1,-2), although
    the field is stated only on V and the source has dimension one.  Here B
    is a smooth nonanalytic bump equal to one on the radius-two ball and
    zero outside the radius-three ball in V (Lee, Lemmas 2.20--2.22).
    """
    plane = SmoothManifolds()(2, "plane for a constant pullback")
    first = plane.chart("U", "x y")
    second = plane.chart("V", "u v")
    x, y = first.coordinate(0), first.coordinate(1)
    u, v = second.coordinate(0), second.coordinate(1)
    plane.transition_map("U", "V", (x, y + x*x), (u, v - u*u))
    line = SmoothManifolds()(1, "line for a constant pullback")
    source = line.chart("W", "t")
    ring = source.function_ring()
    mapping = line.Mor(plane)({("W", "U"): (ring.one(), ring.zero())})
    vector = plane.tangent_bundle().sections().section(
        {"V": (plane.chart_bump("V", 2, 3), second.function_ring().zero())}
    )
    bundle = plane.tangent_bundle().pullback_along(mapping)

    pulled = bundle.sections().pullback_of(vector)

    point = line((3,), "W")
    assert pulled.parent() is bundle.sections()
    assert bundle.rank() == 2
    assert tuple(entry(point) for entry in pulled.components()["W"]) == (RR(1), RR(-2))
    descriptions = pulled.components()
    descriptions["W"] = (ring.zero(), ring.zero())
    assert tuple(pulled.components_at(point, "U")) == (RR(1), RR(-2))
    assert tuple(entry(point) for entry in pulled.components()["W"]) == (RR(1), RR(-2))


def test_local_map_domains_cover_the_pole_and_transport_from_another_source_chart() -> None:
    r"""The smooth map with south coordinates (t,0) has north coordinates (1/t,0).

    The latter description is valid only for t != 0.  The Euler field on
    the sphere is (x1,x2) in the north frame and (-y1,-y2) in the south frame.
    Its pullback, in the south frame, is therefore (-t,0), including t=0.
    The field is stated on another covering pair of charts.  The input point
    at t=0 is given in a third source chart r=t+1.
    """
    sphere = SmoothManifolds().sphere(2)
    north, south = sphere.atlas()["U_N"], sphere.atlas()["U_S"]
    north_copy = sphere.chart_on_open_subset("V_N", "a b", "U_N", (north.function_ring().one(),), same_coordinates=True)
    south_copy = sphere.chart_on_open_subset("V_S", "c d", "U_S", (south.function_ring().one(),), same_coordinates=True)
    vector = sphere.tangent_bundle().sections().section({
        "V_N": (north_copy.coordinate(0), north_copy.coordinate(1)),
        "V_S": (-south_copy.coordinate(0), -south_copy.coordinate(1)),
    })
    line = SmoothManifolds()(1, "line through a stereographic pole")
    source = line.chart("W", "t")
    other = line.chart("Q", "r")
    t, r = source.coordinate(0), other.coordinate(0)
    ring = source.function_ring()
    line.transition_map("W", "Q", (t + ring.one(),), (r - other.function_ring().one(),))
    mapping = line.Mor(sphere)({
        ("W", "U_N"): (source.section_ratio(ring.one(), t), ring.zero()),
        ("W", "U_S"): (t, ring.zero()),
    }, domains={("W", "U_N"): (t,)})
    original_labels = tuple(line.chart_labels())

    pulled = sphere.tangent_bundle().pullback_along(mapping).sections().pullback_of(vector)

    pole = line((1,), "Q")
    assert mapping(pole) == sphere((0, 0), "U_S")
    assert tuple(pulled.components_at(pole, "U_S")) == (RR(0), RR(0))
    assert tuple(pulled.components_at(line((2,), "W"), "U_S")) == (RR(-2), RR(0))
    assert tuple(line.chart_labels()) == original_labels
    north_indices = tuple(index for index in pulled.components()
        if pulled.component_frame(index).label() == "U_N")
    assert north_indices
    with pytest.raises((ValueError, AssertionError)):
        pulled.components()[north_indices[0]][0](line((0,), "W"))
    local_map = mapping.chart_map_chart("W", "U_N")
    assert local_map.domain() is not line
    assert mapping.chart_map("W", "U_N")[0].parent() is local_map.function_ring()
    with pytest.raises((ValueError, AssertionError)):
        mapping.chart_map("W", "U_N")[0](line((0,), "W"))


def test_two_transition_paths_supply_the_actual_cover() -> None:
    r"""The paths through x != 0 and x != 1 together cover the whole plane.

    At x=0 only the second path reads a V-component in the U-frame.  For
    V=(x,y+x^2) the vector (1,0) in V has U-components (1,-2x), hence (1,0)
    at the image of this constant map.  The domains cover because x and x-1
    have no common zero.
    """
    plane = SmoothManifolds()(2, "plane with two transition domains")
    first = plane.chart("U", "x y")
    last = plane.chart("V", "u v")
    x, y = first.coordinate(0), first.coordinate(1)
    u, v = last.coordinate(0), last.coordinate(1)
    away_zero = plane.chart_on_open_subset("B", "b c", "U", (x,), same_coordinates=True)
    away_one = plane.chart_on_open_subset("C", "h k", "U", (x - first.function_ring().one(),), same_coordinates=True)
    b, c = away_zero.coordinate(0), away_zero.coordinate(1)
    h, k = away_one.coordinate(0), away_one.coordinate(1)
    plane.transition_map("B", "V", (b, c+b*b), (u, v-u*u), target_overlap=(u,))
    plane.transition_map("C", "V", (h, k+h*h), (u, v-u*u), target_overlap=(u-last.function_ring().one(),))
    line = SmoothManifolds()(1, "line for a two-path pullback")
    source = line.chart("W", "t")
    zero = source.function_ring().zero()
    mapping = line.Mor(plane)({("W", "U"): (zero, zero)})
    vector = plane.tangent_bundle().sections().section({"V": (last.function_ring().one(), last.function_ring().zero())})
    atlas_before = (tuple(plane.chart_labels()), tuple(plane.transitions().index_set()))

    pulled = plane.tangent_bundle().pullback_along(mapping).sections().pullback_of(vector)

    assert tuple(pulled.components_at(line((2,), "W"), "U")) == (RR(1), RR(0))
    assert (tuple(plane.chart_labels()), tuple(plane.transitions().index_set())) == atlas_before


def test_two_cuts_of_one_stereographic_chart_do_not_cover_the_sphere() -> None:
    r"""Their cutting polynomials have no common zero, but both miss the other pole.

    In opposite coordinates the cuts have denominators |x|^2.  Removing that
    denominator incorrectly adds the pole to their union.
    """
    sphere = SmoothManifolds().sphere(2)
    south = sphere.atlas()["U_S"]
    x, y = south.coordinate(0), south.coordinate(1)
    one = south.function_ring().one()
    first = sphere.chart_on_open_subset("C1", "y1 y2", "U_S", (x*x+y*y-one,), same_coordinates=True)
    second = sphere.chart_on_open_subset("C2", "y1 y2", "U_S", (x*x+y*y-one-one,), same_coordinates=True)

    with pytest.raises((AssertionError, CoverageUndecided)):
        sphere.tangent_bundle().sections().section({
            "C1": (first.function_ring().zero(), first.function_ring().zero()),
            "C2": (second.function_ring().zero(), second.function_ring().zero()),
        })


def test_smooth_local_formulas_agree_only_on_their_actual_overlap() -> None:
    r"""Two formulas on one chart pair glue smoothly without agreeing globally.

    Let H be one on |t|<=1 and zero on |t|>=2; let K have radii 2 and 3.
    The domains H!=0 and 1-H!=0 cover R, since H+(1-H)=1.  The formulas
    0 and 1-K agree on their overlap 1<|t|<2, but disagree at |t|>=3.
    Both the map and the section use genuine smooth nonanalytic bump functions
    (Lee, Lemmas 2.20--2.22).  The V-component bump equals one at both images.
    """
    line = SmoothManifolds()(1, "line with local smooth formulas")
    source = line.chart("W", "t")
    t, ring = source.coordinate(0), source.function_ring()
    h = line.chart_bump("W", 1, 2)
    k = line.chart_bump("W", 2, 3)
    plane = SmoothManifolds()(2, "plane with a smooth bump section")
    first, second = plane.chart("U", "x y"), plane.chart("V", "u v")
    x, y = first.coordinate(0), first.coordinate(1)
    u, v = second.coordinate(0), second.coordinate(1)
    plane.transition_map("U", "V", (x, y+x*x), (u, v-u*u))
    mapping = line.Mor(plane)({
        ("W", "U", "inner"): (ring.zero(), ring.zero()),
        ("W", "U", "outer"): (ring.one()-k, ring.zero()),
    }, domains={
        ("W", "U", "inner"): (h,),
        ("W", "U", "outer"): (ring.one()-h,),
    })
    vector = plane.tangent_bundle().sections().section({
        "V": (plane.chart_bump("V", 2, 3), second.function_ring().zero()),
    })
    module = plane.tangent_bundle().pullback_along(mapping).sections()
    pulled = module.pullback_of(vector)
    inside, outside = line((0,), "W"), line((4,), "W")

    assert mapping(inside) == plane((0, 0), "U")
    assert mapping(outside) == plane((1, 0), "U")
    assert tuple(pulled.components_at(inside, "U")) == (RR(1), RR(0))
    assert tuple(pulled.components_at(outside, "U")) == (RR(1), RR(-2))
    assert tuple((pulled+pulled).components_at(outside, "U")) == (RR(2), RR(-4))
    assert tuple((-pulled).components_at(outside, "U")) == (RR(-1), RR(2))
    assert tuple(module.zero().components_at(outside, "U")) == (RR(0), RR(0))
    assert tuple(((ring.one()+h)*pulled).components_at(inside, "U")) == (RR(2), RR(0))
    with pytest.raises((ValueError, AssertionError)):
        mapping.chart_map("W", "U", "inner")[0](outside)

    doubling = line.Mor(line)({("W", "W"): (t+t,)})
    composite = mapping * doubling
    at_two = line((2,), "W")
    assert composite(at_two) == plane((1, 0), "U")
    nested = module.vector_bundle().pullback_along(doubling).sections().pullback_of(pulled)
    assert tuple(nested.components_at(at_two, "U")) == (RR(1), RR(-2))

    different = plane.tangent_bundle().sections().section({
        "V": (second.function_ring().one(), u),
    })
    other = module.pullback_of(different)
    assert tuple(other.components_at(outside, "U")) == (RR(1), RR(-1))
    with pytest.raises(CoverageUndecided):
        pulled == other


def test_equal_nested_pullbacks_in_different_frames_do_not_form_a_basis() -> None:
    r"""Swapping target coordinates changes component tuples, not the vector.

    Two copies of d/dx cannot form a rank-two frame, although one has tuple
    (1,0) in U and the other (0,1) in V=(y,x).  A determinant must compare
    columns in one fibre frame (Lee, Lemma 10.5 and Proposition 10.22).
    """
    plane = SmoothManifolds()(2, "plane for common fibre frames")
    u, v = plane.chart("U", "x y"), plane.chart("V", "a b")
    plane.transition_map("U", "V", (u.coordinate(1), u.coordinate(0)),
        (v.coordinate(1), v.coordinate(0)),
        source_overlap=(u.function_ring().one(),), target_overlap=(v.function_ring().one(),))
    middle = SmoothManifolds()(1, "middle line for common fibre frames")
    a = middle.chart("A", "z")
    zero = a.function_ring().zero()
    g = middle.Mor(plane)({("A", "U"): (zero, zero), ("A", "V"): (zero, zero)})
    inner = plane.tangent_bundle().pullback_along(g)
    first = inner.sections().pullback_of(plane.tangent_bundle().sections().section({
        "U": (u.function_ring().one(), u.function_ring().zero()),
    }))
    second = inner.sections().pullback_of(plane.tangent_bundle().sections().section({
        "V": (v.function_ring().zero(), v.function_ring().one()),
    }))
    line = SmoothManifolds()(1, "outer line for common fibre frames")
    w = line.chart("W", "t")
    f = line.Mor(middle)({("W", "A"): (w.function_ring().zero(),)})
    module = inner.pullback_along(f).sections()
    first, second = module.pullback_of(first), module.pullback_of(second)
    point = line((0,), "W")
    assert tuple(first.components_at(point, "U")) == (RR(1), RR(0))
    assert tuple(second.components_at(point, "U")) == (RR(1), RR(0))

    with pytest.raises((AssertionError, CoverageUndecided)):
        module.trivialized_by((first, second))
