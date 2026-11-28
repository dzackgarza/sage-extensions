r"""The tangent bundle restricts to an open submanifold, and a chart domain's restriction is trivial.

The differential of an open inclusion $j: U \hookrightarrow M$ is an isomorphism at every
point, so the tangent bundle of $M$ pulled back along $j$ is the tangent bundle of $U$,
and a vector field restricts to a vector field on $U$ (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 3 and Ch. 8).  `U` carries the ambient charts read on it, and
its coordinates are the ambient coordinates there, so the restriction of a section has
the section's components.

The separating case is the stereographic chart of $S^2$ cut where its coordinates do not
all vanish: that open subset $V$ is a proper open submanifold of $S^2$, it is the domain
of one chart, and $TV$ is trivial -- the coordinate frame of that chart is a basis at
every point, with the identity as its components.  $TS^2$ is not trivial, and does not
become so by restricting: neither the ambient manifold's lack of a frame nor a flag about
frames decides the pullback's freeness, the frame of the smaller base does (Lee, Ch. 10).
"""

import pytest

from sage_extensions.all import *


def _the_stereographic_chart_domain(label):
    r"""The open subset of $S^2$ where the stereographic chart's coordinates do not all vanish.

    The chart ``U_N`` projects from the north pole, and its overlap with the chart
    ``U_S`` is the subset where the squared norm of its coordinates does not vanish; the
    chart ``V`` is cut out there, so its domain is a proper open submanifold of $S^2$
    presented by one chart.
    """
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    norm_squared = north.coordinate(0) ** 2 + north.coordinate(1) ** 2
    chart = sphere.chart_on_open_subset(label, "x1 x2", "U_N", (norm_squared,), same_coordinates=True)
    return sphere, chart, chart.domain(), sphere.open_submanifold_inclusion(chart.domain())


def test_the_pullback_of_the_tangent_bundle_along_an_open_inclusion_is_the_domain_s_tangent_bundle() -> None:
    r"""$j^*TS^2 = TV$: the same rank on the smaller base, and its sections are functions on $V$."""
    sphere, _chart, domain, inclusion = _the_stereographic_chart_domain("V1")
    tangent = sphere.tangent_bundle()

    pulled = tangent.pullback_along(inclusion)

    assert pulled.base_manifold() is domain
    assert pulled.rank() == tangent.rank()
    assert pulled.sections() in Modules(domain.smooth_functions())


def test_the_restriction_is_trivial_although_the_tangent_bundle_of_the_sphere_is_not() -> None:
    r"""The coordinate frame of $V$'s one chart is the identity, so $TV$ is trivial; $TS^2$ has no frame.

    The coordinate vector fields of a chart are a basis of the tangent space at every
    point of the chart (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3), and on
    the chart they are the identity matrix of functions, whose determinant is one and
    vanishes nowhere.  $TS^2$ retains no frame, so its module of sections states no rank.
    """
    sphere, chart, domain, inclusion = _the_stereographic_chart_domain("V2")
    tangent = sphere.tangent_bundle()
    pulled = tangent.pullback_along(inclusion)

    frame = tuple(
        pulled.sections().coordinate_vector_field(domain.atlas()[chart.label()], index)
        for index in range(2)
    )
    trivialized = pulled.sections().trivialized_by(frame)

    assert trivialized.module_rank() == 2
    assert trivialized.basis() == frame
    with pytest.raises(AssertionError):
        tangent.sections().module_rank()


def test_a_section_restricts_to_a_section_of_the_open_submanifold() -> None:
    r"""A vector field on the plane restricts to $\{x \neq 0\}$, with its components unchanged there.

    The open subset's chart is the plane's chart read on it, so the restricted section's
    component takes at a point of the subset the value the section's component takes
    there.
    """
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    punctured = plane.chart_on_open_subset("W", "x y", "U", (x,), same_coordinates=True)
    domain = punctured.domain()
    inclusion = plane.open_submanifold_inclusion(domain)
    sections = plane.tangent_bundle().sections()

    section = sections.section(
        {"U": (x, y), "W": (punctured.coordinate(0), punctured.coordinate(1))}
    )
    restricted = sections.restrict(section, inclusion)
    at_two = plane((2, 3))

    assert restricted.parent().vector_bundle().base_manifold() is domain
    assert restricted.components()["W"][0](at_two) == RR(2)
    assert restricted.components()["W"][1](at_two) == RR(3)
