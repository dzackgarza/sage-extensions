r"""Arithmetic on a quotient takes its scalars along the maps it retains.

A quotient ``R[x]/I`` is an ``R``-algebra through its source map, and the rings
below ``R`` reach it through the same tower: ``ZZ -> QQ -> QQ[x] -> QQ[x]/(x^2)``.
So ``a + 3`` is the class of ``a + 3`` — the numeral read at the bottom of the
tower and carried up — and not a Python refusal.  What is *not* claimed here is
the module frame of such a quotient, which is a different operation.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def _dual_numbers_over_qq():
    r"""``QQ[x]/(x^2)`` and the class of ``x``."""
    polynomials = QQ["x"]
    algebra = polynomials.quotient_ring(polynomials.gen() ** 2)
    return algebra, algebra(polynomials.gen())


def _dual_numbers_over_f2():
    r"""``F_2[y]/(y^2)`` and the class of ``y``."""
    polynomials = GF(2)["y"]
    algebra = polynomials.quotient_ring(polynomials.gen() ** 2)
    return algebra, algebra(polynomials.gen())


def test_a_python_integer_is_a_scalar_of_the_quotient_in_both_orders() -> None:
    r"""``a + 3 == A(3) + a == 3 + a``, and subtraction reads ``-3`` the same way."""
    algebra, a = _dual_numbers_over_qq()

    assert a + 3 == algebra(3) + a
    assert 3 + a == a + 3
    assert a - 3 == a + algebra(-3)
    assert 3 - a == algebra(3) - a
    assert a + 3 != a


def test_the_tower_zz_to_qq_to_the_cover_to_the_quotient_is_what_carries_the_numeral() -> None:
    r"""``3`` reaches the quotient as ``ZZ -> QQ -> QQ[x] -> QQ[x]/(x^2)``.

    The numeral is the same element whichever ring of the tower states it, so
    the three spellings agree; the quotient's own element, the coefficient
    field's and the integer's are one scalar here.
    """
    algebra, a = _dual_numbers_over_qq()

    assert a + 3 == a + ZZ(3)
    assert a + 3 == a + QQ(3)
    assert a + QQ(1) / QQ(2) == a + algebra(QQ(1) / QQ(2))
    # ... and over a prime field, where the tower is ZZ -> F_2 -> F_2[y] -> A.
    prime_algebra, b = _dual_numbers_over_f2()
    assert b + 1 == b + GF(2).one()
    assert 1 + b == b + 1
    assert b - 1 == b + prime_algebra(-1)


def test_the_coefficient_ring_view_takes_the_same_scalars() -> None:
    r"""``3 + 5 v`` for ``v`` in the ``QQ``-algebra view of the same quotient."""
    algebra, a = _dual_numbers_over_qq()
    view = algebra.as_algebra_over(QQ)
    v = view(a)

    assert 3 + 5 * v == 5 * v + 3
    assert 3 + 5 * v == view(3) + 5 * v
    assert v - 3 == v + view(-3)


def test_a_non_scalar_operand_is_still_refused() -> None:
    r"""Reading an operand in the quotient does not accept what it is not."""
    algebra, a = _dual_numbers_over_qq()

    with pytest.raises(TypeError):
        a + "x"
