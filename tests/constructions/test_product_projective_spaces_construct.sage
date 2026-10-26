r"""The product of two projective lines is a smooth projective product."""

from sage_extensions.all import *  # noqa: F401,F403


def test_product_of_two_projective_lines() -> None:
    line = ProjectiveSpaces(QQ)(1)
    product = Schemes(QQ).product((line, line))

    assert product in ProductProjectiveSpaces(QQ)
    assert product in ProductSchemes(QQ)
    assert product in ProjectiveSchemes(QQ)
    assert product in SmoothSchemes(QQ)
    assert product.factors().cardinality() == cardinal(2)
    assert product.canonical_line_bundle() == product.O(-2, -2)
    assert product.anticanonical_line_bundle().is_ample()
