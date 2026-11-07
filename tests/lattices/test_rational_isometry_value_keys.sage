"""Equal rational basis actions give the same isometry cache key."""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("numerator, denominator", ((4, 2), (6, 3), (2, 4), (3, 6)))
def test_equivalent_fraction_actions_retrieve_the_same_isometry(numerator, denominator):
    lattice = Lattices(ZZ)([[0, 1], [1, 0]], module_generators=("east", "west"))
    space = lattice.base_change(ZZ.fraction_field_map())
    east, west = tuple(space.module_generators())
    east_label, west_label = tuple(space.module_generating_set())
    ring = space.base_ring()
    scalar = ring(numerator) / ring(denominator)
    reduced = ring(2) if numerator > denominator else ring.one() / ring(2)
    dilation = space.Isom(space)({
        east_label: space.scalar_multiple(scalar, east),
        west_label: space.scalar_multiple(ring.one() / scalar, west),
    })
    reconstructed = space.Isom(space)({
        east_label: space.scalar_multiple(reduced, east),
        west_label: space.scalar_multiple(ring.one() / reduced, west),
    })
    exchange = space.Isom(space)({east_label: west, west_label: east})

    assert dilation(east) == reconstructed(east) == space.scalar_multiple(reduced, east)
    assert dilation(west) == reconstructed(west) == space.scalar_multiple(ring.one() / reduced, west)
    assert dilation == reconstructed
    assert dilation != exchange
    table = {dilation: "dilation", exchange: "exchange"}
    assert table[reconstructed] == "dilation"
    assert table[exchange] == "exchange"
