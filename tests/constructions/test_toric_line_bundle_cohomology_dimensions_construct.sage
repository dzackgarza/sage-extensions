r"""The hyperplane bundle on projective plane has cohomology dimensions 3, 0, 0."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_cohomology_dimensions() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    dimensions = plane.line_bundle_cohomology_dimensions(plane.hyperplane_divisor())

    assert dimensions[0] == 3
    assert dimensions[1] == 0
    assert dimensions[2] == 0
