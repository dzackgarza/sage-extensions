r"""The toric blowup of P^2 at a fixed point records its exceptional ray and del Pezzo status."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_fixed_point_blowup_predicates() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cone = next(
        cone
        for cone in plane.fan().maximal_cones()
        if cone.rays()[0] + cone.rays()[1]
        == plane.cocharacter_lattice()((-1, 0))
    )
    blowup = plane.toric_fixed_point_blowup(cone)

    assert blowup.exceptional_ray().rays()[0] == blowup.cocharacter_lattice()((-1, 0))
    assert blowup.is_toric_fixed_point_blowup()
    assert blowup.is_del_pezzo()
