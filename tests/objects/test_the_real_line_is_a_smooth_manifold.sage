r"""The exact real field is the real line: a smooth one-dimensional manifold.

``RR`` is the set of real numbers with its field structure, and the real line is
that set with its order topology and the identity chart ``x: R -> R`` on the
whole space (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Example 1.2).
The field's own construction places it in the smooth manifolds, so the
membership is a membership of the field: no manifold is built beside it, since
a second real line is equal to ``RR`` in nothing.
"""

from sage_extensions.all import *


def test_the_real_field_is_a_smooth_one_dimensional_manifold() -> None:
    r"""``RR`` is a smooth manifold and a differentiable manifold, of dimension one."""
    assert RR in SmoothManifolds()
    assert RR in DifferentiableManifolds()
    assert RR.dimension() == 1
    assert RR.is_smooth()


def test_the_one_chart_of_the_real_line_is_the_identity_on_the_field() -> None:
    r"""A number is a point of the real line, and its coordinate in the identity chart is itself."""
    chart = RR.identity_chart()

    assert chart.manifold() is RR
    assert chart.domain() is RR
    assert tuple(chart(RR(3))) == (RR(3),)
    assert chart.coordinate(0)(RR(-3)) == RR(-3)


def test_the_smooth_maps_on_the_real_line_state_their_hypothesis_and_build() -> None:
    r"""``C(oo, RR, RR)`` is built on ``RR`` as the smooth manifold whose hypothesis it states."""
    assert RR in SmoothManifolds()
    maps = C(oo, RR, RR)

    assert maps in VectorSpaces(RR)
    assert maps in Algebras(RR)
