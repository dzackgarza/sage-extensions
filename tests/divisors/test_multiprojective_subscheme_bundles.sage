r"""Adjunction for a hypersurface in a product of projective spaces."""

from sage_extensions.all import *  # noqa: F401,F403


def test_canonical_bundle_of_a_bidegree_one_one_hypersurface_in_P2_x_P1_is_O_minus_2_minus_1() -> None:
    r"""``X = V(x0 y0 + x1 y1) subset P^2 x P^1`` has ``K_X = O(-2, -1)|_X``.

    ``K_{P^2 x P^1} = O(-3, -2)`` and adjunction gives
    ``K_X = (K + X)|_X = O(-3 + 1, -2 + 1)|_X`` (Hartshorne, *Algebraic
    Geometry*, II.8.20).  ``X`` is smooth: the partial derivatives
    ``(y0, y1, 0, x0, x1)`` never vanish together on ``P^2 x P^1``.
    """
    plane = ProjectiveSpaces(QQ)(2, names=("x0", "x1", "x2"))
    line = ProjectiveSpaces(QQ)(1, names=("y0", "y1"))
    product = plane * line
    ring = product.homogeneous_coordinate_ring()
    x0, x1, y0, y1 = ring("x0"), ring("x1"), ring("y0"), ring("y1")
    hypersurface = product.closed_subscheme(x0 * y0 + x1 * y1)

    canonical = hypersurface.canonical_bundle()

    assert product.canonical_bundle().is_isomorphic(product.O(-3, -2))
    assert hypersurface.is_smooth()
    assert hypersurface.dimension() == 2
    assert canonical.is_isomorphic(product.O(-2, -1).restrict_to(hypersurface))
    assert canonical.is_isomorphic(
        product.O(-3, 0).restrict_to(hypersurface).tensor_product(product.O(1, -1).restrict_to(hypersurface))
    )
