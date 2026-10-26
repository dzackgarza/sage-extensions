r"""Scheme products retain the number and labels of their factors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_product_projection_labels() -> None:
    line = AffineSpaces(QQ)(1)
    product = Schemes(QQ).product((line, line))

    assert product.number_of_factors() == cardinal(2)
    assert product.projection_label(product.projection(0)) == 0
    assert product.projection_label(product.projection(1)) == 1
