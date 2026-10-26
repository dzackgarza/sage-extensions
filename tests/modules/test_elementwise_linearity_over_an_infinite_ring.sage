r"""Scalar-linearity of an elementwise map over an infinite ring.

The witness is Frobenius $a \mapsto a^3$ on $\mathbb F_3[x]/(x^3 - 1)$, read as
a module over $\mathbb F_3[x]$.  Cubing is additive in characteristic three and
fixes every constant, but it sends $x$ to $x^3 = 1$ while $x \cdot 1^3 = x$, so
it is not $\mathbb F_3[x]$-linear.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_frobenius_on_f3_x_mod_x3_minus_1_is_additive_but_not_x_linear() -> None:
    """Source: freshman's dream (a + b)^3 = a^3 + b^3 in characteristic 3; x^3 = 1 in the quotient."""
    R = GF(3)["x"]
    x = R.gen()
    Q = R.quotient_ring(R.ideal(x**3 - 1))
    M = Modules(R)(Q)
    xbar = Q(x)

    assert (xbar + 1) ** 3 == xbar**3 + 1
    assert xbar**3 == Q.one()
    assert xbar * Q.one() ** 3 != xbar**3

    with pytest.raises(ValueError):
        M.Mor(M).elementwise(lambda m: m**3)
