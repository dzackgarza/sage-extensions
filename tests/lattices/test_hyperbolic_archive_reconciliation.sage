r"""Vinberg's algorithm on the hyperbolic lattice ``U + A1``."""

from sage_extensions.all import *


def test_vinberg_algorithm_on_u_plus_a1_finds_the_2_3_infinity_triangle() -> None:
    r"""On ``U + A1`` (basis ``e, f, a``; ``b(e,f) = 1``, ``a^2 = -2``) with
    controlling vector ``e + f``, the roots orthogonal to it are ``a`` and
    ``e - f``, and the next root is ``f - a``.  The three simple roots have norm
    ``-2`` and pairwise products ``0, 1, 2`` up to sign, i.e. the angles
    ``pi/2, pi/3, 0``: the ``(2, 3, infinity)`` triangle.  Derived by hand; the
    normalized Gram determinant ``-1/4`` confirms hyperbolic finite volume.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    roots = lattice.vinberg_simple_roots()

    assert roots.cardinality() == 3
    assert all(lattice.b(root, root) == -2 for root in roots)
    products = sorted(abs(lattice.b(r, s)) for r in roots for s in roots if r != s)
    assert products == [0, 0, 1, 1, 2, 2]
