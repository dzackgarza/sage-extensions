r"""The hyperplane class on toric projective plane has self-intersection one."""

from sage_extensions.all import *  # noqa: F401,F403


def _projective_plane_and_hyperplane():
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    return plane, plane.hyperplane_divisor()


def test_projective_plane_hyperplane_self_intersection_is_one() -> None:
    plane, hyperplane = _projective_plane_and_hyperplane()

    assert plane.ample_divisor_self_intersection(hyperplane) == 1


def test_projective_plane_hyperplane_intersection_is_one() -> None:
    plane, hyperplane = _projective_plane_and_hyperplane()

    assert plane.ample_divisor_intersection(hyperplane, hyperplane) == 1
