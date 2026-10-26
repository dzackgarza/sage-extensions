r"""A scheme object forms its binary fiber product over the common base with product_with."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_and_projective_lines_product_with_is_the_binary_scheme_product() -> None:
    affine = AffineSpaces(QQ)(1)
    projective = ProjectiveSpaces(QQ)(1)
    product = affine.product_with(projective)

    assert product in ProductSchemes(QQ)
    assert product.factors()[0] is affine
    assert product.factors()[1] is projective
    assert product.relative_dimension() == 2
