r"""Finite symmetric groups lie in the finitely-presented refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_symmetric_three_is_finitely_presented() -> None:
    group = Groups.S(3)

    assert group in FinitelyPresentedGroups()
    assert group.is_finitely_presented()
    assert group.presentation() in GroupsWithChosenFinitePresentation()

