r"""The functions on the base scale the sections of a pullback, and pulling back commutes with them.

The sections of a vector bundle are a module over the functions on its base, and the
pullback along $f: N \to M$ is a map of modules from the sections over $M$ to the sections
over $N$: a function $g$ on $M$ acts on a section $s$ by $(gs)(p) = g(p)s(p)$, and pulling
$(gs)$ back gives $(g \circ f)$ times the pullback of $s$, since the fibre of the pullback
at $q$ is the fibre at $f(q)$ (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).

The specimen is the plane's tangent bundle pulled back along $f(x, y) = (2x, 3y)$, with
$g = x + y$ on the base and $V = (x, y)$ a section: $f^*V$ has components $(2x, 3y)$, and
$g \circ f = 2x + 3y$ scales it there.
"""

import pytest

from sage_extensions.all import *


def _the_plane():
    r"""The plane, its chart, the coordinates, and the endomorphism $f(x, y) = (2x, 3y)$."""
    plane = SmoothManifolds()(2, "R^2")
    chart = plane.chart("U", "x y")
    x, y = chart.coordinate(0), chart.coordinate(1)
    return plane, chart, x, y, plane.Mor(plane)({("U", "U"): (x + x, y + y + y)})


def test_a_function_of_the_base_scales_a_pullback_section() -> None:
    r"""$(x + y) \cdot f^*(x, y)$ takes $(1, 2)$ to $3 \cdot (2, 6) = (6, 18)$.

    A section of the pullback is a map into the fibres over the image, and the functions
    on the pullback's base scale it pointwise, so its components are the function's value
    times the section's there.
    """
    plane, _chart, x, y, mapping = _the_plane()
    tangent = plane.tangent_bundle()
    pulled = tangent.pullback_along(mapping)
    section = pulled.sections().pullback_of(tangent.sections().section({"U": (x, y)}))
    function = plane.smooth_function({"U": x + y})
    at = plane((1, 2))

    scaled = function * section

    assert scaled.parent() is pulled.sections()
    assert tuple(entry(at) for entry in scaled.components()["U"]) == (RR(6), RR(18))


def test_pulling_back_commutes_with_the_scalars_of_the_base() -> None:
    r"""$f^*(gV) = (g \circ f) f^*V$: for $g = x + y$ and $f = (2x, 3y)$, $g \circ f = 2x + 3y$.

    The pullback is a map of modules, so scaling a section on the base and then pulling
    back is scaling the pulled-back section by the pulled-back function.
    """
    plane, _chart, x, y, mapping = _the_plane()
    tangent = plane.tangent_bundle()
    pulled = tangent.pullback_along(mapping)
    section = tangent.sections().section({"U": (x, y)})
    function = plane.smooth_function({"U": x + y})
    composed = plane.smooth_function({"U": x + x + y + y + y})
    at = plane((1, 2))

    left = pulled.sections().pullback_of(function * section)
    right = composed * pulled.sections().pullback_of(section)

    assert tuple(entry(at) for entry in left.components()["U"]) == (RR(16), RR(48))
    assert left == right


def test_the_unit_of_the_functions_fixes_a_pullback_section() -> None:
    r"""$1 \cdot s = s$: the constant function one is the module's unit on a pullback's sections."""
    plane, _chart, x, y, mapping = _the_plane()
    tangent = plane.tangent_bundle()
    pulled = tangent.pullback_along(mapping)
    section = pulled.sections().pullback_of(tangent.sections().section({"U": (x, y)}))
    one = plane.smooth_functions().one()

    assert one * section == section


def test_the_tangent_bundle_s_own_sections_are_scaled_the_same_way() -> None:
    r"""The same product on the tangent bundle of the plane is unchanged: $(x + y)(x, y) = (x^2 + xy,\ xy + y^2)$."""
    plane, _chart, x, y, _mapping = _the_plane()
    tangent = plane.tangent_bundle()
    section = tangent.sections().section({"U": (x, y)})
    function = plane.smooth_function({"U": x + y})
    at = plane((2, 3))

    scaled = function * section

    assert tuple(entry(at) for entry in scaled.components()["U"]) == (RR(10), RR(15))
