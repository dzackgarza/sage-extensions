r"""A negative-semidefinite rank-two lattice with one-dimensional radical is parabolic."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_negative_semidefinite_lattice_with_radical_is_parabolic() -> None:
    lattice = Lattices(ZZ)([[-1, 0], [0, 0]])

    assert lattice.is_parabolic()


def test_negative_definite_a1_is_not_parabolic() -> None:
    assert not NamedLattices.A1.is_parabolic()
