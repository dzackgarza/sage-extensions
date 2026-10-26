r"""Integral lattice genera expose discriminant data, local symbols, representatives, and mass."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_genus_retains_discriminant_form_and_local_three_adic_excess() -> None:
    lattice = NamedLattices.A2
    genus = lattice.genus()
    symbol = genus.local_symbol(3)

    assert genus.discriminant_form().is_isomorphic(
        lattice.discriminant_quadratic_form()
    )
    assert symbol.prime() == 3
    assert genus.excess(3) == 2


def test_e8_genus_exists_and_has_one_owned_representative() -> None:
    lattice = NamedLattices.E8
    genus = lattice.genus()
    representatives = genus.representatives()

    assert genus.exists()
    assert representatives.cardinality() == cardinal(1)
    assert representatives[0].genus() == genus
    assert representatives[0].is_isometric(lattice) is True


def test_a2_definite_genus_has_mass_one_twelfth() -> None:
    genus = NamedLattices.A2.genus()

    assert genus.mass() == QQ(1) / 12
