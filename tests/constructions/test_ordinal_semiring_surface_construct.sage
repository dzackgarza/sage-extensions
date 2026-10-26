r"""Ordinals expose initial ordinals together with ordinary and Hessenberg arithmetic."""

from sage_extensions.all import *  # noqa: F401,F403


def test_initial_ordinal_round_trip_and_order_surface() -> None:
    ordinals = Ordinals()
    first = ordinals.initial(0)
    second = ordinals.initial(1)

    assert ordinals.from_expression(first.expression()) == first
    assert first.is_initial()
    assert first.initial_index() == ordinal(0)
    assert second.is_initial()
    assert second.initial_index() == ordinal(1)
    assert ordinals.proves_le(first, second)
    assert not ordinals.proves_le(second, first)


def test_ordinary_ordinal_product_and_power_are_order_sensitive() -> None:
    ordinals = Ordinals()
    omega0 = ordinals.initial(0)
    two = ordinals(2)

    assert ordinals.ordinal_product(two, omega0) == omega0
    assert ordinals.ordinal_product(omega0, two) != omega0
    assert ordinals.ordinal_power(two, omega0) == omega0


def test_hessenberg_sum_and_product_are_commutative_on_finite_ordinals() -> None:
    ordinals = Ordinals()
    two = ordinals(2)
    three = ordinals(3)

    assert ordinals.natural_sum(two, three) == ordinals(5)
    assert ordinals.natural_sum(two, three) == ordinals.natural_sum(three, two)
    assert ordinals.natural_product(two, three) == ordinals(6)
    assert ordinals.natural_product(two, three) == ordinals.natural_product(three, two)
