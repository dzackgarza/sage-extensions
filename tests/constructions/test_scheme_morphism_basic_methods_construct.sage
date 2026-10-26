r"""Scheme morphisms expose their affine pullback, composition, and immersion predicates."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_scheme_morphism_exposes_its_coordinate_pullback() -> None:
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = AffineSchemes(QQ)(ring)
    squaring = line.Mor(line)(ring.Mor(ring)({"x": x**2}))

    assert squaring.pullback_on_coordinate_algebras() is squaring.coordinate_algebra_morphism()


def test_scheme_morphism_then_is_notebook_order_composition() -> None:
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = AffineSchemes(QQ)(ring)
    squaring = line.Mor(line)(ring.Mor(ring)({"x": x**2}))
    translation = line.Mor(line)(ring.Mor(ring)({"x": x + 1}))

    assert squaring.then(translation) == translation * squaring


def test_closed_subscheme_inclusion_is_a_closed_immersion() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    parabola = plane.closed_subscheme(y - x**2)

    assert parabola.inclusion().is_closed_immersion()
