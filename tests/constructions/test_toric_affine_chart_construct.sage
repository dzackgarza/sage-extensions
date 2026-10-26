r"""A maximal cone of the projective-plane fan gives an affine-plane chart."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_maximal_cone_chart_is_an_affine_plane() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    fan = fans.projective_space_fan()
    plane = fan.toric_variety(QQ)
    cone = fan.maximal_cones()[0]
    chart = plane.affine_chart(cone)

    assert chart in AffineSchemes(QQ)
    assert chart.relative_dimension() == 2
    assert chart.coordinate_algebra().krull_dimension() == 2
