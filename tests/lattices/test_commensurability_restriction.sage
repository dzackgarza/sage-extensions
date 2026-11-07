r"""Restriction to an integral module requires equality, not containment."""

import pytest

from sage_extensions.all import *


def test_reference_restriction_and_residue_action_have_their_actual_inverse():
    plane = Lattices(QQ)([[0, 1], [1, 0]])
    labels = tuple(plane.module_generating_set())
    basis = tuple(plane.module_generator(label) for label in labels)
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    half = QQ(1) / QQ(2)
    reference = space.subobject_on([space(half * point) for point in basis])
    swap = plane.Aut()(dict(zip(labels, reversed(basis))))
    group = plane.Aut().subgroup((swap,))
    finite = IntegralStructureAction(group, reference.inclusion()).finite_quotient(3)
    restricted = finite.restricted_automorphism(swap)
    inverse = ~restricted
    projection = finite.quotient_projection()
    residue = finite.quotient_automorphism(swap)
    for point in reference.inclusion().domain().module_generators():
        assert inverse(restricted(point)) == point
        assert reference.inclusion()(restricted(point)).underlying_element() == swap(reference.inclusion()(point).underlying_element())
        assert residue(projection(point)) == projection(restricted(point))
        assert residue(residue(projection(point))) == projection(point)


def test_proper_containment_does_not_define_a_reference_automorphism():
    plane = Lattices(QQ)([[0, 1], [1, 0]])
    labels = tuple(plane.module_generating_set())
    first, second = tuple(plane.module_generator(label) for label in labels)
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    reference = space.subobject_on([space(first)])
    scaling = plane.Aut()({labels[0]: 2 * first, labels[1]: (QQ(1) / QQ(2)) * second})
    group = plane.Aut().subgroup((scaling,))
    finite = IntegralStructureAction(group, reference.inclusion()).finite_quotient(2)
    with pytest.raises(ValueError):
        finite.restricted_automorphism(scaling)


def test_two_index_two_lattices_have_their_exact_finite_orbit_and_transporter():
    plane = Lattices(QQ)([[0, 1], [1, 0]])
    labels = tuple(plane.module_generating_set())
    first, second = tuple(plane.module_generators())
    space = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(plane)
    reference = space.subobject_on([space(first), space(second)])
    source = space.subobject_on([space(2 * first), space(second)])
    target = space.subobject_on([space(first), space(2 * second)])
    swap = plane.Aut()({labels[0]: second, labels[1]: first})
    group = plane.Aut().subgroup((swap,))
    action = IntegralStructureAction(group, source.inclusion()).with_stable_containing_bound(reference.inclusion())
    finite = action.finite_representation()
    orbit = finite.orbit_submodules()
    assert finite.g_set().cardinality() == 2
    assert all(submodule.cardinality() == 2 for submodule in orbit)
    assert all(submodule.inclusion().codomain() is action.finite_module() for submodule in orbit)
    witness = action.transporter(target.inclusion())
    assert witness(first) == second and witness(second) == first
    assert (~witness)(witness(first)) == first
    outside = space.subobject_on([space((QQ(1) / QQ(2)) * first), space(second)])
    too_small = space.subobject_on([space(4 * first), space(second)])
    assert action.transporter(outside.inclusion()) is None
    assert action.transporter(too_small.inclusion()) is None
