r"""The Enriques primitive extension lifts and compares its anti-invariant arithmetic-group elements."""

from sage_extensions.all import *  # noqa: F401,F403


def test_enriques_coinvariant_extension_lifts_minus_identity_to_the_k3_centralizer() -> None:
    extension = Involutions.I_En.primitive_extension()
    anti = extension.orthogonal_complement
    minus_identity = anti.O()(
        {
            label: -anti.module_generator(label)
            for label in anti.module_generating_set()
        }
    )
    lifted = extension.lift_coinvariant_extension_element(minus_identity)

    assert extension.coinvariant_restriction(lifted) == minus_identity
    assert lifted in extension.centralizer_group()


def test_enriques_coinvariant_isotropic_orbit_representative_has_identity_witness() -> None:
    extension = Involutions.I_En.primitive_extension()
    representatives = extension.coinvariant_isotropic_orbit_representatives(1)
    representative = representatives[0]
    witness = extension.coinvariant_isotropic_equivalence_witness(
        representative,
        representative,
    )

    assert representatives.cardinality() == cardinal(2)
    assert witness is not None
    assert witness in extension.centralizer_group()
    assert extension.coinvariant_restriction(
        witness
    ) in extension.coinvariant_extension_subgroup()
