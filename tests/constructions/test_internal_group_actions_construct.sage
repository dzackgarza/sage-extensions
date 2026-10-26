r"""The terminal object carries the canonical action of the terminal internal group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_terminal_internal_group_action_in_sets() -> None:
    group = InternalGroupObjects(Sets()).an_object()
    actions = InternalGroupActions(group)
    acted = actions.an_object()

    assert acted in actions
    assert acted.group_object() is group
    assert acted.underlying_object() in Sets()
    assert actions.Mor(acted, acted).identity().underlying_arrow() == (
        Sets().Mor(acted.underlying_object(), acted.underlying_object()).identity()
    )
