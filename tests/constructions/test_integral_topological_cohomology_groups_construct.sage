r"""Integral topological cohomology retains its realization and degree data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_integral_topological_cohomology_data() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    degree_two = plane.integral_singular_cohomology(2)

    assert degree_two in IntegralTopologicalCohomologyGroups(ZZ)
    assert degree_two.cohomological_degree() == 2
    assert degree_two.cohomology_coefficients() is ZZ
    assert degree_two.topological_scheme() is plane
