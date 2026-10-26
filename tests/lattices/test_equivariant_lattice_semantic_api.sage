r"""Invariant and coinvariant lattices of an isometry."""

from sage_extensions.all import *


def test_the_swap_on_U_has_invariant_lattice_of_norm_two_and_coinvariant_lattice_of_norm_minus_two() -> None:
    r"""On U with b(e, f) = 1 the swap e <-> f fixes Z(e + f), q(e + f) = 2,
    and negates Z(e - f), q(e - f) = -2.  Their sum has discriminant -4
    against -1 for U, so it has index 2 in U: the glue is nontrivial."""
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    swap = lattice.O()((f, e))

    invariant = swap.invariant_lattice()
    coinvariant = swap.coinvariant_lattice()

    assert invariant.is_isometric(Lattices(ZZ)([[2]]))
    assert coinvariant.is_isometric(Lattices(ZZ)([[-2]]))
    assert (invariant + coinvariant).discriminant_group().cardinality() == 4
    assert lattice.discriminant_group().cardinality() == 1
