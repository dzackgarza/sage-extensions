r"""The hyperplane divisor on projective plane has a three-dimensional section space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_section_space_has_dimension_three() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    sections = plane.divisor_section_space(plane.hyperplane_divisor())

    assert sections.dimension() == 3
    assert sections.module_rank() == 3
