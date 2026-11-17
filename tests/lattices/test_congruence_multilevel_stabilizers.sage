r"""Finite-image simultaneous marked stabilizers at distinct congruence levels.

For O(U)={I,-I,s,-s}, s interchanges the two null axes. The
intersections below are derived by checking those four integral
isometries on the specified reductions. The actual joint image is
computed once at the least common multiple of the levels, not assumed
to be a product of its individual finite images.
"""

from sage_extensions.all import *


def _hyperbolic_data():
    plane = Lattices(ZZ)("U")
    e, f = tuple(plane.module_generators())
    group = plane.O()
    labels = tuple(plane.module_generating_set())
    negation = group({label: -plane.module_generator(label) for label in labels})
    exchange = group(dict(zip(labels, (f, e), strict=True)))
    return plane, group, e, f, negation, exchange


def test_mod_two_and_three_based_markings_have_trivial_joint_stabilizer():
    plane, group, e, _f, negation, exchange = _hyperbolic_data()
    gamma = group.congruence_multilevel_stabilizer(((2, (e,), ()), (3, (e,), ())))
    assert gamma.cardinality() == cardinal(1)
    assert group.one() in gamma
    assert negation not in gamma and exchange not in gamma
    assert all(generator == group.one() for generator in gamma.group_generators())
    assert group.congruence_vector_stabilizer(2, e).cardinality() == cardinal(2)
    assert group.congruence_vector_stabilizer(3, e).cardinality() == cardinal(1)


def test_mixed_mod_two_vector_and_mod_six_line_have_trivial_intersection():
    plane, group, e, f, negation, exchange = _hyperbolic_data()
    line = plane.subobject_on((e,)).inclusion()
    # e+f is fixed as a vector by {I,s} modulo 6, whereas Ze is fixed
    # as a submodule by {I,-I}. Imposing e (mod 2) does not add s.
    gamma = group.congruence_multilevel_stabilizer(((2, (e,), ()), (6, (e+f,), (line,))))
    assert gamma.cardinality() == cardinal(1)
    assert group.one() in gamma
    assert negation not in gamma and exchange not in gamma


def test_nonfree_submodule_and_diagonal_line_at_distinct_composite_levels():
    plane, group, e, f, negation, exchange = _hyperbolic_data()
    twice_axis = plane.subobject_on((2*e,)).inclusion()
    diagonal = plane.subobject_on((e+f,)).inclusion()
    # At level 4, 2e generates a nonfree order-two submodule stabilized
    # by {I,-I}; the diagonal submodule at level 6 is fixed by all O(U).
    gamma = group.congruence_multilevel_stabilizer(((4, (), (twice_axis,)), (6, (), (diagonal,))))
    assert gamma.cardinality() == cardinal(2)
    assert group.one() in gamma and negation in gamma
    assert exchange not in gamma
    assert all(generator in gamma for generator in gamma.group_generators())


def test_trivial_level_conditions_are_discarded_but_not_other_conditions():
    plane, group, e, _f, negation, exchange = _hyperbolic_data()
    axis = plane.subobject_on((e,)).inclusion()
    gamma = group.congruence_multilevel_stabilizer(((1, (e,), (axis,)), (6, (), (axis,))))
    assert gamma.cardinality() == cardinal(2)
    assert group.one() in gamma and negation in gamma and exchange not in gamma
    assert group.congruence_multilevel_stabilizer(((1, (e,), (axis,)),)) is group
    assert group.congruence_multilevel_stabilizer(()) is group
