r"""The de Rham differential as a degree-one derivation."""

from sage_extensions.all import *  # noqa: F401,F403


def test_de_rham_differential_is_a_degree_one_graded_derivation() -> None:
    r"""On ``Ω^•(QQ[x,y])``: ``d`` raises degree by one, ``d(xy) = dx y + x dy``,
    ``d^2 = 0``."""
    algebra = QQ["x,y"]
    x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
    dga = algebra.de_rham_algebra()
    d = dga.differential()
    X, Y = dga(x), dga(y)

    assert d.degree_shift() == 1
    assert d(X * Y) == d(X) * Y + X * d(Y)
    assert d(d(X)) == dga.zero()
    assert d(X) != dga.zero()
