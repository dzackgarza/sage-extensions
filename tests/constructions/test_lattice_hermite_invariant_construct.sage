r"""The standard square lattice has Hermite invariant one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_rank_two_lattice_has_hermite_invariant_one() -> None:
    lattice = Lattices(ZZ)(ZZ^2)

    assert lattice.hermite_invariant() == 1
