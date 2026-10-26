r"""The real Lebesgue spaces ``L^p(RR)``: membership, Hölder conjugates, the integral on ``L^1``.

Values are the Gaussian integral ``int e^{-x^2} dx = sqrt(pi)``, the elementary
``int e^{-|x|} dx = 2``, the odd integrand ``int x e^{-x^2} dx = 0``, and the
defining relation ``1/p + 1/q = 1`` of Hölder conjugate exponents.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_integration_on_L1_is_the_linear_functional_with_the_gaussian_and_laplace_values() -> None:
    r"""``int: L^1(RR) -> RR`` sends ``e^{-x^2}`` to ``sqrt(pi)`` and ``e^{-|x|}`` to ``2``.

    It is linear, so ``e^{-|x|} + e^{-x^2}`` goes to ``2 + sqrt(pi)`` and
    ``3 e^{-|x|}`` to ``6``; the odd function ``x e^{-x^2}`` integrates to ``0``.
    """
    space = Lp(1, RR, RR)
    f1(x) = exp(-x * x)
    f2(x) = exp(-abs(x))
    f3(x) = x * exp(-x * x)
    integral = space.integration_morphism()
    gaussian = space(f1)
    laplace = space(f2)

    assert integral.domain() is space
    assert integral(gaussian) == sqrt(pi)
    assert integral(laplace) == 2
    assert integral(gaussian + laplace) == sqrt(pi) + 2
    assert integral(3 * laplace) == 6
    assert integral(space(f3)) == 0


def test_integration_is_not_a_functional_on_L2() -> None:
    r"""``1/(1+|x|)`` is in ``L^2(RR)`` and not in ``L^1(RR)``, so ``int`` is no functional on ``L^2``."""
    with pytest.raises(TypeError):
        Lp(2, RR, RR).integration_morphism()


def test_holder_conjugate_exponents_satisfy_one_over_p_plus_one_over_q_is_one() -> None:
    r"""``L^3`` pairs with ``L^{3/2}``, ``L^1`` with ``L^oo``, ``L^oo`` with ``L^1``; ``L^2`` is self-conjugate."""
    assert Lp(3, RR, RR).conjugate_lebesgue_space().integrability_exponent() == QQ(3) / 2
    assert Lp(QQ(3) / 2, RR, RR).conjugate_lebesgue_space().integrability_exponent() == 3
    assert Lp(1, RR, RR).conjugate_lebesgue_space().integrability_exponent() == oo
    assert Lp(oo, RR, RR).conjugate_lebesgue_space().integrability_exponent() == 1
    assert Lp(2, RR, RR).conjugate_lebesgue_space() is Lp(2, RR, RR)
    assert Lp(2, RR, RR).pairing_module() is Lp(2, RR, RR)


def test_only_L2_is_a_formed_module_and_every_Lp_is_a_real_vector_space() -> None:
    r"""``<f, g> = int f g`` is a form on ``L^2`` alone; ``L^p`` is a vector space for every ``p > 0``."""
    assert Lp(2, RR, RR) in FormModules(RR)
    assert Lp(1, RR, RR) not in FormModules(RR)
    assert Lp(3, RR, RR) in VectorSpaces(RR)
    assert Lp(QQ(1) / 2, RR, RR) in VectorSpaces(RR)
    assert Lp(2, RR, RR).quotient_by_null_functions() in VectorSpaces(RR)


def test_the_exponent_zero_defines_no_lebesgue_space() -> None:
    r"""``L^p`` is defined for ``p > 0``."""
    with pytest.raises(ValueError):
        Lp(0, RR, RR)


def test_pointwise_operations_on_square_integrable_maps() -> None:
    r"""``(f + f)(0) = 2`` and ``(3 f)(0) = 3`` for ``f = e^{-x^2}``, and ``f(1) = e^{-1}``."""
    space = Lp(2, RR, RR)
    f1(x) = exp(-x * x)
    gaussian = space(f1)

    assert gaussian(0) == 1
    assert gaussian(1) == exp(-1)
    assert (gaussian + gaussian)(0) == 2
    assert (3 * gaussian)(0) == 3


def test_sine_is_not_square_integrable() -> None:
    r"""``int sin^2 = oo`` over ``RR``: ``sin`` is not in ``L^2(RR)``."""
    space = Lp(2, RR, RR)
    f1(x) = sin(x)

    assert f1 not in space


def test_sine_is_not_integrable() -> None:
    r"""``int |sin| = oo`` over ``RR``: ``sin`` is not in ``L^1(RR)``."""
    space = Lp(1, RR, RR)
    f1(x) = sin(x)

    assert f1 not in space


def test_the_exponential_is_not_square_integrable() -> None:
    r"""``int_0^oo e^{2x} dx = oo``: ``e^x`` is not in ``L^2(RR)``."""
    space = Lp(2, RR, RR)
    f1(x) = exp(x)

    assert f1 not in space


def test_the_exponential_is_not_essentially_bounded() -> None:
    r"""``e^x`` is unbounded on every ``[N, oo)``, so it is not in ``L^oo(RR)``."""
    space = Lp(oo, RR, RR)
    f1(x) = exp(x)

    assert f1 not in space


def test_the_classes_of_two_maps_differing_on_a_positive_measure_set_differ() -> None:
    r"""``e^{-|x|}`` and ``e^{-x^2}`` differ on ``(0, 1)``, so they are not equal almost everywhere."""
    space = Lp(1, RR, RR)
    f1(x) = exp(-abs(x))
    f2(x) = exp(-x * x)
    laplace = space(f1)
    gaussian = space(f2)
    classes = space.quotient_by_null_functions()

    assert ask(space.almost_everywhere_equal(laplace, gaussian)) is False
    assert (classes(laplace) == classes(gaussian)) is False


def test_almost_everywhere_equality_is_reflexive() -> None:
    r"""``f = f`` everywhere, hence almost everywhere; its class equals itself in ``L^1``."""
    space = Lp(1, RR, RR)
    f1(x) = exp(-abs(x))
    laplace = space(f1)
    classes = space.quotient_by_null_functions()

    assert ask(space.almost_everywhere_equal(laplace, laplace)) is True
    assert (classes(laplace) == classes(laplace)) is True


def test_the_cauchy_density_integrates_to_pi() -> None:
    r"""``int dx / (1 + x^2) = [arctan x] = pi``."""
    space = Lp(1, RR, RR)
    f1(x) = 1 / (1 + x * x)

    assert space.integration_morphism()(space(f1)) == pi


def test_the_squared_l2_norm_of_the_gaussian_is_root_pi_over_two() -> None:
    r"""``<e^{-x^2}, e^{-x^2}> = int e^{-2x^2} dx = sqrt(pi/2)`` by the substitution ``x = u/sqrt 2``."""
    space = Lp(2, RR, RR)
    f1(x) = exp(-x * x)
    gaussian = space(f1)

    assert space.b(gaussian, gaussian) == sqrt(pi / 2)
