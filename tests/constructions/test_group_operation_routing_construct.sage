r"""General group operations expose unsupported algorithms at their true owners."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_infinite_finitely_presented_abelianization_names_missing_route() -> None:
    group = Groups.Free(2)

    with pytest.raises(AssertionError, match="presentation-quotient route"):
        Groups().abelianization()(group)


def test_general_group_operations_do_not_silently_assume_gap_finiteness() -> None:
    group = Groups.Free(2)
    subgroups = group.subgroups()
    whole = group.predicate_subgroup(lambda _element: True, "the whole group")

    with pytest.raises(AssertionError, match="commutator subgroup.*defined for every group"):
        group.commutator_subgroup()
    with pytest.raises(AssertionError, match="center.*defined for every group"):
        group.center()
    assert subgroups in Sets()
    assert whole in subgroups
    assert whole.supergroup() is group
    with pytest.raises(AssertionError, match="defined for every pair of groups"):
        group.is_isomorphic_to(group)


def test_group_mor_cardinality_names_missing_nonfinite_algorithm() -> None:
    source = Groups.Free(1)
    target = Groups.C(2)

    with pytest.raises(AssertionError, match="cardinality of Mor"):
        source.Mor(target).cardinality()
