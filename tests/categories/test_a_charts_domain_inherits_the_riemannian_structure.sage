r"""The domain of a chart on a proper open subset of a Riemannian manifold is a Riemannian manifold."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_chart_on_a_proper_open_subset_is_a_riemannian_open_submanifold() -> None:
    r"""An open subset of a Riemannian manifold carries the restricted metric.

    ``U`` is the chart of the hyperbolic plane on the open subset where the
    first chart coordinate does not vanish, so its domain is a proper open
    subset; with the restricted atlas it is a smooth manifold of the same
    dimension (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Example 1.4)
    and, with the metric restricted along the inclusion, a Riemannian manifold.
    The restriction is stated in the charts the ambient metric is stated in,
    which restrict to the open subset, so ``U`` is not among its labels.
    """
    space = HyperbolicSpaces(2).an_object()
    chart = space.atlas()["hyperboloid"]
    domain = space.chart_on_open_subset("U", "y0 y1", "hyperboloid", (chart.coordinate(0),)).domain()

    assert domain in RiemannianManifolds()
    assert domain.dimension() == space.dimension()

    metric = domain.riemannian_metric()
    assert tuple(metric.index_set()) == ("hyperboloid",)
    assert metric["hyperboloid"][0][0](space.point((0, 0), "hyperboloid")) == 1

    smooth_domain = domain.underlying_smooth_manifold()
    assert smooth_domain in SmoothManifolds()
    assert smooth_domain.dimension() == space.dimension()
    assert RiemannianManifolds().forget_metric()(domain) is smooth_domain
