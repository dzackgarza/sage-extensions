r"""Hölder and Young products of Gaussians on the real line."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pointwise_square_of_the_l2_gaussian_is_in_l1_with_integral_sqrt_pi_over_2() -> None:
    r"""For ``g = exp(-x^2) ∈ L^2(R)``, Hölder places ``g · g = exp(-2x^2)`` in
    ``L^1`` (degrees ``1/2 + 1/2 = 1``), and
    ``<g, g>_{L^2} = ∫ exp(-2x^2) dx = sqrt(pi/2)`` (Gaussian integral
    ``∫ exp(-a x^2) dx = sqrt(pi/a)``)."""
    algebra = GradedLebesgueAlgebra
    g(t) = exp(-t^2)
    h(u) = exp(-2 * u^2)
    gaussian = Lp(2, RR, RR)(g)
    square = algebra(gaussian) * algebra(gaussian)

    assert square.homogeneous_component(NonNegativeReals(1)) == Lp(1, RR, RR)(h)
    assert algebra.integral_pairing()(algebra(gaussian), algebra(gaussian)) == RR(sqrt(pi / 2))
    assert Lp(2, RR, RR).b(gaussian, gaussian) == RR(sqrt(pi / 2))


def test_self_convolution_of_the_gaussian_is_sqrt_pi_over_2_times_exp_of_minus_x_squared_over_2() -> None:
    r"""``(g * g)(x) = ∫ exp(-t^2) exp(-(x - t)^2) dt = sqrt(pi/2) exp(-x^2/2)``:
    complete the square, ``t^2 + (x - t)^2 = 2(t - x/2)^2 + x^2/2``.  Young's
    inequality places ``L^2 * L^2`` in ``L^∞``."""
    g(t) = exp(-t^2)
    widened(u) = sqrt(pi / 2) * exp(-u^2 / 2)
    gaussian = Lp(2, RR, RR).quotient_by_null_functions()(Lp(2, RR, RR)(g))
    product = LebesgueConvolutionModule.convolution(LebesgueConvolutionModule(gaussian), LebesgueConvolutionModule(gaussian))
    expected = Lp(Infinity, RR, RR).quotient_by_null_functions()(Lp(Infinity, RR, RR)(widened))

    assert product.homogeneous_component(UnitInterval.zero()) == expected


def test_integration_is_multiplicative_for_convolution_on_l1() -> None:
    r"""On ``L^1(R)`` under convolution, ``∫ (f * h) = ∫ f · ∫ h`` (Fubini);
    for ``f = exp(-x^2)``, ``h = exp(-2x^2)``: ``sqrt(pi) · sqrt(pi/2)``.
    Convolution is commutative and associative."""
    algebra = LebesgueConvolutionAlgebra
    g(t) = exp(-t^2)
    narrow(u) = exp(-2 * u^2)
    f = algebra(Lp(1, RR, RR)(g))
    h = algebra(Lp(1, RR, RR)(narrow))
    integral = algebra.integration_morphism()

    assert integral(f) == RR(sqrt(pi))
    assert integral(f * h) == RR(sqrt(pi) * sqrt(pi / 2))
    assert f * h == h * f
    assert (f * f) * h == f * (f * h)
