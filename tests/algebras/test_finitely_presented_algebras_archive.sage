r"""Morphisms out of a presented algebra are determined by generator images."""

from sage_extensions.all import *  # noqa: F401,F403


def test_swapping_the_axes_is_an_involutive_automorphism_of_qq_xy_mod_xy() -> None:
    r"""``x ↔ y`` respects the relation ``xy`` of ``QQ[x,y]/(xy)``, so it defines an
    algebra endomorphism ``σ`` with ``σ(x^2 + y) = y^2 + x`` and ``σ^2 = id``."""
    plane = QQ["x,y"]
    axes = plane.quotient(plane.ideal([plane.gen(0) * plane.gen(1)]))
    x, y = axes(plane.gen(0)), axes(plane.gen(1))
    swap = axes.Mor(axes)({x: y, y: x})

    assert swap(x) == y
    assert swap(x**2 + y) == y**2 + x
    assert swap(x * y) == axes.zero()
    assert swap(swap(x**3 + 2 * y)) == x**3 + 2 * y
    assert swap(x) != x
