r"""Hom-sets of opposite and product categories of finite sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hom_set_cardinalities_in_the_opposite_and_product_of_finite_sets() -> None:
    r"""With ``[n] = {0, ..., n}``: ``|Hom([2], [1])| = 2^3 = 8``;
    ``Hom_{C^op}(A, B) = Hom_C(B, A)``, so ``|Hom_op([1], [2])| = 8`` and
    ``|Hom_op([2], [1])| = 3^2 = 9``; in ``Sets × Sets``,
    ``|Hom(([2], [1]), ([1], [2]))| = 2^3 · 3^2 = 72``."""
    three, two = Sets.Δ[2], Sets.Δ[1]
    opposite = Sets().opposite()
    product = Cat().product([Sets(), Sets()])

    assert Sets().Mor(three, two).cardinality() == 8
    assert opposite.Mor(opposite(two), opposite(three)).cardinality() == 8
    assert opposite.Mor(opposite(three), opposite(two)).cardinality() == 9
    assert product.Mor(product(three, two), product(two, three)).cardinality() == 72


def test_composition_in_the_opposite_category_is_reversed_composition() -> None:
    r"""For ``f : [2] -> [1]``, ``x ↦ min(x, 1)`` and ``g : [1] -> [0]``:
    ``f^op ∘ g^op = (g ∘ f)^op``."""
    a, b, c = Sets.Δ[2], Sets.Δ[1], Sets.Δ[0]
    f = Sets().Mor(a, b)(lambda x: b(min(int(x), 1)))
    g = Sets().Mor(b, c)(lambda _x: c(0))
    opposite = Sets().opposite()
    op_f = opposite.Mor(opposite(b), opposite(a))(f)
    op_g = opposite.Mor(opposite(c), opposite(b))(g)

    assert op_f * op_g == opposite.Mor(opposite(c), opposite(a))(g * f)
