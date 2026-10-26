r"""The Horikawa family is the invariant (4,4) double-cover construction on P1 x P1."""

from sage_extensions.all import *  # noqa: F401,F403


def test_horikawa_family_has_the_expected_base_surface_and_line_bundles() -> None:
    family = HorikawaK3Family()
    surface = family.base_surface()

    assert surface in ProductProjectiveSpaces(family.base_ring())
    assert surface.factors().cardinality() == cardinal(2)
    assert family.branch_line_bundle() == surface.O(4, 4)
    assert family.cover_line_bundle() == surface.O(2, 2)


def test_horikawa_family_uses_the_diagonal_c2_action_on_the_base() -> None:
    family = HorikawaK3Family()

    assert family.base_action() == family.base_surface().c2_diagonal_sign_action(
        family.acting_group()
    )


def test_horikawa_default_branch_section_is_invariant() -> None:
    family = HorikawaK3Family()

    assert family.default_branch_section() in family.invariant_branch_sections()
