r"""The Horikawa branch sections form the 25-dimensional C2-representation of O(4,4)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_horikawa_branch_section_space_and_group_module_have_dimension_twenty_five() -> None:
    family = HorikawaK3Family()

    assert family.branch_section_space().dimension() == 25
    assert family.branch_group_module().module_rank() == cardinal(25)


def test_horikawa_branch_sections_split_into_invariant_and_anti_invariant_parts() -> None:
    family = HorikawaK3Family()
    invariant = family.invariant_branch_sections()
    anti_invariant = family.anti_invariant_branch_sections()
    decomposition = family.branch_isotypic_decomposition()

    assert invariant.module_rank() + anti_invariant.module_rank() == cardinal(25)
    assert decomposition.trivial_component() is invariant
    assert decomposition.nontrivial_components().cardinality() == cardinal(1)


def test_horikawa_base_surface_has_two_factor_labels() -> None:
    family = HorikawaK3Family()

    assert family.factor_labels().cardinality() == cardinal(2)
