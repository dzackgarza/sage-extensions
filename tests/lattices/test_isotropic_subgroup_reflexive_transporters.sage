r"""A maximal coordinate null sublattice belongs to its own SO orbit in dU."""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("rank", (1, 2, 3, 4), ids=("U", "2U", "3U", "4U"))
def test_maximal_null_marking_has_an_exact_self_transporter_in_the_special_group(rank):
    hyperbolic = Lattices(ZZ)("U")
    lattice = hyperbolic
    for _ in range(rank - 1):
        lattice = lattice + hyperbolic
    basis = tuple(lattice.module_generators())
    null = lattice.primitive_isotropic_subobject(*basis[::2])
    group = lattice.SO()
    witness = group.isotropic_equivalence_witness(null, null)
    assert witness.domain() is lattice and witness.codomain() is lattice
    assert witness in group
    for action in (witness, ~witness):
        assert all(null.inclusion().is_in_image(action(point)) for point in basis[::2])
    assert all((~witness)(witness(point)) == point for point in basis)
    assert all(lattice.b(witness(x), witness(y)) == lattice.b(x, y) for x in basis for y in basis)
