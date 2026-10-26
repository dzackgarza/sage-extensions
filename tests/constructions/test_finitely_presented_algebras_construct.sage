r"""A quotient of a polynomial algebra by finitely many relations is finitely presented."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_axes_are_finitely_presented_as_an_algebra() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations((x * y,))

    assert axes in FinitelyPresentedAlgebras(QQ)
    assert axes in Algebras(QQ).Associative().Unital().FinitelyPresentedAsAlgebra()
    assert axes.is_finitely_presented()

