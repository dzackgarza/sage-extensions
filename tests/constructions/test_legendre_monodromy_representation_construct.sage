r"""The Legendre family retains its pointed fundamental group and positive monodromy."""

from sage_extensions.all import *  # noqa: F401,F403


def test_legendre_pointed_fundamental_group_uses_the_smooth_stratum_and_basepoint() -> None:
    family = LegendreMonodromyFamily()
    fundamental_group = family.pointed_fundamental_group()

    assert fundamental_group.space() is family.smooth_stratum()
    assert fundamental_group.base_point() is family.base_point()


def test_legendre_positive_monodromy_is_the_image_of_the_positive_loop() -> None:
    family = LegendreMonodromyFamily()
    fundamental_group = family.pointed_fundamental_group()
    representation = family.monodromy_representation()

    assert family.positive_monodromy() == representation(
        fundamental_group.positive_loop_generator()
    )
    assert family.monodromy_preserves_pairing()
