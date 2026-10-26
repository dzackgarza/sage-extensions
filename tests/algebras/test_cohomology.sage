r"""De Rham cohomology of the dual numbers over ``GF(2)``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_x_dx_is_a_nonzero_de_rham_class_of_gf2_dual_numbers_with_zero_square() -> None:
    r"""For ``A = GF(2)[x]/(x^2)``: ``dx = d(x)`` is a nonzero exact 1-form; ``x dx``
    is closed (every 1-form is, as ``Ω^2_A = 0``) and not exact, since the exact
    forms are ``d(a + bx) = b dx``; its class does not depend on the
    representative (``[x dx + dx] = [x dx]``) and squares to zero.

    Derivation: ``Ω^1_A = A dx / (2x dx) = A dx`` in characteristic 2.
    """
    polynomials = GF(2)["x"]
    x = polynomials.gen()
    algebra = polynomials.quotient(polynomials.ideal([x**2]))
    xbar = algebra(x)
    de_rham = algebra.de_rham_algebra()
    d = de_rham.differential()
    dx = d(de_rham(xbar))
    cohomology = de_rham.cohomology_algebra()
    alpha = cohomology.class_of(de_rham(xbar) * dx)

    assert dx != de_rham.zero()
    assert cohomology.class_of(dx) == cohomology.zero()
    assert alpha != cohomology.zero()
    assert cohomology.class_of(de_rham(xbar) * dx + dx) == alpha
    assert cohomology.one() * alpha == alpha
    assert alpha * alpha == cohomology.zero()
