r"""Graphs and scheme-theoretic images satisfy their defining identities."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_scheme_morphism_has_the_diagonal_as_graph() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))
    identity = line.categorical_identity_morphism()

    assert identity.graph_morphism() == line.diagonal_morphism()
    assert identity.graph_subscheme() == line.diagonal_subscheme()


def test_identity_inverse_image_of_a_closed_subscheme_is_itself() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    x = plane.coordinate_algebra().algebra_generator("x")
    line = plane.closed_subscheme(x)

    assert plane.categorical_identity_morphism().inverse_image(line) == line


def test_closed_immersion_has_its_source_as_scheme_theoretic_image() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    ring = plane.coordinate_algebra()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    parabola = plane.closed_subscheme(y - x**2)

    assert parabola.inclusion().scheme_theoretic_image() == parabola
