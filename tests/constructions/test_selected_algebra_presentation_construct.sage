r"""A finitely presented algebra exposes its selected truncation-one algebra presentation."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_axes_selected_algebra_presentation_retains_polynomial_level_zero() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))
    presentation = axes.selected_algebra_presentation()

    assert presentation.truncation() == 1
    assert presentation.level(0) is plane
    assert axes.presentation_ring() is presentation.level(0)
