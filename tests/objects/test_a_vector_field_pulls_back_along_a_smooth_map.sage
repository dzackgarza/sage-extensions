r"""A vector field pulls back along a smooth map, and the pullback is a bundle of its own.

The pullback $f^*E$ of a vector bundle $E \to M$ along a smooth map $f: N \to M$ is the
bundle over $N$ whose fibre at $q$ is the fibre of $E$ at $f(q)$; a section of $E$ gives
one of $f^*E$ by $q \mapsto s(f(q))$ (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
Ch. 10).  Along an open inclusion the differential is an isomorphism at every point and
the pullback of the tangent bundle is the tangent bundle of the domain, but along any
other smooth map it is a bundle of its own: $f^*TM$ need not be $TN$, and a section of
it that is not the pullback of one needs the bundle's transition functions on a cover of
the target.

The specimen is the plane's tangent bundle along $f(x, y) = (2x, 3y)$: the section
$(x, y)$ pulls back to $(2x, 3y)$, taking at $(1, 2)$ the value that $(x, y)$ takes at
$f(1, 2) = (2, 6)$; and the map is no inclusion, since its coordinate representation is
not the identity.
"""

import pytest

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, the two coordinates, and the endomorphism $f(x, y) = (2x, 3y)$."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    return plane, chart, x, y, plane.Mor(plane)({("U", "U"): (x + x, y + y + y)})


def test_the_pullback_of_the_tangent_bundle_along_a_smooth_map_is_its_own_bundle() -> None:
    r"""$f^*T\mathbb{R}^2$ is a rank-two bundle on the plane, and it is not $T\mathbb{R}^2$: it retains the bundle and the map it came from.

    The map's coordinate representation is $(2x, 3y)$, which is not the identity, so this
    is no inclusion and the pullback is not the tangent bundle of its domain.
    """
    plane, _chart, _x, _y, mapping = _the_plane()
    tangent = plane.tangent_bundle()

    pulled = tangent.pullback_along(mapping)

    assert pulled.base_manifold() is plane
    assert pulled.rank() == tangent.rank()
    assert pulled.is_pullback() is True
    assert pulled.underlying_bundle() is tangent
    assert pulled.mapping() is mapping


def test_the_pullback_of_a_section_takes_at_a_point_the_value_at_the_image_point() -> None:
    r"""$(x, y) \circ f = (2x, 3y)$, which takes $(1, 2)$ to $(2, 6)$: the value at $f(1, 2)$.

    The pullback's component in the plane's chart is the section's component on the
    target chart composed with the coordinate representation of the map, which is what
    the section of the pullback is.
    """
    plane, chart, x, y, mapping = _the_plane()
    pulled = plane.tangent_bundle().pullback_along(mapping)
    section = plane.tangent_bundle().sections().section({"U": (x, y)})
    at = plane((1, 2))
    image = mapping(at)

    pulled_back = pulled.sections().pullback_of(section)

    assert tuple(entry(at) for entry in pulled_back.components()["U"]) == (RR(2), RR(6))
    assert tuple(entry(image) for entry in section.components()["U"]) == (RR(2), RR(6))


def test_the_pullback_is_additive_and_carries_the_negatives() -> None:
    r"""$f^*(V + W) = f^*V + f^*W$ and $f^*(-V) = -f^*V$: the pullback is a map of abelian groups.

    Sections are added pointwise in the fibres, and the fibre of the pullback at $q$ is
    the fibre of the bundle at $f(q)$, so adding commutes with pulling back.
    """
    plane, chart, x, y, mapping = _the_plane()
    tangent = plane.tangent_bundle()
    pulled = tangent.pullback_along(mapping)
    first = tangent.sections().section({"U": (x, y)})
    second = tangent.sections().section({"U": (y, x)})

    assert pulled.sections().pullback_of(first + second) == (
        pulled.sections().pullback_of(first) + pulled.sections().pullback_of(second)
    )
    assert pulled.sections().pullback_of(-first) == -(pulled.sections().pullback_of(first))


def test_a_section_of_the_pullback_that_is_not_a_pullback_is_refused() -> None:
    r"""$f^*T\mathbb{R}^2$'s sections are stated in the bundle's trivializations on a cover of the target, which this owner does not retain."""
    plane, chart, x, _y, mapping = _the_plane()
    pulled = plane.tangent_bundle().pullback_along(mapping)

    with pytest.raises(AssertionError):
        pulled.sections().section({"U": (chart.coordinate(0), chart.coordinate(1))})


def test_the_pullback_along_an_open_inclusion_is_still_the_domain_s_tangent_bundle() -> None:
    r"""The canonical case is unchanged: along the inclusion of a chart domain the pullback of $T\mathbb{R}^2$ is the tangent bundle of that domain."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    punctured = plane.chart_on_open_subset("W", "x y", "U", (chart.coordinate(0),))
    domain = punctured.domain()
    inclusion = plane.open_submanifold_inclusion(domain)

    pulled = plane.tangent_bundle().pullback_along(inclusion)

    assert pulled.base_manifold() is domain
    assert pulled.is_pullback() is False
    assert pulled.rank() == 2
