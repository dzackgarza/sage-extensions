r"""A toric divisor class is its image under the class-group projection."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_class_is_the_class_group_projection() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    hyperplane = plane.hyperplane_divisor()

    assert plane.divisor_class(hyperplane) == plane.class_group_projection()(hyperplane)
