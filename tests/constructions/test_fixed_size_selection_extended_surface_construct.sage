r"""Fixed-size selections retain combinadic ranks, words, size families, and multiplicity constructors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_subset_combinadic_rank_word_and_size_family() -> None:
    points = Sets.Δ[3]
    subsets = points.ordered_subsets_of_size(2)
    subset = subsets.from_source_rank_positions((0, 2))

    assert subsets.selection_size() == 2
    assert subsets.with_size(3) is points.ordered_subsets_of_size(3)
    assert subset.combinatorial_rank() == 1
    assert tuple(subset.word()) == (points(0), points(2))
    assert subset == subsets.from_multiplicities(
        {points(0): 1, points(2): 1}
    )
    assert subset.add_label(points(1)) == points.ordered_subsets_of_size(
        3
    ).from_labels((points(0), points(1), points(2)))


def test_multiset_merge_and_singleton_power_use_multiplicities() -> None:
    points = Sets.Δ[3]
    pairs = points.multisets_of_size(2)
    doubled_one = pairs.singleton_power(points(1))
    zero_three = pairs.from_source_rank_positions((0, 3))
    merged = doubled_one.merged_with(zero_three)

    assert doubled_one == pairs.from_multiplicities({points(1): 2})
    assert merged.multiplicity(points(1)) == 2
    assert merged.multiplicity(points(0)) == 1
    assert merged.multiplicity(points(3)) == 1
