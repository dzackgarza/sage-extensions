r"""A cyclic group carries its selected generator as framing data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_six_has_a_selected_group_generator() -> None:
    group = Groups.C(6)
    generator = group.group_generator()
    framing = group.framing_morphism()

    assert group in CyclicGroups()
    assert framing.codomain() is group
    assert generator in group
    assert generator.order() == 6

