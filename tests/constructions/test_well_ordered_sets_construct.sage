r"""Finite ordinals are well-ordered sets with order-preserving morphisms."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_point_finite_ordinal_is_a_well_order() -> None:
    three = Sets.Δ[2]

    assert three in WellOrderedSets()
    assert three.order_type() == ordinal(3)


def test_well_order_identity_retains_underlying_set_map() -> None:
    three = Sets.Δ[2]
    identity = WellOrderedSets().Mor(three, three).identity()

    assert identity.is_identity()
    assert identity.underlying_set_morphism() == Sets().Mor(three, three).identity()
