r"""Square-integrable functions on the real line.

$f \in L^2(\mathbb R)$ exactly when $\int_{\mathbb R} |f|^2 < \infty$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_gaussian_is_square_integrable_and_x_squared_and_sine_are_not() -> None:
    r"""$\int e^{-2x^2}\,dx = \sqrt{\pi/2}$; $x^2$ and $\sin x$ have divergent square integrals.

    Source: the Gaussian integral; by hand.
    """
    maps = C(Infinity, RR, RR)
    L = Lp(2, RR, RR)
    g(t) = exp(-t^2)
    square(u) = u^2
    sine(v) = sin(v)
    gaussian = L(maps(g))
    assert gaussian(0) == 1
    assert L.q(gaussian) == sqrt(pi / 2)
    assert g in L
    assert square not in L
    assert sine not in L


def test_the_integral_pairing_on_minus_one_one_gives_x_x_two_thirds_and_x_x2_zero() -> None:
    r"""$\int_{-1}^1 x^2\,dx = 2/3$ and $\int_{-1}^1 x^3\,dx = 0$ (an odd integrand).

    Source: by hand.
    """
    maps = C(Infinity, RR, RR)
    square(t) = t^2
    cube(u) = u^3
    xx = maps.integral(maps(square), 0)
    xxx = maps.integral(maps(cube), 0)
    assert xx(1) - xx(-1) == QQ(2) / 3
    assert xxx(1) - xxx(-1) == 0


def test_rational_functions_in_l2_are_those_of_degree_at_most_minus_one_without_real_poles() -> None:
    r"""$1/(1+x^2)$ decays like $x^{-2}$; $1/x$ has a non-square-integrable pole at $0$;
    $x^2/(1+x^2) \to 1$ at infinity.

    Source: comparison with $\int |x|^{-2k}$; by hand.
    """
    L = Lp(2, RR, RR)
    lorentzian(t) = 1 / (1 + t^2)
    odd(u) = u / (1 + u^2)
    reciprocal(v) = 1 / v
    saturating(w) = w^2 / (1 + w^2)
    assert lorentzian in L
    assert odd in L
    assert reciprocal not in L
    assert saturating not in L


def test_bounded_multiples_and_decaying_tails_are_in_l2_and_tanh_is_not() -> None:
    r"""$|\sin x/(1+x^2)| \le 1/(1+x^2)$, $\operatorname{sech}(x^2) \le 2e^{-x^2}$, $e^{-\cosh x} \le e^{-|x|/2}$
    are square integrable; $\tanh x \to \pm 1$ is not.

    Source: comparison test; by hand.
    """
    L = Lp(2, RR, RR)
    damped(t) = sin(t) / (1 + t^2)
    secant(u) = sech(u^2)
    tail(v) = exp(-cosh(v))
    saturating(w) = tanh(w)
    assert damped in L
    assert secant in L
    assert tail in L
    assert saturating not in L


def test_exp_minus_abs_x_is_in_l2_and_exp_minus_x_is_not() -> None:
    r"""$\int e^{-2|x|} = 1$; $\int_{-\infty}^0 e^{-2x} = \infty$. Source: by hand."""
    L = Lp(2, RR, RR)
    decay(t) = exp(-abs(t))
    one_sided(u) = exp(-u)
    assert decay in L
    assert one_sided not in L


def test_zero_and_x_times_the_gaussian_are_in_l2() -> None:
    r"""$\int x^2 e^{-2x^2}\,dx = \sqrt{\pi/2}/4$. Source: Gaussian moments; by hand."""
    maps = C(Infinity, RR, RR)
    L = Lp(2, RR, RR)
    assert L.zero() in L
    moment(t) = t * exp(-t^2)
    weighted = L(maps(moment))
    assert weighted(2) == 2 * exp(-4)
    assert L.q(weighted) == sqrt(pi / 2) / 4
