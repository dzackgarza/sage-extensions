r"""Stable-component Eichler transvections give exact null-line transporters.

In 2U(2)+A2 and its A2 sign variant, the transvection along the first
null basis vector and an A2 root carries the opposite null line into
the same arithmetic orbit. Each transporter supplies an integral witness.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("root_twist, signature", ((1, (2, 4)), (-1, (4, 2))), ids=("A2", "A2_twist_minus_one"))
def test_stable_component_line_transporter_matches_an_eichler_transvection(root_twist, signature):
    hyperbolic = Lattices(ZZ)("U").twist(2)
    lattice = hyperbolic + hyperbolic + Lattices(ZZ)("A2").twist(root_twist)
    assert tuple(map(int, lattice.signature_pair())) == tuple(map(int, signature))
    basis = tuple(lattice.module_generators())
    e, f, a, b, c, d = basis
    group = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    transvection = lattice.eichler_transvection(e, c)
    assert transvection in group
    source = lattice.primitive_isotropic_subobject(f)
    target = transvection.transport_isotropic_object(source)
    witness = group.isotropic_equivalence_witness(source, target)
    assert witness in group
    assert all(target.inclusion().is_in_image(witness(source.inclusion()(point)))
               for point in source.module_generators())
    assert all(source.inclusion().is_in_image((~witness)(target.inclusion()(point)))
               for point in target.module_generators())
    assert all((~witness)(witness(point)) == point for point in basis)
    assert all(lattice.b(witness(x), witness(y)) == lattice.b(x, y) for x in basis for y in basis)
