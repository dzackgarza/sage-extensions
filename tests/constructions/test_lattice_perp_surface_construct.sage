r"""The lattice perp notation is the orthogonal-complement construction."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_perp_matches_orthogonal_complement() -> None:
    lattice = NamedLattices.U
    line = lattice.subobject_on((lattice.basis_vector(0),))

    assert lattice.perp(line) == lattice.orthogonal_complement(line)


def test_sublattice_perp_without_argument_uses_its_ambient_inclusion() -> None:
    lattice = NamedLattices.U
    line = lattice.subobject_on((lattice.basis_vector(0),))

    assert line.perp() == line.orthogonal_complement()
    assert line.perp().ambient_lattice() is lattice
