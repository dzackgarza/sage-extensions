r"""Enumerated sets build fixed-size subsets and multisets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_four_points_have_six_pairs_and_ten_two_multisets() -> None:
    points = Sets.Δ[3]
    subsets = points.fixed_size_selections(2, repetition=False)
    multisets = points.fixed_size_selections(2, repetition=True)

    assert subsets is points.ordered_subsets_of_size(2)
    assert multisets is points.multisets_of_size(2)
    assert subsets.cardinality() == cardinal(6)
    assert multisets.cardinality() == cardinal(10)
    assert points.ordered_subsets_of_size(0).cardinality() == cardinal(1)
    assert points.ordered_subsets_of_size(5).cardinality() == cardinal(0)
