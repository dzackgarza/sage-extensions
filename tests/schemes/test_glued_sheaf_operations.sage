r"""Kernels and cokernels of maps of quasi-coherent sheaves on ``P^1``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_kernel_of_x_y_from_o_squared_to_o_1_on_p1_is_o_minus_1() -> None:
    r"""The Euler sequence ``0 -> O(-1) -> O^2 --(x, y)--> O(1) -> 0`` on ``P^1_QQ``.

    ``(x, y)`` is surjective since ``x`` and ``y`` have no common zero, and its kernel
    is the line bundle ``O(-1)``, generated on ``D_+(x)`` by ``(y/x, -1)``; so
    ``h^0 = h^1 = 0`` for the kernel (Hartshorne II.8.13 and III.5.1).  A map
    that kills one summand, ``(x, 0)``, has kernel ``O`` and cokernel the skyscraper
    ``O_{V(x)}(1)`` of length 1.
    """
    P1 = Schemes(QQ).projective_space(1, names=("x", "y"))
    x, y = P1.coordinate_ring().algebra_generator("x"), P1.coordinate_ring().algebra_generator("y")
    O = P1.structure_sheaf()
    E = O.direct_sum(O)
    euler = E.Mor(P1.O(1))((x, y))
    K = euler.kernel()

    assert euler.is_surjective()
    assert euler.cokernel().is_zero()
    assert K.rank() == 1
    assert K.is_isomorphic(P1.O(-1))
    assert K.cohomology(0).dimension() == 0
    assert K.cohomology(1).dimension() == 0

    partial = E.Mor(P1.O(1))((x, 0 * y))
    assert partial.kernel().is_isomorphic(O)
    assert partial.cokernel().support().dimension() == 0
    assert partial.cokernel().global_sections().dimension() == 1
