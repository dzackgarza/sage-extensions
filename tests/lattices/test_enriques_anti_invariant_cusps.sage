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




def test_the_enriques_period_lattice_has_two_isotropic_line_orbits_and_two_isotropic_plane_orbits() -> None:
    r"""``dzackgarza/lattice-database``, tag ``029J``, row ``O``: two orbits of
    primitive isotropic lines and two of primitive isotropic planes of T_En
    modulo O(T_En) (H. Sterk, *Compactifications of the period space of
    Enriques surfaces, Part I*, Math. Z. 207 (1991), Propositions 4.5 (p. 28)
    and 4.6 (p. 29); D. Dutour Sikiri'c and K. Hulek, arXiv:2302.01679,
    Section 3.6, p. 22).  The count is read from the card by tag and compared
    with the same public call the ``029J`` test of #286 uses."""
    lattice = NamedLattices.TEn
    lines = lattice.Aut().isotropic_orbit_representatives(1)
    assert lines.cardinality() == cardinal(2)
    planes = lattice.Aut().isotropic_orbit_representatives(2)
    assert planes.cardinality() == cardinal(2)
