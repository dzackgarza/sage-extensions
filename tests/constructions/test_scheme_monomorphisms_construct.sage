r"""Closed and open immersions are monomorphisms of schemes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_closed_and_open_inclusions_are_scheme_monomorphisms() -> None:
    ring = QQ["x,y"]
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    plane = AffineSchemes(QQ)(ring)
    parabola = plane.closed_subscheme(y - x**2)
    open_set = plane.distinguished_open(x)
    monomorphisms = SchemeMonomorphisms(Schemes(QQ))

    assert parabola.inclusion() in monomorphisms
    assert open_set.inclusion() in monomorphisms
