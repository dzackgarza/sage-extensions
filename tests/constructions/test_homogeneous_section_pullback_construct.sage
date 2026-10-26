r"""Pullback along a projective-product projection sends O(d) sections to the corresponding multidegree."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadratic_sections_pull_back_along_first_projection_of_p1_times_p1() -> None:
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    product = Schemes(QQ).product((line, line))
    sections = line.O(2).homogeneous_polynomial_sections()
    pullback = sections.pullback(product.projection(0))

    assert pullback.domain() is sections
    assert pullback.codomain().dimension() == 3
    assert pullback.codomain() is product.O(2, 0).global_sections()
