r"""The Euclidean line: the standard object of the Riemannian manifolds, with its metric."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_standard_riemannian_object_is_the_euclidean_line() -> None:
    r"""``(R, dx^2)``: a smooth manifold of dimension 1 with one global chart.

    The object is the smooth line ``R`` with the metric added to it, so it is
    a smooth manifold, its atlas is the line's chart ``x``, and the manifold
    it was selected on is an object of ``SmoothManifolds()``.
    """
    space = RiemannianManifolds().an_object()

    assert space in RiemannianManifolds()
    assert space.category() is RiemannianManifolds()
    assert space.dimension() == 1
    assert space.is_smooth() is True
    assert space.chart_labels().cardinality() == 1
    assert space.atlas()["x"].coordinates().cardinality() == 1
    assert space.underlying_smooth_manifold() in SmoothManifolds()


def test_the_metric_of_the_euclidean_line_is_one_in_its_chart() -> None:
    r"""``g(d/dx, d/dx) = 1`` at every point of the line.

    The metric is stated in the chart ``x`` of the smooth line it was selected
    on, and its one Gram entry is a function there; the value it takes at
    ``x = 3`` and at ``x = 0`` is 1, which is what makes the coordinate ``x``
    an isometry of the line onto ``R``.
    """
    space = RiemannianManifolds().an_object()
    line = space.underlying_smooth_manifold()
    metric = space.riemannian_metric()

    assert tuple(metric.index_set()) == tuple(space.chart_labels())
    entry = metric["x"][0][0]
    assert entry(line.point((3,), "x")) == 1
    assert entry(line.point((0,), "x")) == 1


def test_forgetting_the_metric_of_the_euclidean_line_returns_its_line() -> None:
    r"""``forget_metric`` sends ``(R, dx^2)`` to the smooth line it was selected on."""
    space = RiemannianManifolds().an_object()

    forgotten = RiemannianManifolds().forget_metric()(space)

    assert forgotten is space.underlying_smooth_manifold()
    assert forgotten in SmoothManifolds()


def test_the_globally_symmetric_category_forgets_a_metric_too() -> None:
    r"""A globally symmetric space is a Riemannian manifold, so it forgets its metric.

    The functor is stated on the axiom category, from itself to the smooth
    manifolds: what is forgotten is the metric, not the symmetric structure.
    """
    symmetric = RiemannianManifolds().GloballySymmetric()
    forgetting = symmetric.forget_metric()

    assert forgetting.domain() is symmetric
    assert forgetting.codomain() is SmoothManifolds()
