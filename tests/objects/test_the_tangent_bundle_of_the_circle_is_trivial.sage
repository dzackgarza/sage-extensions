r"""The tangent bundle of the circle is a rank-one bundle, trivialized by a stated frame.

The tangent space of a smooth manifold at a point is the space of derivations of the
algebra of germs of smooth functions there, so a vector field is a derivation of
$C^\infty(M)$ and the sections of $TM$ are exactly the derivations of that algebra
(Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3 and Ch. 10).  The tangent
bundle of $S^1$ is trivial of rank one, and a trivialization is a global section that
is a basis of every fibre: $E = (1 + x^2)\partial_x$ on the north chart and
$E = -(1 + y^2)\partial_y$ on the south chart, two expressions that agree on the
overlap because $\partial_y = -x^2 \partial_x$ there.  Triviality is a datum here and
never a flag: the engine's unawareness of a frame on some manifold is not a proof that
none exists, and no fictitious global chart is added to $S^1$ to state the frame.

The specimen is the smallest that decides it: the two stereographic charts, a function
$h$ written in both, and the derivative $E(h)$ read at one point in each chart.
"""

import pytest

from sage_extensions.all import *


def _the_circle():
    r"""$S^1$, its two stereographic charts, and their coordinates."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    return circle, north, south, north.coordinate(0), south.coordinate(0)


def _the_frame(circle, x, y):
    r"""The global section $E$ whose components in the two charts are $1 + x^2$ and $-(1 + y^2)$.

    The components are written with the chart's own unit, which is the constant
    function taking the value one on that chart.
    """
    one_north = circle.atlas()["U_N"].function_ring().one()
    one_south = circle.atlas()["U_S"].function_ring().one()
    return circle.tangent_bundle().sections().section(
        {"U_N": (one_north + x**2,), "U_S": (-(one_south + y**2),)}
    )


def test_the_tangent_bundle_of_the_circle_is_a_rank_one_bundle_on_it() -> None:
    r"""$\operatorname{rank} TS^1 = \dim S^1 = 1$, and its sections are a $C^\infty(S^1)$-module.

    The tangent space at a point has the dimension of the manifold, so the bundle has
    that rank; and the sections of a vector bundle form a module over the functions on
    the base (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).
    """
    circle, _north, _south, _x, _y = _the_circle()
    tangent = circle.tangent_bundle()

    assert tangent.base_manifold() is circle
    assert tangent.rank() == circle.dimension()
    assert tangent.sections() in Modules(circle.smooth_functions())
    assert tangent.sections().vector_bundle() is tangent


def test_a_vector_field_is_stated_by_its_chart_components_and_they_must_agree() -> None:
    r"""One section is one object on the manifold: its components are related by the transitions.

    With $y = 1/x$ the coordinate change has $\partial_y = -x^2\partial_x$, so the
    components of a vector field satisfy $a_S(1/x)(-x^2) = a_N(x)$.  The frame $E$
    satisfies it; the constant $1$ on both charts does not, and is a different vector
    field on each chart rather than a section.
    """
    circle, north, south, x, y = _the_circle()
    sections = circle.tangent_bundle().sections()

    frame = _the_frame(circle, x, y)
    assert frame in sections
    at_two = circle.point((2,), "U_N")
    at_half = circle.point((QQ(1) / 2,), "U_S")
    assert frame.components()["U_N"][0](at_two) == RR(5)
    assert frame.components()["U_S"][0](at_half) == -RR(5) / RR(4)

    with pytest.raises(AssertionError):
        sections.section({"U_N": (RR.one(),), "U_S": (RR.one(),)})


def test_the_frame_trivializes_the_bundle_and_its_two_maps_are_inverse() -> None:
    r"""$S^1 \times \mathbb R \to TS^1$, $(p,a) \mapsto aE_p$, with inverse $V \mapsto V/E$.

    A section that is a basis of every fibre is a trivialization of a rank-one bundle
    (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  The two maps are
    inverse on the expressions: $\frac{a(1+x^2)}{1+x^2} = a$ on the north chart and
    $\frac{-a(1+y^2)}{-(1+y^2)} = a$ on the south, so $a \mapsto aE \mapsto a$ is the
    identity of $C^\infty(S^1)$.
    """
    circle, north, south, x, y = _the_circle()
    sections = circle.tangent_bundle().sections()
    frame = _the_frame(circle, x, y)
    trivialized = sections.trivialized_by(frame)
    trivialization = trivialized.trivialization()

    assert circle.tangent_bundle().rank() == 1
    assert trivialized.vector_bundle() is sections.vector_bundle()
    assert trivialized.module_rank() == 1
    assert trivialized.basis() == (frame,)
    assert trivialization.frame() is frame

    a = circle.smooth_function(
        {
            "U_N": north.section_ratio(x + x, north.function_ring().one() + x**2),
            "U_S": south.section_ratio(y + y, south.function_ring().one() + y**2),
        }
    )
    at_two = circle.point((2,), "U_N")
    assert trivialization.inverse(trivialization.forward(a))(at_two) == a(at_two)
    assert trivialization.inverse(trivialization.forward(a))(at_two) == RR(4) / RR(5)
    assert trivialization.forward(trivialization.inverse(frame)) == frame


def test_a_bundle_without_a_retained_frame_does_not_answer_for_freeness() -> None:
    r"""The sections of $TS^2$ are not a free module, and the tree does not guess which.

    A module of sections is free exactly when a global frame is known, and the failure of
    an engine to know one is not a proof that none exists (Lee, *Introduction to Smooth
    Manifolds*, 2nd ed., Ch. 10).  $TS^2$ retains no frame here, so its module of
    sections has no stated rank, and no chart is invented to give it one.
    """
    sphere = SmoothManifolds().sphere(2)
    tangent = sphere.tangent_bundle()

    assert tangent.rank() == 2
    with pytest.raises(AssertionError):
        tangent.sections().module_rank()
    with pytest.raises(AssertionError):
        tangent.sections().trivialization()


def test_the_frame_acts_on_a_smooth_function_as_the_derivation_it_is() -> None:
    r"""$E(h) = 2(1 - x^2)/(1 + x^2)$ on the north chart and $-2(1 - y^2)/(1 + y^2)$ on the south.

    For $h$ with $h_N(x) = 2x/(1 + x^2)$ and $h_S(y) = 2y/(1 + y^2)$, and
    $E_N = (1 + x^2)\partial_x$, $E_S = -(1 + y^2)\partial_y$:
    $E_N(h) = (1 + x^2)\frac{2(1 - x^2)}{(1 + x^2)^2} = \frac{2(1 - x^2)}{1 + x^2}$, and
    the south chart gives the same function under $y = 1/x$.  So the derivative is one
    smooth function on $S^1$, and it takes the value $-6/5$ at the point of coordinate
    $x = 2$ -- read in either chart.  A derivation kills constants, and obeys Leibniz.
    """
    circle, north, south, x, y = _the_circle()
    frame = _the_frame(circle, x, y)
    h = circle.smooth_function(
        {
            "U_N": north.section_ratio(x + x, north.function_ring().one() + x**2),
            "U_S": south.section_ratio(y + y, south.function_ring().one() + y**2),
        }
    )
    derivative = frame(h)
    at_two = circle.point((2,), "U_N")

    assert derivative(at_two) == -RR(6) / RR(5)
    assert derivative(circle.point((QQ(1) / 2,), "U_S")) == -RR(6) / RR(5)
    assert derivative(at_two) == 2 * (1 - RR(2) ** 2) / (1 + RR(2) ** 2)

    constant = circle.smooth_functions().one()
    assert frame(constant)(at_two) == RR.zero()

    product = h * h
    left = frame(product)(at_two)
    right = 2 * h(at_two) * frame(h)(at_two)
    assert left == right
