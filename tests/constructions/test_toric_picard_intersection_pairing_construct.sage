r"""The hyperplane class on projective plane has Picard self-intersection one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_picard_hyperplane_has_square_one() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    hyperplane_class = plane.torus_invariant_cartier_class_projection()(
        plane.hyperplane_divisor()
    )
    pairing = plane.picard_intersection_pairing()

    assert pairing(hyperplane_class, hyperplane_class) == 1
