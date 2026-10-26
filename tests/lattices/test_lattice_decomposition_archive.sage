r"""Orthogonal decomposition of definite lattices into indecomposables."""

from sage_extensions.all import *


def test_a_skew_gram_presentation_of_A1_plus_A1_splits_into_two_copies_of_A1() -> None:
    r"""In the basis \((r_1, r_1 + r_2)\) of \(A_1 \oplus A_1\) the Gram matrix is
    \(\begin{pmatrix}-2&-2\\-2&-4\end{pmatrix}\); a definite lattice decomposes
    uniquely into indecomposables (Eichler; Kitaoka, Arithmetic of Quadratic
    Forms, Thm. 6.7.1)."""
    lattice = Lattices(ZZ)([[-2, -2], [-2, -4]])
    root_line = Lattices(ZZ)("A1")

    summands = lattice.indecomposable_summands()

    assert lattice.is_decomposable()
    assert summands.cardinality() == 2
    assert all(summand.is_isometric_to(root_line) for summand in summands)


def test_A2_is_indecomposable() -> None:
    r"""A splitting of \(A_2\) would be \(\langle a\rangle\oplus\langle b\rangle\) with
    \(ab = \det A_2 = 3\) and \(a, b\) even, since \(A_2\) is even; no such pair exists."""
    assert not Lattices(ZZ)("A2").is_decomposable()
