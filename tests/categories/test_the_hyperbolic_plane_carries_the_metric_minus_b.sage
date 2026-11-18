r"""The metric of the hyperboloid model, and the refusal of a component of the wrong rank."""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_the_hyperbolic_plane_carries_the_metric_minus_b() -> None:
    r"""``g = -b`` on each tangent space: the identity at the chart's origin, ``diag(4/5, 1)`` at ``y = (1/2, 0)``.

    ``b`` is negative definite on ``t^perp`` for ``t`` the timelike vector of
    the component, so ``-b`` is positive definite on each ``x^perp``, and the
    chart sends ``y`` to ``x = s t + sum_p y_p u_p`` with
    ``s = sqrt((1 - q(y))/q(t))``.  Hence ``dx(u) = ds(u) t + u`` and

    .. math::

        g_{ij}(y) = -b(u_i, u_j) - \frac{b(y, u_i) b(y, u_j)}{1 - q(y)}.

    For the standard lattice ``I_{1,2}`` with ``t = -e_0`` the basis is
    ``u_1 = -e_1``, ``u_2 = -e_2``, so the matrix at ``y = 0`` is the identity;
    at ``y = (1/2, 0)`` it is ``diag(4/5, 1)``, since ``b(y, u_1) = -1/2`` and
    ``q(y) = -1/4`` give ``1 - (1/4)/(5/4) = 4/5``.
    """
    space = HyperbolicSpaces(2).an_object()
    metric = space.riemannian_metric()
    entries = metric["hyperboloid"]

    assert tuple(metric.index_set()) == tuple(space.chart_labels())
    centre = space.point((0, 0), "hyperboloid")
    assert entries[0][0](centre) == 1
    assert entries[1][1](centre) == 1
    assert entries[0][1](centre) == 0
    assert entries[1][0](centre) == 0

    half = space.point((RR(1) / RR(2), RR(0)), "hyperboloid")
    assert entries[0][0](half) == RR(4) / RR(5)
    assert entries[1][1](half) == 1
    assert entries[0][1](half) == entries[1][0](half)


def test_placing_a_component_of_the_wrong_rank_is_refused() -> None:
    r"""A component of a rank-three lattice spans a hyperbolic plane, not a hyperbolic 3-space.

    The dimension of ``HH(C^+)`` is ``rank - 1``, so placing that component in
    ``HyperbolicSpaces(3)`` is a wrong argument and is refused as one, and
    placing it in ``HyperbolicSpaces(2)`` gives an object of that category.
    """
    space = HyperbolicSpaces(2).an_object()
    component = space.positive_cone_component()

    with pytest.raises(ValueError):
        HyperbolicSpaces(3)(component)

    assert HyperbolicSpaces(2)(component) in HyperbolicSpaces(2)
