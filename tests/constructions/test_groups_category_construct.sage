r"""A cyclic group exhibits the group laws at the public group category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_six_is_a_group() -> None:
    group = Groups.C(6)
    element = group.group_generators()[0]

    assert group in Groups()
    assert element * element.inverse() == group.one()
    assert element.inverse() * element == group.one()
    assert element.cyclic_subgroup().order() == element.order()

