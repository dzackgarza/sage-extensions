r"""Isotropic flags under finite-preimage subgroups (not character kernels).

O(U) has four elements {I,-I,s,-s}, with s exchanging the two
primitive isotropic lines. The congruence kernel Γ(3) is trivial:
the full O(U)-orbit of its two lines splits into exactly two Γ(3)
classes; the empty transporter between them is an exact finite
quotient obstruction, not a missing arithmetic-group generator.
"""
from sage_extensions.all import *


def test_congruence_three_splits_primitive_null_line_flags():
    lattice = Lattices(ZZ)("U")
    e, f = tuple(lattice.module_generators())
    group = lattice.O()
    gamma = group.congruence_preimage(3)
    assert gamma.index() == 4
    complex_ = RationalIsotropicFlagComplex(gamma)
    flag_orbits = complex_.simplex_orbits(FlagType((1,)))
    assert flag_orbits.cardinality() == cardinal(2)
    flags = tuple(flag_orbits)
    assert all(flag.lattice() is lattice and int(flag.top().rank()) == 1 for flag in flags)
    assert all(gamma.isotropic_equivalence_witness(flag, flag, flag=True) in gamma for flag in flags)
    assert gamma.isotropic_equivalence_witness(flags[0], flags[1], flag=True) is None
    assert gamma.isotropic_equivalence_witness(flags[1], flags[0], flag=True) is None
    for flag in flags:
        stabilizer = tuple(complex_.stabilizer_generators(flag))
        assert all(g in gamma and
                   flag.top().inclusion().is_in_image(g(flag.isotropic_basis()[0]))
                   for g in stabilizer)
    line_keys = {
        tuple(abs(int(v.to_vector()(label))) for label in lattice.module_generating_set())
        for flag in flags for v in flag.isotropic_basis()
    }
    assert line_keys == {(1, 0), (0, 1)}
