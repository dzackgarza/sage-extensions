r"""Tensor and symmetric algebras of a finite abelian group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_generators_of_orders_two_and_three_multiply_to_zero() -> None:
    r"""For ``M = ZZ/2 x ⊕ ZZ/3 y``: in ``T(M)`` and ``Sym(M)``, ``2x = 3y = 0`` and
    ``xy = 0``, since ``xy`` lies in the image of ``ZZ/2 ⊗ ZZ/3 = 0``; but
    ``x^2 ≠ 0`` and ``y^2 ≠ 0`` (``ZZ/n ⊗ ZZ/n = ZZ/n``)."""
    free = Modules(ZZ).free_module(("x", "y"))
    ex, ey = free.module_generator("x"), free.module_generator("y")
    torsion = free.Mor(free)({ex: 2 * ex, ey: 3 * ey}).cokernel()

    for algebra in (torsion.tensor_algebra(), torsion.symmetric_algebra()):
        x, y = algebra.degree_one_generator(0), algebra.degree_one_generator(1)
        assert 2 * x == algebra.zero()
        assert 3 * y == algebra.zero()
        assert x != algebra.zero()
        assert x * y == algebra.zero()
        assert x * x != algebra.zero()
        assert y * y != algebra.zero()
