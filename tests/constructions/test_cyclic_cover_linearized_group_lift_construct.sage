r"""A Horikawa cyclic-cover algebra lifts the selected C2 linearization to the cover."""

from sage_extensions.all import *  # noqa: F401,F403


def test_horikawa_cyclic_algebra_lifts_nikulin_linearization() -> None:
    family = HorikawaK3Family()
    member = family.member()
    generator = next(iter(family.acting_group().group_generators()))
    lifted = member.cyclic_algebra().lift_linearized_group_element(
        family.nikulin_linearization(),
        generator,
    )

    assert lifted == member.nikulin_lift()
