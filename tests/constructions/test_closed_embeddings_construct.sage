r"""A principal closed subscheme retains its closed immersion into the ambient scheme."""

from sage_extensions.all import *  # noqa: F401,F403


def test_parabola_is_a_closed_embedding_in_the_affine_plane() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    parabola = plane.closed_subscheme(y - x**2)

    assert parabola in ClosedEmbeddings(plane)
    assert parabola.inclusion().codomain() is plane
    assert parabola.codimension() == 1
    assert parabola.defining_equations().cardinality() == cardinal(1)
