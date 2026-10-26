r"""The punctured affine plane over QQ.

Source: Hartshorne, *Algebraic Geometry*, Exercise I.3.6 and II.2.17: the
functions on `U = \mathbb{A}^2 \setminus \{0\}` are `\mathbb{Q}[x, y]` (a function
regular off a point of codimension 2 extends), so `U` is not affine, since an
affine scheme with the coordinate ring of `\mathbb{A}^2` would be `\mathbb{A}^2`.
"""

from sage_extensions.all import *


def test_the_punctured_plane_is_not_affine_and_has_the_functions_of_the_plane() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    punctured = plane.closed_subscheme(x, y).open_complement()

    assert not punctured.is_affine()
    assert punctured.structure_sheaf().global_sections().is_isomorphic(plane.coordinate_ring())
    assert punctured.relative_dimension() == 2
