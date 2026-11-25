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


def test_rank_two_flag_apex_stabilizer_retains_all_marking_legs():
    # In U + U, the maximal primitive null plane spanned by e,u has
    # dual basis f,v. A stabilizer of Ze < Ze+Zu must preserve both
    # terms. In particular the integral Levi shear u -> u+e,
    # f -> f-v is in it, whereas exchanging the two U summands is not.
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e, f, u, v = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    group = lattice.O()
    flag = lattice.isotropic_flag(e, u)
    stabilizer = group.stabilizer(flag)
    shear = group(dict(zip(labels, (e, f-v, u+e, v), strict=True)))
    exchange = group(dict(zip(labels, (u, v, e, f), strict=True)))
    assert shear in stabilizer and exchange not in stabilizer
    family = tuple(stabilizer.group_generators())
    assert family
    assert all(g in group and g in stabilizer for g in family)
    assert all(term.stabilizes(g) for g in family for term in flag.terms())


def test_discriminant_preimage_splits_null_line_flags_in_u_scaled_by_two():
    # O(U(2)) = {1,-1,s,-s}, where s exchanges the two primitive
    # null lines. Its discriminant group is (Z/2)^2: -1 acts
    # trivially and s exchanges its two standard classes.
    # The discriminant kernel therefore fixes both null lines.
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    group = lattice.O()
    rho = lattice.discriminant_representation()
    gamma = group.discriminant_preimage(rho.codomain().subgroup(()))
    assert gamma.contains_character_kernel()
    assert gamma.index() == 2
    flags = tuple(gamma.isotropic_orbit_representatives(1, flag=True))
    assert len(flags) == 2
    assert all(flag.lattice() is lattice for flag in flags)
    assert gamma.isotropic_equivalence_witness(flags[0], flags[1], flag=True) is None
    assert gamma.isotropic_equivalence_witness(flags[1], flags[0], flag=True) is None
