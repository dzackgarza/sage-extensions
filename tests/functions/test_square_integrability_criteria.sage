r"""Which elementary maps ``RR -> RR`` are square-integrable.

A polynomial ``p != 0`` is not in ``L^2(RR)`` (``int p^2 = oo``); a rational
function ``p/q`` in lowest terms is in ``L^2`` exactly when ``q`` has no real
root and ``deg q >= deg p + 1``; ``sin`` and ``cos`` of a linear argument are
not, their squares averaging ``1/2``; a Gaussian times a polynomially bounded
map is; a sum of an ``L^2`` map and a non-``L^2`` map is not, since ``L^2`` is
a vector space.  Values: ``int x^2 e^{-x^2} dx = sqrt(pi)/2`` by parts from the
Gaussian integral.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_gaussians_times_bounded_maps_are_square_integrable() -> None:
    r"""``x^2 e^{-x^2}``, ``sin(x) e^{-x^2}``, ``e^{-x^4}`` and ``e^{-x^2} + e^{-|x|}`` are in ``L^2(RR)``."""
    space = Lp(2, RR, RR)
    f1(x) = x * x * exp(-x * x)
    f2(x) = sin(x) * exp(-x * x)
    f3(x) = exp(-x * x * x * x)
    f4(x) = exp(-x * x) + exp(-abs(x))

    assert space(f1)(1) == exp(-1)
    assert space(f2)(0) == 0
    assert space(f3)(1) == exp(-1)
    assert space(f4)(0) == 2


def test_the_second_moment_of_the_gaussian() -> None:
    r"""``int x^2 e^{-x^2} dx = sqrt(pi) / 2``."""
    space = Lp(1, RR, RR)
    f1(x) = x * x * exp(-x * x)

    assert space.integration_morphism()(space(f1)) == sqrt(pi) / 2


def test_nonzero_polynomials_are_not_square_integrable() -> None:
    r"""``int x^2 = int x^4 = oo``."""
    space = Lp(2, RR, RR)
    f1(x) = x
    f2(x) = x * x

    assert f1 not in space
    with pytest.raises(ValueError):
        space(f2)


def test_cosine_is_not_square_integrable() -> None:
    r"""``int_0^{2 pi N} cos^2 = pi N`` grows without bound."""
    space = Lp(2, RR, RR)
    f1(x) = cos(x)

    assert f1 not in space


def test_a_square_integrable_map_plus_sine_is_not_square_integrable() -> None:
    r"""If ``e^{-x^2} + sin x`` were in ``L^2`` then so would ``sin x`` be, since ``L^2`` is a vector space."""
    space = Lp(2, RR, RR)
    f1(x) = exp(-x * x) + sin(x)

    assert f1 not in space


def test_the_gaussian_is_in_every_Lp() -> None:
    r"""``e^{-x^2}`` is bounded and integrable, hence in ``L^p`` for every ``p >= 1``; its value at 0 is 1."""
    f1(x) = exp(-x * x)
    f2(x) = exp(-x * x)

    assert Lp(3, RR, RR)(f1)(0) == 1
    assert Lp(oo, RR, RR)(f2)(0) == 1


def test_a_rational_function_without_real_poles_decaying_like_one_over_x_is_square_integrable() -> None:
    r"""``x / (x^2 + pi)`` has no real pole and ``deg q = deg p + 1``: it is in ``L^2`` and not ``L^1``."""
    f1(x) = x / (x * x + pi)
    f2(x) = x / (x * x + pi)

    assert Lp(2, RR, RR)(f1)(0) == 0
    assert f2 not in Lp(1, RR, RR)


def test_sine_of_a_multiple_of_x_is_not_square_integrable() -> None:
    r"""``int sin(2x)^2 = oo``."""
    f1(x) = sin(2 * x)

    assert f1 not in Lp(2, RR, RR)
