r"""The maximal cones of the projective-plane fan give its three affine charts."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_affine_cover_has_one_chart_per_maximal_cone() -> None:
    fan = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan()
    plane = fan.toric_variety(QQ)
    cover = plane.affine_cover()

    assert cover.cardinality() == fan.maximal_cones().cardinality() == cardinal(3)
