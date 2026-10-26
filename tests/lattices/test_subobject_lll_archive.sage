r"""LLL reduction of a skew sublattice of \(\mathbb Z^4\)."""

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


def test_an_LLL_reduced_basis_spans_an_isometric_lattice_with_a_short_first_vector() -> None:
    r"""Reduction changes basis only, so \(\det = 1512^2 = 2286144\); an LLL-reduced
    basis (\(\delta = 3/4\)) has \(q(b_1) \le 2^{n-1}\lambda_1^2\) (Lenstra–Lenstra–Lovász,
    Math. Ann. 261 (1982), Prop. 1.11)."""
    sublattice = _skew_sublattice()

    reduced = sublattice.LLL()

    assert sublattice.determinant() == 2286144
    assert reduced.determinant() == 2286144
    assert reduced.is_isometric_to(sublattice)
    assert reduced.basis_vector(0).q() <= 8 * sublattice.minimum()
