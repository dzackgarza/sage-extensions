r"""Coordinate pointwise stabilizers in O(Z^3) have their signed-permutation orders."""

from sage_extensions.all import *

import pytest


@pytest.mark.parametrize("rank, expected_order", ((0, 48), (2, 2), (3, 1)))
def test_pointwise_coordinate_stabilizers_have_the_full_generating_group(rank, expected_order):
    r"""Fixing k coordinate axes pointwise leaves signed permutations on the other 3-k axes."""
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    basis = tuple(lattice.module_generators())
    selected = lattice.subobject_on(basis[:int(rank)])
    stabilizer = lattice.O().pointwise_stabilizer(selected.inclusion())
    group_generators = tuple(stabilizer.group_generators())

    assert stabilizer.cardinality() == cardinal(expected_order)
    assert all(
        generator(point) == point
        for generator in group_generators for point in basis[:int(rank)]
    )
    assert all(
        lattice.b(generator(left), generator(right)) == lattice.b(left, right)
        for generator in group_generators for left in basis for right in basis
    )
