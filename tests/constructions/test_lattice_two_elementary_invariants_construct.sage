r"""Even 2-elementary lattices expose Nikulin's rank, length, and delta triple."""

from sage_extensions.all import *  # noqa: F401,F403


def test_unimodular_hyperbolic_plane_has_nikulin_invariants_two_zero_zero() -> None:
    lattice = NamedLattices.U
    invariants = lattice.two_elementary_invariants()

    assert invariants == (NN**3)((2, 0, 0))


def test_two_elementary_invariants_are_built_from_owned_lattice_invariants() -> None:
    lattice = NamedLattices.U

    assert lattice.two_elementary_invariants() == nikulin_invariants(
        lattice.rank(),
        lattice.discriminant_length(),
        lattice.delta(),
    )
