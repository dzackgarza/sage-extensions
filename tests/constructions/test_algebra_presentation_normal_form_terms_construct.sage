r"""The selected normal form of x+y on the coordinate axes has two monomial terms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_axes_normal_form_terms_of_x_plus_y() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))
    x_bar = axes.algebra_generator("x")
    y_bar = axes.algebra_generator("y")
    terms = axes.presentation_normal_form_terms(x_bar + y_bar)

    assert terms.cardinality() == cardinal(2)
