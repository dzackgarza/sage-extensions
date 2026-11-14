r"""Colon and saturation in a quotient by a univariate cover.

The ideal owner computes a quotient's colon on preimages: ``(I : J)~ = (I~ : J~)``
and ``(I : J^infinity)~ = (I~ : J~^infinity)``, in the covering polynomial ring.
For a multivariate cover the cover ideal answers ``quotient`` itself; for a
*univariate* one the ring is a PID whose Sage ideal class has no
``syzygy_module``, and the preimage construction needs one.

Sage owns that module over a PID: the syzygies of ``(a_1, ..., a_n)`` are the
kernel of ``(x_1, ..., x_n) |-> sum x_i a_i``, and its finitely generated module
over a PID computes that kernel from the one-column matrix of generators.  These
tests state the two decisions that rest on it, in ``(Z/5)[t]/(t^2)``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _square_zero():
    r"""``(Z/5)[t]/(t^2)`` and the class of ``t``."""
    field = GF(5)
    polynomial = field.polynomial_ring("t")
    t = polynomial.algebra_generator("t")
    quotient = polynomial.quotient_ring(t**2)
    return quotient, quotient.quotient_map()(t)


def test_the_annihilator_of_t_in_the_square_zero_ring_is_t() -> None:
    r"""``(0 : (t)) = (t)``: every ``a`` with ``a t = 0`` is a multiple of ``t``."""
    quotient, tbar = _square_zero()
    annihilator = quotient.ideal(quotient.zero()).colon(quotient.ideal(tbar))

    assert annihilator == quotient.ideal(tbar)
    assert tbar * tbar == quotient.zero()
    assert tbar != quotient.zero()


def test_the_saturation_of_t_by_t_is_the_unit_ideal() -> None:
    r"""``(t) : (t)^infinity = A``: ``t^2 = 0``, so ``(t)^2`` is already zero."""
    quotient, tbar = _square_zero()
    saturated = quotient.ideal(tbar).ideal_saturation(quotient.ideal(tbar))

    assert saturated == quotient.ideal(quotient.one())


def test_a_multivariate_cover_still_answers_its_own_colon() -> None:
    r"""The univariate route is a fallback: ``(x) : (x)`` in ``QQ[x,y]/(xy)`` is ``A``."""
    presentation = QQ.polynomial_ring(("x", "y"))
    x, y = presentation.algebra_generators()
    axes = presentation.quotient_by_relations((x * y,))
    xbar = axes.algebra_generator("x")

    ybar = axes.algebra_generator("y")

    # ``a x = 0`` in ``QQ[x,y]/(xy)`` exactly when ``a`` is a multiple of ``y``.
    assert axes.ideal(axes.zero()).colon(axes.ideal(xbar)) == axes.ideal(ybar)
    assert axes.ideal(xbar).colon(axes.ideal(xbar)) == axes.ideal(axes.one())
