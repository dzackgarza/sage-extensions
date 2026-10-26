r"""The Horikawa family retains its two distinct C2 linearizations of the branch data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_horikawa_branch_linearization_is_one_of_the_two_selected_lifts() -> None:
    family = HorikawaK3Family()
    selected = family.branch_linearization()
    enriques = family.enriques_linearization()
    nikulin = family.nikulin_linearization()

    assert enriques != nikulin
    assert selected in (enriques, nikulin)
