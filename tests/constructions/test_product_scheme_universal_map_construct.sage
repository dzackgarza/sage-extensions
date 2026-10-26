r"""A scheme product is the universal target of its projection cone."""

from sage_extensions.all import *  # noqa: F401,F403


def test_product_scheme_projections_reconstruct_the_identity() -> None:
    line = AffineSpaces(QQ)(1)
    product = Schemes(QQ).product((line, line))
    projections = (product.projection(0), product.projection(1))

    assert product.from_product_cone(projections) == product.categorical_identity_morphism()
