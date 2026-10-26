r"""All conic sections of P^2 form a five-dimensional projective linear system."""

from sage_extensions.all import *  # noqa: F401,F403


def test_complete_conic_sections_as_a_projective_linear_system() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(2)
    system = bundle.linear_system()

    assert system in ProjectiveLinearSystems(QQ)
    assert system.line_bundle() is bundle
    assert system.ambient_section_space().dimension() == 6
    assert system.selected_section_space().dimension() == 6
    assert system.projective_dimension() == 5
    assert system.is_basepoint_free()
