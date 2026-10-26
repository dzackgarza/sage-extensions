r"""The hyperplane divisor on projective plane is ample and basepoint free."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_is_ample() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.is_ample(plane.hyperplane_divisor())


def test_projective_plane_hyperplane_is_basepoint_free() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.is_basepoint_free(plane.hyperplane_divisor())
