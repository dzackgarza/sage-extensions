r"""Morphisms out of a presented algebra are determined by generator images.

A morphism of a presented algebra is given by the images of its algebra
generators, keyed by their labels, and it is admitted only when those images
annihilate the retained presentation relations.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_swapping_the_axes_is_an_involutive_automorphism_of_qq_xy_mod_xy() -> None:
    r"""``x ↔ y`` respects the relation ``xy`` of ``QQ[x,y]/(xy)``, so it defines an
    algebra endomorphism ``σ`` with ``σ(x^2 + y) = y^2 + x`` and ``σ^2 = id``."""
    plane = QQ["x, y"]
    plane_x = plane.algebra_generator("x")
    plane_y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations([plane_x * plane_y])
    x = axes.algebra_generator("x")
    y = axes.algebra_generator("y")
    swap = axes.Mor(axes)({"x": y, "y": x})

    assert swap(x) == y
    assert swap(x**2 + y) == y**2 + x
    assert swap(x * y) == axes.zero()
    assert swap(swap(x**3 + 2 * y)) == x**3 + 2 * y
    assert swap(x) != x
