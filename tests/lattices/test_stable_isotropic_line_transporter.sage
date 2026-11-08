r"""Stable-component Eichler transvections give exact null-line transporters.

In 2U(2)+A2(-1), the transvection along the first null basis vector
and an A2 root carries the opposite null line into the same arithmetic
orbit. The subgroup transporter must supply its full integral witness.
"""

from sage_extensions.all import *


def test_stable_component_line_transporter_matches_an_eichler_transvection():
    hyperbolic = Lattices(ZZ)("U").twist(2)
    lattice = hyperbolic + hyperbolic + Lattices(ZZ)("A2").twist(-1)
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
