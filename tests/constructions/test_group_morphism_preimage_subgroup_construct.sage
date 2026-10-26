r"""Inverse image of the identity subgroup under C4 -> C2 has two elements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_reduction_c4_to_c2_preimage_of_identity_subgroup_has_order_two() -> None:
    four = Groups.C(4)
    two = Groups.C(2)
    reduction = four.Mor(two)(
        {four.group_generators()[0]: two.group_generators()[0]}
    )
    identity_subgroup = two.one().cyclic_subgroup()
    preimage = reduction.preimage_subgroup(identity_subgroup)

    assert preimage.cardinality() == cardinal(2)
