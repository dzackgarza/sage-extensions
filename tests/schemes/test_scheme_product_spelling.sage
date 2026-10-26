r"""The Segre embedding identifies `\mathbb{P}^1 \times \mathbb{P}^1` with the quadric
`xw = yz` in `\mathbb{P}^3` (Hartshorne, *Algebraic Geometry*, Exercise I.2.14 and
Example II.7.6.3)."""

from sage_extensions.all import *


def test_the_projective_line_times_itself_is_the_smooth_quadric_surface() -> None:
    line = ProjectiveSpaces(QQ)(1)
    space = ProjectiveSpaces(QQ)(3, names=("x", "y", "z", "w"))
    x, y, z, w = space.homogeneous_coordinate_generators()
    quadric = space.closed_subscheme(x * w - y * z)

    product = line.product_with(line)

    assert product.is_isomorphic(quadric)
    assert quadric.is_smooth()
    assert product.projection(0).codomain() is line
    assert product.projection(1).codomain() is line
