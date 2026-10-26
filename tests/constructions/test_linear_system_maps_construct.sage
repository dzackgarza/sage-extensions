r"""Linear systems expose their projectivizations, base loci, maps, and restrictions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_complete_line_system_projectivization_comparison() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    system = plane.complete_linear_system(plane.hyperplane_divisor())
    projectivization = system.quotient_projectivization().arrow().domain()
    comparison = system.quotient_projectivization_comparison()

    assert system.associated_morphism().codomain() is system
    assert comparison.forward().domain() is projectivization
    assert comparison.forward().codomain() is system
    assert comparison.backward().domain() is system
    assert comparison.backward().codomain() is projectivization


def test_complete_conic_system_exposes_selected_sections_and_map() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(2)
    system = bundle.linear_system()

    assert system.section_embedding().domain() is system.selected_section_space()
    assert system.section_embedding().codomain() is system.ambient_section_space()
    assert system.selected_sections().cardinality() == cardinal(6)
    assert system.base_locus().is_empty()
    assert system.domain_of_definition() is plane
    assert system.associated_morphism().domain() is plane
    assert system.associated_morphism().codomain() is system


def test_quadrics_restrict_to_a_projective_line() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    bundle = plane.O(2)
    system = bundle.linear_system()
    line = plane.closed_subscheme(plane.homogeneous_coordinate_ring()("x"))
    restriction = system.restriction_map(line)

    assert restriction.domain() is system.selected_section_space()
    assert restriction.domain().dimension() == 6
    assert restriction.codomain().dimension() == 3
    assert restriction.kernel().dimension() == 3


def test_imposed_double_point_retains_jet_evaluation() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((1, 0, 0))
    system = plane.O(3).imposed_multiplicity_linear_system(point, 2)
    evaluation = system.imposed_jet_evaluation()

    assert evaluation.domain() is system.ambient_section_space()
    assert evaluation.kernel() is system.constrained_section_space()
    assert evaluation.codomain().jet_order() == 2
    assert evaluation.codomain().jet_point() is point
