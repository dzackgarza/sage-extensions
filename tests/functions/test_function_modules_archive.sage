r"""Which functions on $\mathbb{R}$ are square-integrable."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rational_functions_in_l2_are_those_with_no_real_pole_and_decay() -> None:
    r"""$1/(1+x^2)$ and $x/(1+x^2)$ are in $L^2(\mathbb{R})$; $x^2$, $1/x$ and $x^2/(1+x^2)$ are not.

    A rational function is square-integrable on $\mathbb{R}$ iff it has no
    real pole and its degree is at most $-1$ at infinity.
    """
    space = Lp(2, RR, RR)
    lorentzian(t) = 1 / (1 + t^2)
    odd(u) = u / (1 + u^2)
    square(v) = v^2
    reciprocal(w) = 1 / w
    saturating(y) = y^2 / (1 + y^2)

    assert lorentzian in space
    assert odd in space
    assert square not in space
    assert reciprocal not in space
    assert saturating not in space
    assert space(odd)(1) == RR(1) / 2


def test_decaying_and_bounded_products_are_in_l2_but_sine_is_not() -> None:
    r"""$x e^{-x^2}$, $3e^{-x^2} - 2/(1+x^2)$ and $\sin(x)/(1+x^2)$ are in $L^2(\mathbb{R})$; $\sin x$ is not."""
    space = Lp(2, RR, RR)
    moment(t) = t * exp(-t^2)
    difference(u) = 3 * exp(-u^2) - 2 / (1 + u^2)
    damped(v) = sin(v) / (1 + v^2)
    sine(w) = sin(w)

    assert moment in space
    assert difference in space
    assert damped in space
    assert sine not in space
    assert space(moment)(2) == 2 * exp(-4)


def test_two_sided_exponential_decay_is_in_l2_but_one_sided_is_not() -> None:
    r"""$\int_{\mathbb{R}} e^{-2|x|}\,dx = 1$, while $e^{-2x}$ is not integrable on $(-\infty, 0]$."""
    space = Lp(2, RR, RR)
    decay(t) = exp(-abs(t))
    one_sided(u) = exp(-u)
    two_sided = space(decay)

    assert decay in space
    assert one_sided not in space
    assert space.q(two_sided) == 1
