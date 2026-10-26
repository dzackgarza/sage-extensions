r"""The fixed-cardinality subset functor sends a finite set to its k-subsets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_element_subset_functor_on_three_points_has_three_values() -> None:
    functor = Sets().fixed_cardinality_subset_functor(2)
    three = Sets.Δ[2]

    assert functor.subset_cardinality() == 2
    assert functor(three).cardinality() == cardinal(3)
