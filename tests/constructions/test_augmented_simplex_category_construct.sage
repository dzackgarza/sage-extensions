r"""Finite ordinals are the objects of the augmented simplex category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_simplex_object_has_canonical_order_type_and_ranking() -> None:
    three = Sets.Δ[2]

    assert three in AugmentedSimplexCategory()
    assert three.is_parent_of(three(0))
    assert three.is_parent_of(three(2))
    assert not three.is_parent_of(NN(3))
    assert three.order_type() == ordinal(3)
    assert three.ranking_map()(three(2)) == NN(2)
