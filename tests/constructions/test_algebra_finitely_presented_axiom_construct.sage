r"""The coordinate axes admit a finite algebra presentation."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_axes_lie_in_the_finitely_presented_algebra_refinement() -> None:
    plane = QQ["x,y"]
    x, y = plane.algebra_generator("x"), plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))
    category = Algebras(QQ).Associative().Unital().FinitelyPresentedAsAlgebra()

    assert axes in category
    assert axes.presentation_ring() is plane
