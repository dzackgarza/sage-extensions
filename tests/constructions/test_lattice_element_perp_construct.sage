r"""A lattice vector exposes its orthogonal-complement sublattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_basis_vector_perp_matches_its_sublattice_complement() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)

    assert e.perp() == e.sublattice().orthogonal_complement()
    assert e.orthogonal_complement() == e.perp()


def test_vector_perp_retains_the_same_ambient_lattice() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    complement = e.perp()

    assert complement.ambient_lattice() is lattice
