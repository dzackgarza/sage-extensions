r"""Picard arithmetic on `\mathbb{P}^1 \times \mathbb{P}^1` over QQ.

Source: Hartshorne, *Algebraic Geometry*, II.6.6.1 and V.1.4.3:
`\operatorname{Pic}(\mathbb{P}^1 \times \mathbb{P}^1) = \mathbb{Z}^2` by bidegree,
`K = \mathcal{O}(-2,-2)`, `\mathcal{O}(a,b)` is ample iff `a, b > 0`, and the
intersection form is the hyperbolic plane.
"""

from sage_extensions.all import *


def test_picard_arithmetic_of_a_product_of_lines_is_by_bidegree() -> None:
    line = ProjectiveSpaces(QQ)(1)
    product = Schemes(QQ).product((line, line))

    assert product.O(2, 1).tensor_product(product.O(-2, -1)) == product.O(0, 0)
    assert product.canonical_line_bundle() == product.O(-2, -2)
    assert product.anticanonical_line_bundle().is_ample()
    assert not product.O(1, 0).is_ample()


def test_picard_pairing_of_P1_times_P1_is_the_hyperbolic_plane() -> None:
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    surface = fans.hirzebruch_surface_fan(0).toric_variety(QQ)
    picard = surface.picard_group()
    pairing = surface.picard_intersection_pairing()
    classes = tuple(
        surface.torus_invariant_cartier_class_projection()(
            surface.torus_invariant_prime_divisor(ray)
        )
        for ray in surface.fan().cones(1)
    )

    assert picard.module_rank() == 2
    assert any(
        pairing(left, left) == 0
        and pairing(right, right) == 0
        and pairing(left, right) == 1
        and pairing(right, left) == 1
        for left in classes
        for right in classes
    )
