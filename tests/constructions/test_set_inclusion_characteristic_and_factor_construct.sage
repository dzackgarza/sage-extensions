r"""Subset inclusions classify membership and factor exactly along containment."""

from sage_extensions.all import *  # noqa: F401,F403


def test_nested_finite_subset_inclusion_factors_and_characteristic_map_detects_membership() -> None:
    ambient = finite_ordered_set((0, 1, 2, 3))
    even = ambient.condition_set(lambda n: n % 2 == 0)
    zero = ambient.condition_set(lambda n: n == 0)
    even_inclusion = even.inclusion()
    zero_inclusion = zero.inclusion()
    factor = zero_inclusion.factor_through_or_none(even_inclusion)
    characteristic = even_inclusion.characteristic_morphism()

    assert factor is not None
    assert even_inclusion * factor == zero_inclusion
    assert characteristic(0) == Sets.Δ[1](1)
    assert characteristic(1) == Sets.Δ[1](0)


def test_noncontained_finite_subset_inclusion_has_no_factor() -> None:
    ambient = finite_ordered_set((0, 1, 2, 3))
    even = ambient.condition_set(lambda n: n % 2 == 0)
    odd = ambient.condition_set(lambda n: n % 2 == 1)

    assert odd.inclusion().factor_through_or_none(even.inclusion()) is None
