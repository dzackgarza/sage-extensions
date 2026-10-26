r"""The swap involution of the hyperbolic plane ``U``: its eigenlattices and centralizer."""

from sage_extensions.all import *


def _hyperbolic_swap():
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    return lattice, lattice.O()({e: f, f: e})


def test_the_swap_on_U_has_invariant_lattice_of_norm_two_and_coinvariant_lattice_of_norm_minus_two() -> None:
    r"""``U^swap = ZZ(e+f)`` with ``(e+f)^2 = 2``; its complement is ``ZZ(e-f)`` with ``(e-f)^2 = -2``.

    Their sum has determinant ``-4 = -1 * 2^2``, so it has index 2 in ``U``.
    """
    _lattice, swap = _hyperbolic_swap()
    invariant = swap.invariant_lattice()
    coinvariant = swap.coinvariant_lattice()

    assert invariant.module_rank() == 1
    assert coinvariant.module_rank() == 1
    assert invariant.determinant() == 2
    assert coinvariant.determinant() == -2
    assert (invariant + coinvariant).determinant() == -4


def test_the_centralizer_of_the_swap_is_all_of_O_U_which_has_order_four() -> None:
    r"""``O(U) = {1, -1, swap, -swap}`` is abelian, so the swap's centralizer is ``O(U)``."""
    lattice, swap = _hyperbolic_swap()

    assert swap.centralizer_group().cardinality() == 4
    assert -lattice.O().one() in swap.centralizer_group()
