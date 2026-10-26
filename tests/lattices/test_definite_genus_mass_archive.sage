r"""Archived definite-genus representatives and mass on the live genus owner.

The archived integral-lattice genus object exposed a representative, all class
representatives, class number, determinant, and Smith--Minkowski--Siegel mass.
For the even unimodular ``E8`` genus there is one class, so its mass is exactly
the reciprocal of the full orthogonal-group order.
"""

from sage_extensions.all import *


def test_archived_e8_genus_has_one_owned_representative() -> None:
    lattice = Lattices.E8
    genus = lattice.genus()
    representatives = genus.representatives()

    assert genus.exists()
    assert genus.determinant() == 1
    assert genus.class_number() == 1
    assert representatives.cardinality() == 1
    assert representatives[0].genus() == genus
    assert representatives[0].is_isometric(lattice) is True

    representative = genus.representative()
    assert representative.genus() == genus
    assert representative.is_isometric(lattice) is True


def test_archived_e8_genus_mass_is_the_reciprocal_orthogonal_group_order() -> None:
    lattice = Lattices.E8
    genus = lattice.genus()
    orthogonal_order = lattice.O().cardinality().finite_value()

    assert orthogonal_order == 696729600
    assert genus.mass() == QQ(1) / orthogonal_order
