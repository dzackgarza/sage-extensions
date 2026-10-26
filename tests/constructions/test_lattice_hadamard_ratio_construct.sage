r"""An orthonormal lattice basis has Hadamard ratio one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_rank_two_lattice_has_hadamard_ratio_one() -> None:
    lattice = Lattices(ZZ)(ZZ^2)

    assert lattice.hadamard_ratio() == 1
