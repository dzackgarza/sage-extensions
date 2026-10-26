r"""Integral singular cohomology of P^2 has ranks 1,0,1,0,1."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_integral_singular_cohomology() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    degree_two = plane.integral_singular_cohomology(2)

    assert degree_two in IntegralTopologicalCohomologyGroups(ZZ)
    assert degree_two in IntegralSingularCohomologyGroups(ZZ)
    assert degree_two in ToricIntegralSingularCohomologyGroups(ZZ)
    assert degree_two.cohomological_degree() == 2
    assert degree_two.cohomology_coefficients() is ZZ
    assert degree_two.topological_scheme() is plane
    assert degree_two.rank() == 1
    assert [plane.integral_singular_cohomology(k).rank() for k in range(5)] == [1, 0, 1, 0, 1]
