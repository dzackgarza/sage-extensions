r"""Owned rng morphisms extend and contract ideals and recognize group-algebra maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_identity_extends_and_contracts_ideals_trivially() -> None:
    identity = ZZ.Mor(ZZ).identity()
    ideal = ZZ.ideal(6)

    assert identity.extension_of_ideal(ideal) == ideal
    assert identity.contraction_of_ideal(ideal) == ideal
    assert not identity.is_group_algebra_augmentation()
    assert not identity.is_group_algebra_subgroup_inclusion()
