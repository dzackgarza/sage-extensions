r"""The natural numbers expose zero as their additive monoidal unit."""

from sage_extensions.all import *  # noqa: F401,F403


def test_natural_numbers_have_zero_as_additive_unit() -> None:
    unit = NN.monoidal_unit()
    n = NN(7)

    assert unit == NN(0)
    assert unit + n == n
    assert n + unit == n

