r"""Equivariant vector orbits are computed under the actual lattice centralizer."""

from sage_extensions.all import *


def test_representatives_are_the_same_live_orbit_package() -> None:
    lattice = Lattices(ZZ)("A1")
    root = lattice.basis_vector(0)
    isometry = lattice.Aut().one()
    decomposition = isometry.equivariant_vector_orbit_decomposition(root.q())

    assert isometry.equivariant_vector_orbit_representatives(
        root.q()
    ) == decomposition.representatives()
    assert decomposition.orbits().cardinality() == 1
    assert lattice.vectors_of_square(root.q()).cardinality() == 2
    assert decomposition.group().cardinality() == 2
