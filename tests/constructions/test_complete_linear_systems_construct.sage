r"""The complete linear system of a line on P^2 is a projective plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_complete_linear_system_of_a_line_on_projective_plane() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    system = plane.complete_linear_system(divisor)

    assert system in CompleteLinearSystems(QQ)
    assert system.linear_system_scheme() is plane
    assert system.linear_system_divisor() == divisor
    assert system.section_space().dimension() == 3
    assert system.projective_dimension() == 2
