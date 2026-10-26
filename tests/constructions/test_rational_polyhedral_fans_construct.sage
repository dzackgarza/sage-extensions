r"""The fan of the projective plane is a smooth complete rational polyhedral fan."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_fan_has_three_rays_and_seven_cones() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    fan = fans.projective_space_fan()

    assert fan in fans
    assert fan.dimension() == 2
    assert fan.rays().cardinality() == 3
    assert fan.maximal_cones().cardinality() == 3
    assert fan.cones(0).cardinality() == 1
    assert fan.cones(1).cardinality() == 3
    assert fan.cones(2).cardinality() == 3
    assert fan.cardinality() == 7
    assert fan.is_complete()
    assert fan.is_smooth()


def test_first_two_hirzebruch_fans_are_distinct() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    zeroth = fans.hirzebruch_surface_fan(0)
    first = fans.hirzebruch_surface_fan(1)

    assert zeroth.is_complete()
    assert zeroth.is_smooth()
    assert first.is_complete()
    assert first.is_smooth()
    assert not zeroth.is_isomorphic(first)
