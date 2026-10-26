r"""Ordered enumerated sets retain their chosen enumeration and ranking."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_ordinal_exposes_ordered_enumeration_data() -> None:
    three = Sets.Δ[2]
    enumeration = three.enumeration()
    inverse = three.enumeration_inverse()

    assert three in OrderedEnumeratedSets()
    assert three.index_set() is three
    assert enumeration(three(1)) == three(1)
    assert inverse(three(2)) == three(2)
    assert three.is_parent_of(three(0))
    assert three.order_type() == ordinal(3)
    assert three.ranking_map()(three(2)) == NN(2)
