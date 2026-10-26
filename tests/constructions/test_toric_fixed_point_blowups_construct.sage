r"""Blowing up a torus-fixed point of P^2 gives the first Hirzebruch surface."""

from sage_extensions.all import *  # noqa: F401,F403


def test_toric_fixed_point_blowup_of_projective_plane() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cone = next(
        cone
        for cone in plane.fan().maximal_cones()
        if cone.rays()[0] + cone.rays()[1] == plane.cocharacter_lattice()((-1, 0))
    )
    blowup = plane.toric_fixed_point_blowup(cone)

    assert blowup in ToricFixedPointBlowups(QQ)
    assert blowup in ProperSurfaces(QQ)
    assert blowup in ProjectiveSurfaces(QQ)
    assert blowup.blowup_source() is plane
    assert blowup.source_picard_group().picard_scheme() is plane
    assert blowup.blowup_center_cone() == cone
    assert blowup.blowup_morphism().codomain() is plane
    assert blowup.is_hirzebruch_surface(1)
    assert blowup.exceptional_self_intersection() == -1
    assert DelPezzoSurfaces(blowup.scheme_base_ring())(blowup).del_pezzo_degree() == 8
