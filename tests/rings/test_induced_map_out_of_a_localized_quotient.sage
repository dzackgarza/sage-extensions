r"""The universal property of localization over the coordinate axes.

A = Q[x,y]/(xy) and A[1/x] is the punctured x-axis, on which y = 0 because
xy = 0 and x is invertible.  A map g out of A carrying x to a unit extends
uniquely to A[1/x] by a/s -> g(a) g(s)^{-1} (Atiyah-Macdonald 3.1).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _axes():
    plane = QQ['x,y']
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))
    return axes, axes.algebra_generator("x"), axes.algebra_generator("y")


def test_the_map_induced_by_the_localization_map_is_the_identity() -> None:
    r"""In A[1/x], y/x = 0 and (1/x) x = 1; by uniqueness the map induced by the
    localization map itself is the identity."""
    axes, xbar, ybar = _axes()
    punctured = axes.localization(xbar)
    induced = punctured.induced_morphism(punctured.localization_map())
    inverse_x = punctured.fraction(axes.one(), xbar)

    assert punctured.fraction(ybar, xbar) == punctured.zero()
    assert punctured(ybar) == punctured.zero()
    assert punctured(xbar) != punctured.zero()
    assert inverse_x * punctured(xbar) == punctured.one()
    assert induced(inverse_x) == inverse_x
    assert induced(punctured.fraction(xbar + 1, xbar**2)) == punctured.fraction(xbar + 1, xbar**2)


def test_an_evaluation_that_inverts_x_extends_to_the_localization() -> None:
    r"""The evaluation A -> Q, x -> 2, y -> 0 respects xy = 0 and sends x to a unit, so
    it extends to A[1/x], sending y/x to 0, 1/x to 1/2 and (x+1)/x^2 to 3/4."""
    axes, xbar, ybar = _axes()
    punctured = axes.localization(xbar)
    evaluation = axes.Mor(QQ)({"x": QQ(2), "y": QQ.zero()})
    induced = punctured.induced_morphism(evaluation)

    assert induced(punctured.fraction(ybar, xbar)) == 0
    assert induced(punctured.fraction(axes.one(), xbar)) == QQ(1) / 2
    assert induced(punctured.fraction(xbar + 1, xbar**2)) == QQ(3) / 4
    assert induced(punctured.localization_map()(xbar)) == 2
