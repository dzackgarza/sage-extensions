r"""A section is fixed by its components on a cover, not on every chart a manifold happens to carry.

The charts of an atlas that a construction registered on a manifold accumulate: a chart cut
on a subset, or a chart of another chart's domain, is a chart of the same manifold, and two
charts of one atlas are related by their coordinate change only where the atlas states one
(Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 1).  A section, a form or a frame is
fixed by its components on a cover of the manifold -- the charts it is stated on -- and the
agreement of those components is a question about the pairs among them, not about every chart
the atlas carries.

The specimen is the pair of errors: a chart is cut on the sphere, and then a chart domain is
read with the two charts it presents.  The frame of the north chart is a basis of every fibre
of the chart domain's tangent bundle, and an unrelated chart registered on the sphere before
it must not change that.
"""

import pytest

from sage_extensions.all import *


def _the_sphere_with_an_extra_chart(label):
    r"""$S^2$ with a chart cut on it under ``label``, and the chart domain of ``U_N`` read afterwards."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    norm_squared = north.coordinate(0) ** 2 + north.coordinate(1) ** 2
    sphere.chart_on_open_subset(label, "x1 x2", "U_N", (norm_squared,))
    domain = north.domain()
    return sphere, sphere.open_submanifold(sphere.open_submanifold_inclusion(domain))


def test_a_chart_registered_on_the_sphere_does_not_change_the_submanifold_s_bundle() -> None:
    r"""The north chart's frame trivializes the chart domain's tangent bundle, whatever other charts the sphere carries.

    The frame is stated on the two charts the domain presents -- the north chart and the
    south one read on it -- and those cover the domain: the chart cut on the sphere lies
    inside the north chart.  So the frame is a basis of every fibre, and the module of
    sections is free of rank two.
    """
    sphere, submanifold = _the_sphere_with_an_extra_chart("X1")
    sections = submanifold.tangent_bundle().sections()
    frame = tuple(
        sections.coordinate_vector_field(submanifold.atlas()["U_N"], index)
        for index in range(2)
    )

    trivialized = sections.trivialized_by(frame)

    assert trivialized.module_rank() == 2
    assert trivialized.basis() == frame
    assert "X1" in submanifold.chart_labels()


def test_a_smooth_function_is_stated_on_the_charts_that_cover_the_domain() -> None:
    r"""$x_1$ on the north chart and $y_1/\lvert y\rvert^2$ on the south one are one function, without naming the extra chart.

    The two charts cover the domain, and the pair has a stated coordinate change, so the
    agreement of the two expressions is the question that decides the function.
    """
    _sphere, submanifold = _the_sphere_with_an_extra_chart("X2")
    north = submanifold.atlas()["U_N"]
    south = submanifold.atlas()["U_S"]
    norm_squared = south.coordinate(0) ** 2 + south.coordinate(1) ** 2

    function = submanifold.smooth_function(
        {
            "U_N": north.coordinate(0),
            "U_S": south.section_ratio(south.coordinate(0), norm_squared),
        }
    )

    at = submanifold.atlas()["U_S"].domain()((RR(2) / RR(13), RR(3) / RR(13)))
    assert function(at) == RR(2)


def test_a_family_that_does_not_cover_the_manifold_is_refused() -> None:
    r"""One chart of a two-chart domain states no section: the other chart's points have no component.

    Coverage is decided, not assumed: a chart of the atlas that lies inside none of the
    charts given leaves points the section says nothing about, and the constructor refuses
    rather than completing it.
    """
    sphere = SmoothManifolds().sphere(1)
    north = sphere.atlas()["U_N"]

    with pytest.raises(AssertionError):
        sphere.smooth_function({"U_N": north.coordinate(0)})
