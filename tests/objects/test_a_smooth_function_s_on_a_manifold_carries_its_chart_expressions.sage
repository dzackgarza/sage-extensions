r"""Smooth functions need not possess symbolic formulas.

The sections of the tangent bundle act on the smooth functions as derivations (Lee,
*Introduction to Smooth Manifolds*, 2nd ed., Ch. 3). The differentiability
hypothesis is independent of availability of a symbolic formula.
An all-order local derivative datum supports exact differential computation,
including for functions that are not analytic.
"""

from sage_extensions.all import *
import pytest


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


def test_a_set_map_needs_smooth_local_data_to_enter_the_smooth_algebra() -> None:
    r"""The constant point map is smooth, but its opaque program supplies no jets.

    The same mathematical function enters by its actual constant or
    all-order derivative datum; its derivatives are identically zero.
    """
    circle, _north, _south, frame = _the_circle()
    algebra = circle.smooth_functions()
    evaluator = lambda point: RR(1)
    general = Sets().Mor(circle, RR)(evaluator)
    point = circle.point((2,), "U_N")
    assert general(point) == RR(1)
    assert evaluator not in algebra
    assert general not in algebra
    with pytest.raises(AssertionError):
        algebra(evaluator)
    with pytest.raises(AssertionError):
        algebra(general)
    function = algebra.from_local_derivatives(
        lambda chart, point, alpha: RR(1) if sum(alpha) == 0 else RR(0))
    for constant in (function, algebra.one()):
        assert constant.parent() is algebra
        assert constant(point) == RR(1)
        assert frame(constant)(point) == RR(0)
        assert frame(frame(constant))(point) == RR(0)


def test_derivation_and_local_inverse_with_all_order_derivative_data() -> None:
    r"""A constant coefficient supplied as a smooth germ datum, not a Sage formula.

    With E the global frame of the circle, D = 2 E has components
    2(1+x^2) and -2(1+y^2). D of the stereographic smooth function
    h=2x/(1+x^2) is -12/5 at x=2.
    """
    circle, north, south, frame = _the_circle()
    algebra = circle.smooth_functions()
    two = algebra.from_local_derivatives(lambda chart, point, alpha:
                                         RR(2) if sum(alpha) == 0 else RR(0))
    field = frame.parent().scalar_multiple(two, frame)
    x, y = north.coordinate(0), south.coordinate(0)
    h = circle.smooth_function({
        "U_N": north.section_ratio(x + x, north.function_ring().one() + x**2),
        "U_S": south.section_ratio(y + y, south.function_ring().one() + y**2),
    })
    point = circle.point((2,), "U_N")
    assert field(h)(point) == -RR(12) / RR(5)
    recovered = frame.parent().from_derivation(lambda f: field(f))
    assert recovered.components()["U_N"][0](north.domain()((2,))) == RR(10)
    assert recovered.components()["U_S"][0](south.domain()((RR(1)/2,))) == -RR(5)/2
    assert recovered(h)(point) == -RR(12)/5


def test_the_frame_differentiates_chart_functions_and_products() -> None:
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


def test_the_smooth_algebra_owns_its_derivations_as_tangent_sections() -> None:
    r"""Der_R(C^oo(M), C^oo(M)) is Gamma(TM), not a finite algebra presentation.

    Lee, *Introduction to Smooth Manifolds*, 2nd ed., Prop. 8.15. With
    E=(1+x^2)d/dx on the north chart and D=2E, D of h=2x/(1+x^2)
    is -12/5 at x=2, and D(h^2)=2hD(h). Both scalar structures are
    those of the same function algebra.
    """
    circle, north, south, frame = _the_circle()
    algebra = circle.smooth_functions()
    sections = circle.tangent_bundle().sections()
    assert algebra.derivations() is sections
    assert algebra.derivations(algebra.regular_module()) is sections
    assert algebra.vector_fields() is sections
    assert sections.base_ring() is algebra
    coefficient = algebra.from_local_derivatives(lambda chart, point, alpha:
        RR(2) if sum(alpha) == 0 else RR(0))
    vector = sections.scalar_multiple(coefficient, frame)
    assert sections.from_derivation(vector) is vector
    h = circle.smooth_function({
        "U_N": north.section_ratio(2*north.coordinate(0), north.function_ring().one()+north.coordinate(0)**2),
        "U_S": south.section_ratio(2*south.coordinate(0), south.function_ring().one()+south.coordinate(0)**2),
    })
    p = circle.point((2,), "U_N")
    derivative = sections.from_derivation(lambda f: vector(f))
    assert derivative(h).parent() is algebra
    assert derivative(h)(p) == -RR(12)/5
    assert derivative(h*h)(p) == 2*h(p)*derivative(h)(p)
    assert derivative(algebra.one())(p) == RR(0)


def test_zero_derivation_annihilates_a_smooth_function() -> None:
    r"""The zero vector field annihilates every smooth function, independently of its presentation."""
    circle, _north, _south, frame = _the_circle()
    algebra = circle.smooth_functions()
    function = algebra.from_local_derivatives(
        lambda chart, point, alpha: RR(1) if sum(alpha) == 0 else RR(0))
    p = circle.point((2,), "U_N")
    zero = frame.parent().zero()
    assert function.parent() is algebra
    assert zero(function).parent() is algebra
    assert zero(function)(p) == RR(0)
    assert frame(zero(function))(p) == RR(0)
