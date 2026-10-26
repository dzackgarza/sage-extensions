r"""Hölder pairings of Lebesgue spaces, with values computed by hand."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_holder_pairing_of_the_gaussian_in_l1_and_linf_is_root_pi_over_two() -> None:
    r"""$\int_{\mathbb{R}} e^{-x^2} e^{-x^2}\,dx = \int_{\mathbb{R}} e^{-2x^2}\,dx = \sqrt{\pi/2}$."""
    maps = C(oo, RR, RR)
    g(t) = exp(-t^2)
    gaussian = maps(g)
    holder = Lp(1, RR, RR) * Lp(oo, RR, RR)

    assert holder.pairing(Lp(1, RR, RR)(gaussian), Lp(oo, RR, RR)(gaussian)) == RR(sqrt(pi / 2))


def test_the_l2_norm_squared_of_the_gaussian_is_root_pi_over_two() -> None:
    r"""$\|e^{-x^2}\|_2^2 = \int_{\mathbb{R}} e^{-2x^2}\,dx = \sqrt{\pi/2}$, and $q(f) = b(f, f)$."""
    space = Lp(2, RR, RR)
    maps = C(oo, RR, RR)
    g(t) = exp(-t^2)
    gaussian = space(maps(g))

    assert space.b(gaussian, gaussian) == RR(sqrt(pi / 2))
    assert space.q(gaussian) == RR(sqrt(pi / 2))


def test_the_holder_pairing_of_a_geometric_sequence_with_the_constant_one_is_two() -> None:
    r"""$\sum_{n \ge 0} 2^{-n} \cdot 1 = 2$ and $\sum_{n \ge 0} (2^{-n})^2 = 4/3$."""
    a(k) = 2^(-k)
    holder = ell(1, NN, RR) * ell(oo, NN, RR)
    geometric = ell(2, NN, RR)(a)

    assert holder.pairing(ell(1, NN, RR)(a), ell(oo, NN, RR).one()) == RR(2)
    assert ell(2, NN, RR).q(geometric) == RR(QQ(4) / 3)
