r"""Archive reconciliation for cardinality comparison maps of set constructions."""

from sage_extensions.all import *  # noqa: F401,F403






def test_cardinality_compares_a_countable_power_set_with_two_to_aleph_zero() -> None:
    naturals = Sets.Δ[aleph0]
    power_set = naturals.power_set()
    comparison = Sets().cardinality_functor().power_set_comparison(power_set)
    expected = cardinal(2) ** aleph0

    assert comparison.domain() == expected
    assert comparison.codomain() == power_set.cardinality() == expected


def test_cardinality_comparisons_retain_countable_and_continuum_factor_arithmetic() -> None:
    polynomial = QQ.polynomial_ring("y")
    countable_product = ZZ.product_with(polynomial)
    continuum_product = ZZ.product_with(RR)
    continuum_coproduct = QQbar.coproduct_with(CC)
    cardinality = Sets().cardinality_functor()

    countable_comparison = cardinality.cartesian_product_comparison(countable_product)
    assert countable_comparison.domain() == aleph0
    assert countable_comparison.codomain() == aleph0

    continuum_product_comparison = cardinality.cartesian_product_comparison(continuum_product)
    assert continuum_product_comparison.domain() == continuum
    assert continuum_product_comparison.codomain() == continuum

    continuum_coproduct_comparison = cardinality.coproduct_comparison(continuum_coproduct)
    assert continuum_coproduct_comparison.domain() == continuum
    assert continuum_coproduct_comparison.codomain() == continuum
