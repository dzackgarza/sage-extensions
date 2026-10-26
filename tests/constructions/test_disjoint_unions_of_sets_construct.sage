r"""Disjoint unions of sets are the coproduct objects with tagged summands."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_finite_sets_form_a_disjoint_union_with_tagged_elements() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    union = Sets().coproduct((two, three))
    point = union.injection(1)(three(2))

    assert union in DisjointUnionsOfSets()
    assert union.cardinality() == cardinal(5)
    assert point.summand_index() == 1
    assert point.summand_element() == three(2)
