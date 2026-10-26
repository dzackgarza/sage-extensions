r"""Resolution cohomology of the nodal cubic is the cohomology of its normalization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_nodal_cubic_resolution_cohomology_in_degree_one() -> None:
    topology = NodalCubicIntegralTopology()
    ordinary = topology.ordinary_cohomology(1)
    resolved = topology.resolution_cohomology(1)
    pullback = topology.normalization_pullback(1)

    assert resolved in ResolutionIntegralCohomologyGroups(ZZ)
    assert resolved in IntegralTopologicalCohomologyGroups(ZZ)
    assert resolved.cohomological_degree() == 1
    assert resolved.topological_scheme() is topology.scheme()
    assert ordinary.rank() == 1
    assert resolved.rank() == 0
    assert pullback.domain() is ordinary
    assert pullback.codomain() is resolved
    assert pullback.is_zero()
