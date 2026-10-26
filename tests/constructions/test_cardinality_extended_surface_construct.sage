r"""Cardinal arithmetic acts on comparison morphisms and indexed finite families."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_indexed_cardinal_sum_and_product_have_expected_values() -> None:
    cardinals = Cardinalities()
    indices = Sets.Δ[2]

    assert cardinals.indexed_sum(
        indices,
        lambda index: cardinal(int(index) + 1),
    ) == cardinal(6)
    assert cardinals.indexed_product(
        indices,
        lambda index: cardinal(int(index) + 2),
    ) == cardinal(24)
    assert cardinals.supremum(cardinal(3), aleph0) == aleph0


def test_cardinal_arithmetic_carries_comparison_morphisms() -> None:
    cardinals = Cardinalities()
    two_three = cardinals.Mor(2, 3).unique_morphism()
    four_five = cardinals.Mor(4, 5).unique_morphism()

    assert cardinals.sum_morphism(
        two_three,
        four_five,
    ) == cardinals.Mor(6, 8).unique_morphism()
    assert cardinals.product_morphism(
        two_three,
        four_five,
    ) == cardinals.Mor(8, 15).unique_morphism()
    assert cardinals.power_morphism(
        two_three,
        four_five,
    ) == cardinals.Mor(16, 243).unique_morphism()


def test_aleph_two_and_the_continuum_are_undecided_by_the_represented_cardinal_laws() -> None:
    cardinals = Cardinalities()

    assert cardinals.are_incomparable(aleph(2), continuum)
