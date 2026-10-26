r"""The fan of the projective plane gives a smooth complete toric surface."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_from_its_fan_is_toric() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    plane = fans.projective_space_fan().toric_variety(QQ)

    assert plane in ToricSchemes(QQ)
    assert plane in Varieties(QQ)
    assert plane in Surfaces(QQ)
    assert plane in ProperSurfaces(QQ)
    assert plane in ProjectiveSurfaces(QQ)
    assert plane in NormalSchemes(QQ)
    assert plane in SmoothSchemes(QQ)
    assert plane in IntegralSchemes(QQ)
    assert plane.dimension() == 2
    assert plane.is_complete()
    assert plane.is_smooth()
    assert plane.is_normal()
    assert plane.is_del_pezzo()
    assert DelPezzoSurfaces(plane.scheme_base_ring())(plane).del_pezzo_degree() == 9


def test_projective_plane_orbit_cone_correspondence() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    plane = fans.projective_space_fan().toric_variety(QQ)

    assert plane.torus_orbits(2).cardinality() == 1
    assert plane.torus_orbits(1).cardinality() == 3
    assert plane.torus_orbits(0).cardinality() == 3
