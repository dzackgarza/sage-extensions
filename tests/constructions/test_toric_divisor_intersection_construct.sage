r"""The hyperplane on projective plane has self-intersection one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_intersection_is_one() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    hyperplane = plane.hyperplane_divisor()

    assert plane.divisor_intersection(hyperplane, hyperplane) == 1
