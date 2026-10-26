r"""Ambient-centralizer lifts of the Enriques anti-invariant cusp action."""

from sage_extensions.all import *


def test_minus_identity_on_the_anti_invariant_lattice_lifts_to_the_k3_centralizer() -> None:
    extension = Involutions.I_En.primitive_extension()
    anti = extension.orthogonal_complement
    anti_group = extension.coinvariant_extension_subgroup()
    minus_identity = anti.O()(
        {
            label: -anti.module_generator(label)
            for label in anti.module_generating_set()
        }
    )

    assert anti.is_isometric(NamedLattices.TEn)
    assert minus_identity in anti_group
    lifted = extension.lift_coinvariant_extension_element(minus_identity)

    assert lifted in extension.centralizer_group()
    assert extension.coinvariant_restriction(lifted) == minus_identity
    assert lifted * Involutions.I_En == Involutions.I_En * lifted


