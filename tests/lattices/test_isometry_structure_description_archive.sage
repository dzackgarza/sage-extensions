r"""Archived finite-isometry structure descriptions at the live group owner."""


from sage_extensions.all import *


def test_rank_one_root_lattice_has_cyclic_order_two_orthogonal_group() -> None:
    lattice = Lattices(ZZ)("A1")

    assert lattice.O().structure_description() == "C2"
    assert lattice.O().cardinality() == 2



def test_the_orthogonal_group_of_U_is_the_klein_four_group() -> None:
    r"""``O(U) = {1, -1, swap, -swap}``: order 4, every element squares to the identity."""
    group = Lattices(ZZ)("U").O()

    assert group.cardinality() == 4
    assert all(element * element == group.one() for element in group)
