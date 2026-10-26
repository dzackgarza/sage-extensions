r"""The Enriques coinvariant arithmetic group retains its complete finite-character description."""

from sage_extensions.all import *  # noqa: F401,F403


def _enriques_coinvariant_group():
    extension = Involutions.I_En.primitive_extension()
    return extension.coinvariant_extension_subgroup()


def test_enriques_coinvariant_group_has_complete_character_kernel_data() -> None:
    group = _enriques_coinvariant_group()
    quotient = group.finite_character_quotient()

    assert group.character_data_is_complete()
    assert group.contains_character_kernel()
    assert quotient.subgroup is group


def test_enriques_coinvariant_group_has_identity_isotropic_equivalence_witness() -> None:
    group = _enriques_coinvariant_group()
    representative = group.isotropic_orbit_representatives(1)[0]
    witness = group.isotropic_equivalence_witness(representative, representative)

    assert witness is not None
    assert witness(representative) == representative
