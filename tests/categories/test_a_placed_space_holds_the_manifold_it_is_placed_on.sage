r"""A hyperbolic or symmetric space holds the smooth manifold it is placed on."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_hyperbolic_plane_holds_the_smooth_manifold_it_is_placed_on() -> None:
    r"""``HH(C^+)`` is placed on a smooth manifold of dimension ``n``, with its chart.

    A hyperbolic space is a Riemannian manifold, so forgetting its metric is a
    map to a smooth manifold; that manifold is the object the metric is
    selected on, and it carries the hyperboloid's one chart.
    """
    space = HyperbolicSpaces(2).an_object()
    manifold = space.underlying_smooth_manifold()

    assert space.category() is HyperbolicSpaces(2)
    assert manifold in SmoothManifolds()
    assert manifold.dimension() == space.dimension()
    assert tuple(manifold.chart_labels()) == tuple(space.chart_labels())
    assert RiemannianManifolds().forget_metric()(space) is manifold


def test_the_hyperbolic_plane_still_carries_its_metric() -> None:
    r"""``g = -b`` is unchanged by the placement: the identity at ``y = 0``, ``4/5`` at ``y = (1/2, 0)``."""
    space = HyperbolicSpaces(2).an_object()
    entries = space.riemannian_metric()["hyperboloid"]

    assert entries[0][0](space.point((0, 0), "hyperboloid")) == 1
    assert entries[1][1](space.point((0, 0), "hyperboloid")) == 1
    half = space.point((RR(1) / RR(2), RR(0)), "hyperboloid")
    assert entries[0][0](half) == RR(4) / RR(5)
    assert entries[1][1](half) == 1


def test_the_symmetric_space_of_noncompact_type_holds_its_manifold() -> None:
    r"""``G/K`` is placed on a smooth manifold of its own dimension, and forgets its metric to it."""
    symmetric = RiemannianManifolds().GloballySymmetric()
    space = symmetric.noncompact_type(SatakeDiagrams().an_object())
    manifold = space.underlying_smooth_manifold()

    assert space in symmetric
    assert manifold in SmoothManifolds()
    assert manifold.dimension() == space.dimension()
    assert symmetric.forget_metric()(space) is manifold
    assert space.real_rank() == 1


def test_the_globally_symmetric_category_has_a_standard_object() -> None:
    r"""The Euclidean line, whose geodesic symmetries ``s_p(x) = 2p - x`` make it globally symmetric."""
    symmetric = RiemannianManifolds().GloballySymmetric()
    line = symmetric.an_object()

    assert line in symmetric
    assert line.dimension() == 1
    assert symmetric.forget_metric()(line) is line.underlying_smooth_manifold()
    origin = line.underlying_smooth_manifold().point((0,), "x")
    assert line.riemannian_metric()["x"][0][0](origin) == 1
