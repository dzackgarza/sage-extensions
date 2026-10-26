r"""A lattice exposes its algebraic dual and the metric map into that dual."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_linear_dual_is_the_module_dual() -> None:
    lattice = NamedLattices.U

    assert lattice.linear_dual() == lattice.dual_module()
    assert lattice.linear_dual().module_rank() == lattice.module_rank()


def test_hyperbolic_plane_metric_map_is_the_algebraic_correlation() -> None:
    lattice = NamedLattices.U
    metric = lattice.metric_map()
    correlation = lattice.algebraic_correlation_morphism()
    e = lattice.basis_vector(0)

    assert metric == correlation
    assert metric.domain() is lattice
    assert metric.codomain() is lattice.linear_dual()
    assert metric(e) == correlation(e)
