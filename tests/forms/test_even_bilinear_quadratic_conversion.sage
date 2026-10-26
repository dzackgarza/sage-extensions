r"""Even symmetric bilinear forms and their integral quadratic refinements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_even_a2_has_the_integral_half_norm_quadratic_module() -> None:
    r"""``A2`` is even; ``q(x) = b(x, x)/2`` is integral, ``-1`` on the roots, and polarizes back to ``b``.

    In the negative-definite convention ``b(e_i, e_i) = -2`` and
    ``b(e1, e2) = 1``, so ``q(e1 + e2) = (-2 + 2 - 2)/2 = -1``.
    """
    lattice = Lattices(ZZ)("A2")
    e1, e2 = lattice.basis()
    quadratic = lattice.to_quadratic_module()
    f1, f2 = quadratic.basis()
    polarized = quadratic.associated_bilinear_module()
    g1, g2 = polarized.basis()

    assert lattice.is_even()
    assert quadratic.q(f1) == -1
    assert quadratic.q(f2) == -1
    assert quadratic.q(f1 + f2) == -1
    assert quadratic.q(f1 - f2) == -3
    assert polarized.b(g1, g1) == lattice.b(e1, e1)
    assert polarized.b(g1, g2) == lattice.b(e1, e2)
    assert polarized.b(g2, g2) == lattice.b(e2, e2)
    assert not Lattices(ZZ)([[1]]).is_even()
