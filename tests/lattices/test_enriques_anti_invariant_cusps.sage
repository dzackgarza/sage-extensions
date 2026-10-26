r"""The Enriques anti-invariant arithmetic group from primitive gluing."""

from sage_extensions.all import *


def test_enriques_coinvariant_group_is_the_glue_compatible_discriminant_preimage() -> None:
    extension = Involutions.I_En.primitive_extension()
    anti = extension.orthogonal_complement_inclusion().domain()
    group = extension.coinvariant_extension_subgroup()

    assert anti.is_isometric(NamedLattices.TEn)
    assert group.supergroup() is anti.O()
    assert group.contains_character_kernel()
    assert group.character_data_is_complete()




def test_the_enriques_period_lattice_has_two_isotropic_line_orbits_and_five_isotropic_plane_orbits() -> None:
    r"""The Baily--Borel compactification of the Enriques period space has two
    0-dimensional and five 1-dimensional cusps (Sterk, Compactifications of
    the period space of Enriques surfaces I, Math. Z. 207 (1991)); every
    isometry of T_En extends across the glue, so the group is all of O(T_En)."""
    extension = Involutions.I_En.primitive_extension()
    group = extension.coinvariant_extension_subgroup()

    assert group.isotropic_orbit_representatives(1).cardinality() == 2
    assert group.isotropic_orbit_representatives(2).cardinality() == 5
