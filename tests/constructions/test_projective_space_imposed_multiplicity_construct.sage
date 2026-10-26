r"""Projective space constructs the linear system with a coordinate-point multiplicity condition."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_cubics_double_at_coordinate_point_form_p6() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    system = plane.imposed_multiplicity_linear_system(3, 0, 2)

    assert system in ImposedMultiplicityLinearSystems(QQ)
    assert system.constrained_section_space().dimension() == 7
    assert system.projective_dimension() == 6
