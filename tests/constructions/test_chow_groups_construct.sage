r"""The curve Chow group of P^2 is free of rank one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_curve_chow_group() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    chow = plane.chow_group(1)

    assert chow in ChowGroups(ZZ)
    assert chow.chow_scheme() is plane
    assert chow.cycle_dimension() == 1
    assert chow.cycle_codimension() == 1
    assert chow.module_rank() == 1
