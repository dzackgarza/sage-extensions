"""Generated signed-pair permutations admit their words and exclude a shear."""

from sage_extensions.all import *


def test_generated_subgroup_membership_respects_its_full_finite_group():
    lattice = Lattices(ZZ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    space = lattice.base_change(ZZ.fraction_field_map())
    labels = tuple(space.module_generating_set())
    e, f, x, y = tuple(space.module_generators())
    exchange = space.Isom(space)(dict(zip(labels, (x, y, e, f), strict=True)))
    sign = space.Isom(space)(dict(zip(labels, (-e, -f, x, y), strict=True)))
    group = space.O().subgroup((exchange, sign))
    ring = space.base_ring()
    unit = ring(2) / ring(2)
    rebuilt = space.Isom(space)({
        label: space.scalar_multiple(unit, image)
        for label, image in zip(labels, (x, y, e, f), strict=True)
    })
    shear = space.Isom(space)(dict(zip(labels, (e, f - y, x + e, y), strict=True)))

    assert group.membership_decision(exchange) is True
    assert group.membership_decision(rebuilt) is True
    assert group.membership_decision(~exchange) is True
    assert group.membership_decision(exchange * sign) is True
    assert group.membership_decision(shear) is False
