r"""The free group on two generators realizes the finitely-generated refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_free_group_is_finitely_generated() -> None:
    group = Groups.Free(2)

    assert group in FinitelyGeneratedGroups()
    assert group.is_finitely_generated()
    assert group.group_generators().cardinality() == cardinal(2)

