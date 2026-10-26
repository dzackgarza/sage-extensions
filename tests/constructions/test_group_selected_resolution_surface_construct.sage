r"""A finite cyclic group exposes its selected generator resolution coherently."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cyclic_group_selected_resolution_controls_generators_and_conjugation() -> None:
    group = Groups.C(6)
    resolution = group.selected_group_resolution()
    generator_map = group.group_generator_morphism()
    generator = group.group_generators()[0]
    conjugation = group.conjugation_morphism()

    assert group.has_selected_group_resolution()
    assert group.has_selected_finite_group_generating_set()
    assert resolution.target() is group
    assert group.number_of_group_generators() == cardinal(1)
    assert generator_map.codomain() is group
    assert conjugation(generator) == group.Aut().one()
