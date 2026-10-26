r"""Integral singular cohomology of a smooth complete toric variety retains its toric placement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_has_toric_integral_singular_cohomology() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    degree_two = plane.integral_singular_cohomology(2)

    assert degree_two in ToricIntegralSingularCohomologyGroups(ZZ)
    assert degree_two in IntegralSingularCohomologyGroups(ZZ)
    assert degree_two.rank() == 1
