r"""BKZ and HKZ reduction of a skew sublattice of \(\mathbb Z^4\)."""

from sage_extensions.all import *


def _skew_sublattice():
    r"""Spanned by a triangular basis with diagonal \(9, 4, 7, 6\): index \(1512\)."""
    ambient = Lattices(ZZ)(4)
    e = ambient.module_generators()
    return ambient.sublattice_from(
        (
            9 * e[0] + 13 * e[1],
            4 * e[1] + 11 * e[2],
            7 * e[2] + 5 * e[3],
            6 * e[3],
        )
    )


def test_an_HKZ_reduced_basis_begins_with_a_shortest_vector() -> None:
    r"""By definition the first vector of a Hermite–Korkine–Zolotarev reduced basis
    realizes \(\lambda_1\); reduction preserves \(\det = 1512^2 = 2286144\)."""
    sublattice = _skew_sublattice()

    reduced = sublattice.HKZ()

    assert reduced.determinant() == 2286144
    assert reduced.is_isometric_to(sublattice)
    assert reduced.basis_vector(0).q() == sublattice.minimum()


def test_a_BKZ_reduced_basis_meets_the_LLL_bound() -> None:
    r"""A BKZ-reduced basis of block size \(\ge 2\) is LLL-reduced, so
    \(q(b_1) \le 2^{n-1}\lambda_1^2 = 8\lambda_1^2\) for \(n = 4\)."""
    sublattice = _skew_sublattice()

    reduced = sublattice.BKZ(block_size=2)

    assert reduced.determinant() == 2286144
    assert reduced.is_isometric_to(sublattice)
    assert reduced.basis_vector(0).q() <= 8 * sublattice.minimum()
