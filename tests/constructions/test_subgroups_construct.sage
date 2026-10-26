r"""A point stabilizer in S4 is represented as a specified subgroup of S4."""

from sage_extensions.all import *  # noqa: F401,F403


def test_point_stabilizer_retains_its_supergroup_and_inclusion() -> None:
    group = Groups.S(4)
    stabilizer = Subgroups(group)(lambda g: g(1) == 1, "fixes the point 1")
    inclusion = stabilizer.inclusion()

    assert stabilizer in Subgroups(group)
    assert stabilizer.supergroup() is group
    assert stabilizer.order() == 6
    assert stabilizer.is_isomorphic_to(Groups.S(3))
    assert inclusion.domain() is stabilizer
    assert inclusion.codomain() is group
    assert inclusion.is_injective()
    assert inclusion(stabilizer.one()) == group.one()

