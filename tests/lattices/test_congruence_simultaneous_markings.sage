r"""A single exact finite-image action for simultaneous congruence markings (#42).

For U=Ze+Zf, O(U)={1,-1,s,-s}, s(e)=f. Modulo six,
Stab(e+f)={1,s} as *vectors*, while Stab(Z e)={1,-1} as
*submodules*. Their intersection is the identity, and its Schreier
family and image-lift data belong to that actual subgroup of O(U).
"""

from sage_extensions.all import *


def _data():
    plane = Lattices(ZZ)("U")
    group = plane.O()
    e, f = tuple(plane.module_generators())
    labels = tuple(plane.module_generating_set())
    negative = group({label: -plane.module_generator(label) for label in labels})
    swap = group(dict(zip(labels, (f, e), strict=True)))
    return plane, group, e, f, negative, swap


def test_joint_vector_and_line_stabilizer_is_the_trivial_integral_subgroup():
    plane, group, e, f, negative, swap = _data()
    axis = plane.subobject_on((e,)).inclusion()
    joint = group.congruence_marking_stabilizer(6, vectors=(e+f,), sublattices=(axis,))
    assert joint.cardinality() == cardinal(1)
    assert group.one() in joint
    assert negative not in joint and swap not in joint and negative*swap not in joint
    assert all(generator == group.one() for generator in joint.group_generators())
    assert group.congruence_vector_stabilizer(6, e+f).cardinality() == cardinal(2)
    assert group.congruence_sublattice_stabilizer(6, axis).cardinality() == cardinal(2)


def test_two_simultaneously_preserved_axes_are_not_individually_fixed_vectors():
    plane, group, e, f, negative, swap = _data()
    axes = tuple(plane.subobject_on((vector,)).inclusion() for vector in (e, f))
    joint = group.congruence_marking_stabilizer(6, sublattices=axes)
    assert joint.cardinality() == cardinal(2)
    assert group.one() in joint and negative in joint
    assert swap not in joint
    assert all(generator in joint for generator in joint.group_generators())


def test_finite_index_sublattice_is_its_exact_mod_six_full_preimage():
    plane, group, e, f, negative, swap = _data()
    # M=2Ze+3Zf contains 6U, so Stab(M/6U) = Stab(M) exactly.
    embedding = plane.subobject_on((2*e,3*f)).inclusion()
    finite_level = group.congruence_sublattice_stabilizer(6, embedding)
    integral = group.setwise_stabilizer(embedding)
    assert all((g in finite_level) == (g in integral) for g in
               (group.one(), negative, swap, negative*swap))
    assert finite_level.cardinality() == cardinal(2)


def test_joint_stabilizer_in_infinite_orthogonal_group_contains_true_shear():
    plane = Lattices(ZZ)("U")
    lattice = plane + plane
    group = lattice.O()
    e, f, u, v = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    shear = group(dict(zip(labels, (e, f-v, u+e, v), strict=True)))
    negative = group({label: -lattice.module_generator(label) for label in labels})
    swap = group(dict(zip(labels, (f, e, u, v), strict=True)))
    top = lattice.primitive_isotropic_subobject(e,u).inclusion()
    # At level two the global negation acts trivially on every residue;
    # the shear remains nontrivial integrally but preserves both markings.
    joint = group.congruence_marking_stabilizer(2, vectors=(e,), sublattices=(top,))
    assert shear in joint and negative in joint
    assert swap not in joint
    assert shear(u) != u and shear(e) == e


def test_empty_and_unit_level_markings_stabilize_the_entire_group():
    plane, group, e, _f, _negative, _swap = _data()
    assert group.congruence_marking_stabilizer(6) is group
    assert group.congruence_marking_stabilizer(
        1, vectors=(e,), sublattices=(plane.subobject_on((e,)).inclusion(),)
    ) is group
