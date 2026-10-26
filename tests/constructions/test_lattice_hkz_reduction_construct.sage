r"""HKZ reduction returns an isometric reframing of the same lattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_square_lattice_hkz_reduction_preserves_rank_and_determinant() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    reduction = lattice.hkz_reduction()

    assert reduction.reduced.rank() == cardinal(2)
    assert abs(reduction.reduced.determinant()) == 1
    assert reduction.isometry.domain() is reduction.reduced
    assert reduction.isometry.codomain() is lattice
