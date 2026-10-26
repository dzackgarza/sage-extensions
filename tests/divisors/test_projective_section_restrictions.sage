r"""Projective restriction maps use the exact image on general closed subschemes."""

from sage_extensions.all import *


def _plane_line_and_sections():
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    bundle = plane.O(1)
    sections = bundle.global_sections()
    ring = sections.homogeneous_coordinate_ring()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    z = ring.algebra_generator("z")
    line = plane.closed_subscheme(x + y)
    return plane, bundle, sections, line, x, y, z


def test_restriction_to_noncoordinate_line_has_exact_two_dimensional_image() -> None:
    _plane, bundle, sections, line, x, y, _z = _plane_line_and_sections()
    restriction = bundle.restriction_map(line)
    relation = sections.module_generator(x) + sections.module_generator(y)

    assert restriction.domain() is sections
    assert restriction.codomain().dimension() == 2
    assert restriction.kernel().dimension() == 1
    assert restriction(relation) == restriction.codomain().zero()
    assert restriction.closed_subscheme() is line
    assert restriction.line_bundle() is bundle
    assert restriction.restriction_image_inclusion().domain() is restriction.codomain()
    quotient = restriction.coordinate_quotient()
    assert quotient.presentation_ring() is sections.homogeneous_coordinate_ring()
    assert quotient(x + y) == quotient.zero()


def test_selected_linear_system_restriction_corestricts_to_its_actual_image() -> None:
    _plane, bundle, sections, line, x, y, z = _plane_line_and_sections()
    relation = sections.module_generator(x) + sections.module_generator(y)
    surviving = sections.module_generator(z)
    system = bundle.linear_system((relation, surviving))

    restriction = system.restriction_map(line)
    selected_labels = tuple(system.selected_section_space().module_generating_set())
    killed = system.selected_section_space().module_generator(selected_labels[0])
    live = system.selected_section_space().module_generator(selected_labels[1])

    assert restriction.domain() is system.selected_section_space()
    assert restriction.codomain().dimension() == 1
    assert restriction.kernel().dimension() == 1
    assert restriction(killed) == restriction.codomain().zero()
    assert restriction(live) != restriction.codomain().zero()
