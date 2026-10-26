r"""Regularity of the affine plane and of the cusp `y^2 = x^3` at points.

Derivation: `\mathbb{Q}[x, y]_{(x, y)}` is regular of dimension 2, hence a UFD
(Auslander--Buchsbaum); on the cusp the maximal ideal `(x, y)` needs two generators
in a local ring of dimension 1, so it is singular, while at `(1, 1)` the gradient
`(-3x^2, 2y) = (-3, 2)` is nonzero.
"""

from sage_extensions.all import *


def test_the_plane_is_regular_and_the_cusp_is_singular_only_at_the_origin() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_ring()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    origin = plane.underlying_space()(ring.ideal(x, y))

    assert plane.is_regular_at(origin)
    assert plane.is_locally_factorial_at(origin)

    cusp = plane.closed_subscheme(y**2 - x**3)
    cusp_ring = cusp.coordinate_ring()
    cx = cusp_ring.algebra_generator("x")
    cy = cusp_ring.algebra_generator("y")
    cusp_origin = cusp.underlying_space()(cusp_ring.ideal(cx, cy))
    cusp_one = cusp.underlying_space()(cusp_ring.ideal(cx - 1, cy - 1))

    assert cusp.is_singular_at(cusp_origin)
    assert not cusp.is_regular_at(cusp_origin)
    assert cusp.is_regular_at(cusp_one)
