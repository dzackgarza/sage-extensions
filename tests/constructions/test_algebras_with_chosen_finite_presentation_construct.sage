r"""The node xy=0 retains its chosen polynomial presentation and quotient map."""

from sage_extensions.all import *  # noqa: F401,F403


def _coordinate_axes():
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))
    return plane, x, y, axes


def test_coordinate_axes_retain_the_selected_algebra_presentation() -> None:
    plane, x, y, axes = _coordinate_axes()
    projection = axes.algebra_presentation_morphism()
    xbar = axes.algebra_generator("x")
    ybar = axes.algebra_generator("y")

    assert axes in AlgebrasWithChosenFinitePresentation(QQ)
    assert axes.presentation_ring() is plane
    assert axes.relations().cardinality() == cardinal(1)
    assert axes.presentation_ideal() == plane.ideal(x * y)
    assert projection.domain() is plane
    assert projection.codomain() is axes
    assert projection(x) == xbar
    assert projection(y) == ybar
    assert projection(x * y) == axes.zero()
    assert projection(axes.lift_to_presentation(xbar + ybar)) == xbar + ybar
    assert axes.is_torsion_free()


def test_coordinate_axes_base_change_retains_the_defining_relation() -> None:
    _, _, _, axes = _coordinate_axes()
    gaussian = QuadraticField(-1, "i")
    scalar_map = QQ.Mor(gaussian)(lambda rational: gaussian(rational))
    changed = axes.base_change(scalar_map)
    x = changed.algebra_generator("x")
    y = changed.algebra_generator("y")

    assert changed in AlgebrasWithChosenFinitePresentation(gaussian)
    assert x * y == changed.zero()

