r"""The hyperplane on projective plane has three homogeneous linear sections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_homogeneous_section_space_has_dimension_three() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    sections = plane.homogeneous_polynomial_section_space(plane.hyperplane_divisor())

    assert sections.dimension() == 3
    assert sections.module_rank() == 3
