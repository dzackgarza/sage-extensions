r"""The $k$-element subsets and $k$-element multisets of a finite or countable set.

For $|S| = n$ there are $\binom{n}{k}$ subsets and $\binom{n+k-1}{k}$
multisets of size $k$; there is one of size $0$ and no subset of size $k > n$.
For countably infinite $S$ and $k \ge 1$ both are countably infinite.  The
exterior product $e_A \wedge e_B$ of two disjoint subsets is
$\pm e_{A \cup B}$, with sign $(-1)^{\#\{(a, b) \in A \times B : a > b\}}$,
and it vanishes when $A \cap B \neq \emptyset$.  These are the definitions of
binomial coefficients and of the exterior algebra's standard basis.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_four_points_have_six_two_subsets_and_ten_two_multisets() -> None:
    points = Sets.Δ[3]
    subsets = points.ordered_subsets_of_size(2)
    multisets = points.multisets_of_size(2)

    assert subsets.cardinality() == cardinal(6)
    assert multisets.cardinality() == cardinal(10)
    assert points.ordered_subsets_of_size(0).cardinality() == cardinal(1)
    assert points.ordered_subsets_of_size(5).cardinality() == cardinal(0)
    assert [subsets.ranking_map()(subset) for subset in subsets] == [0, 1, 2, 3, 4, 5]


def test_the_two_subsets_of_the_natural_numbers_are_countably_infinite() -> None:
    assert NN.ordered_subsets_of_size(2).cardinality() == aleph0


def test_a_two_subset_has_its_support_and_multiplicities() -> None:
    points = Sets.Δ[3]
    subset = points.ordered_subsets_of_size(2).from_labels([points(0), points(2)])

    assert list(subset) == [points(0), points(2)]
    assert subset.multiplicity(points(2)) == 1
    assert subset.multiplicity(points(1)) == 0
    assert subset.support().cardinality() == cardinal(2)
    assert subset.add_label(points(1)) == points.ordered_subsets_of_size(3).from_labels(
        [points(0), points(1), points(2)]
    )


def test_a_multiset_counts_repeated_points_and_merges_by_adding_multiplicities() -> None:
    r"""$\{1, 1\} + \{0, 3\} = \{0, 1, 1, 3\}$, whose support has three points."""
    points = Sets.Δ[3]
    multisets = points.multisets_of_size(2)
    doubled = multisets.from_labels([points(1), points(1)])
    merged = doubled.merged_with(multisets.from_labels([points(0), points(3)]))

    assert doubled.multiplicity(points(1)) == 2
    assert doubled.support().cardinality() == cardinal(1)
    assert merged.multiplicity(points(1)) == 2
    assert merged.support().cardinality() == cardinal(3)
    assert multisets.from_multiplicities({points(0): 1, points(3): 1}) == multisets.from_labels(
        [points(0), points(3)]
    )


def test_the_exterior_product_of_e02_and_e13_is_minus_e0123() -> None:
    r"""$e_0 e_2 e_1 e_3 = -e_0 e_1 e_2 e_3$ (one inversion); $e_1 e_3 e_0 e_2$ has three inversions; $e_{02} \wedge e_{02} = 0$."""
    points = Sets.Δ[3]
    subsets = points.ordered_subsets_of_size(2)
    first = subsets.from_labels([points(0), points(2)])
    second = subsets.from_labels([points(1), points(3)])
    whole = points.ordered_subsets_of_size(4).from_labels(list(points))

    assert first.wedge_with(second) == (whole, -1)
    assert second.wedge_with(first) == (whole, -1)
    assert first.wedge_with(first) is None
