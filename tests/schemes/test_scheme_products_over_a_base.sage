r"""Products of projective and affine lines over QQ.

Source: Hartshorne, *Algebraic Geometry*, II.6.6.1: `\operatorname{Pic}(\mathbb{P}^1
\times \mathbb{P}^1) = \mathbb{Z}^2`, while `\operatorname{Pic} \mathbb{P}^2 =
\mathbb{Z}`, so the two surfaces are not isomorphic.  `\mathbb{A}^1 \times
\mathbb{P}^1` contains the complete curve `\{0\} \times \mathbb{P}^1`, so it is not
affine.
"""

from sage_extensions.all import *


def test_the_product_of_two_projective_lines_is_a_projective_surface_not_the_plane() -> None:
    line = ProjectiveSpaces(QQ)(1)
    quadric = Schemes(QQ).product((line, line))

    assert quadric.is_projective()
    assert quadric.is_smooth()
    assert quadric.relative_dimension() == 2
    assert quadric.picard_group().module_rank() == 2
    assert not quadric.is_isomorphic(ProjectiveSpaces(QQ)(2))


def test_the_product_of_the_affine_and_projective_lines_is_not_affine() -> None:
    product = Schemes(QQ).product((AffineSpaces(QQ)(1), ProjectiveSpaces(QQ)(1)))

    assert product.relative_dimension() == 2
    assert not product.is_affine()
    assert product.structure_sheaf().global_sections().krull_dimension() == 1
