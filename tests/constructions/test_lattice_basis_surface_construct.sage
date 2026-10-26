r"""A lattice exposes its selected basis as lattice elements and by position."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_lattice_basis_matches_module_generators() -> None:
    lattice = NamedLattices.U
    basis = lattice.lattice_basis()
    generators = lattice.module_generators()

    assert basis.cardinality() == cardinal(2)
    assert basis == generators


def test_hyperbolic_plane_basis_vector_is_positional_access_to_selected_basis() -> None:
    lattice = NamedLattices.U
    basis = lattice.lattice_basis()

    assert lattice.basis_vector(0) == basis[0]
    assert lattice.basis_vector(1) == basis[1]
    assert lattice.b(lattice.basis_vector(0), lattice.basis_vector(1)) == ZZ.one()
