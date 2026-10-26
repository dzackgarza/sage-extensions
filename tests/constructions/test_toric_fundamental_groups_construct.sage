r"""The complex projective plane is simply connected at a torus-fixed point."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_has_trivial_toric_fundamental_group() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    plane = fans.projective_space_fan().toric_variety(QQ)
    cone = next(iter(plane.fan().maximal_cones()))
    pi_one = plane.fundamental_group(cone)

    assert pi_one in ToricFundamentalGroups()
    assert pi_one.cardinality() == 1
    assert pi_one.base_point_cone() == cone
    assert pi_one.topological_scheme() is plane
