r"""The orthogonal group is the lattice automorphism isometry group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_orthogonal_group_is_its_automorphism_group() -> None:
    lattice = NamedLattices.A1

    assert lattice.orthogonal_group() is lattice.Aut()
