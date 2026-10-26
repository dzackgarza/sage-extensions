r"""BKZ and HKZ return isometric reduced framings of a lattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_BKZ_preserves_rank_and_determinant() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    reduced = lattice.BKZ(block_size=2)

    assert reduced.rank() == cardinal(2)
    assert abs(reduced.determinant()) == 1
    assert lattice.is_isometric(reduced)


def test_square_lattice_HKZ_preserves_rank_and_determinant() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    reduced = lattice.HKZ()

    assert reduced.rank() == cardinal(2)
    assert abs(reduced.determinant()) == 1
    assert lattice.is_isometric(reduced)
