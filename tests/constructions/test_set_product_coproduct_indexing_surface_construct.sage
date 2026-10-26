r"""Set products and coproducts retain their indexed families and finite enumeration data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cartesian_product_retains_indexed_family_and_ranking() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    product = Sets().product((three, two))
    point = product((three(1), two(0)))

    assert product.family().index_set() is product.index_set()
    assert product.family()[0] is three
    assert product.family()[1] is two
    assert product.ranking_map().inverse()(product.ranking_map()(point)) == point


def test_coproduct_retains_indexed_family_and_parenthood() -> None:
    three = Set((1, 2, 3))
    two = Sets.Δ[1]
    coproduct = Sets().coproduct((three, two))
    point = coproduct.injection(1)(two(0))

    assert coproduct.family().index_set() is coproduct.index_set()
    assert coproduct.family()[0] is three
    assert coproduct.family()[1] is two
    assert coproduct.is_parent_of(point)
