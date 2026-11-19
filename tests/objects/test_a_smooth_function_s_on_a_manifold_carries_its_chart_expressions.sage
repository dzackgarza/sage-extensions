r"""An element of $C^\infty(M)$ carries its chart expressions, so every one of them is differentiable.

The sections of the tangent bundle act on the smooth functions as derivations (Lee,
*Introduction to Smooth Manifolds*, 2nd ed., Ch. 3), and that action is a computation on the
function's expression in a chart.  An algebra whose elements may also be opaque maps -- a
Python callable with no expression anywhere -- is an algebra on which the action is not
defined: the tree can neither differentiate such a map nor even decide its smoothness, since
the differentiability condition answers a proposition on any domain but the line.

So the algebra of smooth functions on a manifold admits the maps it states by their chart
expressions, and refuses an opaque map at its own boundary, naming the construction that
states one.  What it admits, it differentiates: the frame of the circle acts on every
element, including the constants and the products the algebra builds.
"""

import pytest

from sage_extensions.all import *


def _the_circle():
    r"""$S^1$, its two charts, and the frame $E$ trivializing its tangent bundle."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    frame = circle.tangent_bundle().sections().section(
        {
            "U_N": (north.function_ring().one() + north.coordinate(0) ** 2,),
            "U_S": (-(south.function_ring().one() + south.coordinate(0) ** 2),),
        }
    )
    return circle, north, south, frame


def test_an_opaque_map_is_refused_by_the_algebra_of_smooth_functions() -> None:
    r"""A Python callable with no chart expression is not an element of $C^\infty(S^1)$ here.

    The algebra admits the maps it can state in charts; a callable carries no expression, so
    the tree could neither decide that it is smooth nor differentiate it, and admitting it
    would put an element in the algebra that no derivation is defined on.
    """
    circle, _north, _south, _frame = _the_circle()

    with pytest.raises(AssertionError):
        circle.smooth_functions()(lambda point: RR(1))


def test_every_element_the_algebra_admits_is_differentiated_by_the_frame() -> None:
    r"""The frame acts on a chart-stated function, on a constant, and on their product: $E(h)$, $E(1) = 0$, and Leibniz.

    For $h_N(x) = 2x/(1+x^2)$ and $E_N = (1+x^2)\partial_x$, the derivative takes
    $-6/5$ at $x = 2$, the constant one takes $0$ there, and $E(h \cdot h) = 2h\,E(h)$.
    """
    circle, north, south, frame = _the_circle()
    h = circle.smooth_function(
        {
            "U_N": north.section_ratio(north.coordinate(0) + north.coordinate(0), north.function_ring().one() + north.coordinate(0) ** 2),
            "U_S": south.section_ratio(south.coordinate(0) + south.coordinate(0), south.function_ring().one() + south.coordinate(0) ** 2),
        }
    )
    at = circle.point((2,), "U_N")
    constant = circle.smooth_functions().one()

    assert frame(h)(at) == -RR(6) / RR(5)
    assert frame(constant)(at) == RR(0)
    assert frame(h * h)(at) == 2 * h(at) * frame(h)(at)
