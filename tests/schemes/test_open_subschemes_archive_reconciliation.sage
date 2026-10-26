r"""Distinguished opens of the affine plane over QQ."""

from sage_extensions.all import *


def test_inclusions_of_distinguished_opens_compose_and_intersect() -> None:
    r"""`D(xy) \subseteq D(x) \subseteq \mathbb{A}^2` compose to the inclusion of `D(xy)`,
    and `D(x) \cap D(y) = D(xy)` (a prime avoids `xy` iff it avoids `x` and `y`)."""
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    open_x = plane.distinguished_open(x)
    open_y = plane.distinguished_open(y)
    open_xy = plane.distinguished_open(x * y)

    assert open_x.inclusion() * open_xy.inclusion_into(open_x) == open_xy.inclusion()
    assert open_x.intersection(open_y) == open_xy
    assert open_x.coordinate_ring().krull_dimension() == 2
