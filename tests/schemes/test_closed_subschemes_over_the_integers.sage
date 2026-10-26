r"""Closed subschemes of the affine plane over the integers."""

from sage_extensions.all import *


def test_the_point_x_zero_on_the_parabola_over_the_integers_is_the_origin() -> None:
    r"""On the parabola \(y = x^2\) in \(\mathbf A^2_{\mathbf Z}\), cutting \(x = 0\) gives
    \(\mathbf Z[x,y]/(y-x^2, x) \cong \mathbf Z\): \(y\) vanishes there as well, the parabola has relative
    dimension \(1\) over \(\operatorname{Spec}\mathbf Z\) and the cut has relative dimension \(0\).

    Derivation: \(y = (y - x^2) + x\cdot x \in (y - x^2, x)\).
    """
    plane = Schemes(ZZ)(ZZ["x,y"])
    x, y = ZZ["x,y"].algebra_generator("x"), ZZ["x,y"].algebra_generator("y")
    parabola = plane.closed_subscheme(y - x**2)
    on_parabola = parabola.inclusion().coordinate_algebra_morphism()

    origin = parabola.closed_subscheme(on_parabola(x))
    to_origin = origin.inclusion().coordinate_algebra_morphism()

    assert to_origin(on_parabola(y)).is_zero()
    assert not on_parabola(y).is_zero()
    assert parabola.relative_dimension() == 1
    assert origin.relative_dimension() == 0
