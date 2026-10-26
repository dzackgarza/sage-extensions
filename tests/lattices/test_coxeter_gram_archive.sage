r"""Root lattices of Coxeter diagrams: determinants, signatures and radicals.

A Coxeter diagram is given by its Coxeter matrix \(M\), with \(M_{vv}=1\) and
\(M_{vw}=m_{vw}\).  For a simply-laced diagram the root lattice has roots of
square \(-2\) (this repository's negative-definite convention) pairing to
\(1\) along a bond \(3\) and to \(0\) along a bond \(2\).
"""

from sage_extensions.all import *


def path_coxeter_matrix(rank: int, bond: int = 3) -> list[list[int]]:
    r"""The Coxeter matrix of the path on ``rank`` nodes with every bond ``bond``."""
    return [
        [1 if i == j else (bond if abs(i - j) == 1 else 2) for j in range(rank)]
        for i in range(rank)
    ]


def test_the_a2_root_lattice_has_determinant_three_and_is_negative_definite() -> None:
    r"""The \(A_2\) root lattice has Gram \([[-2,1],[1,-2]]\), determinant \(3\), signature \((0,2)\)."""
    lattice = CoxeterDiagrams()(path_coxeter_matrix(2)).root_lattice()

    assert lattice.gram_matrix().determinant() == 3
    assert lattice.signature_pair() == signature_pair(0, 2)
    assert lattice.is_nondegenerate()


def test_the_a_n_root_lattice_has_determinant_signed_n_plus_one() -> None:
    r"""\(\det A_n = (-1)^n (n+1)\) for the negative-definite \(A_n\), of signature \((0,n)\).

    The positive-definite Cartan matrix of \(A_n\) has determinant \(n+1\)
    (Humphreys, *Introduction to Lie Algebras*, 11.4); negating an
    \(n\times n\) matrix multiplies the determinant by \((-1)^n\).
    """
    for rank, determinant in ((1, -2), (2, 3), (3, -4), (4, 5)):
        lattice = CoxeterDiagrams()(path_coxeter_matrix(rank)).root_lattice()

        assert lattice.module_rank() == rank
        assert lattice.gram_matrix().determinant() == determinant
        assert lattice.signature_pair() == signature_pair(0, rank)


def test_the_affine_a2_gram_is_degenerate_with_a_rank_one_radical() -> None:
    r"""The affine \(\tilde A_2\) Gram has determinant \(0\), signature \((0,2)\), radical of rank \(1\).

    The radical is spanned by \(e_1+e_2+e_3\), the null root: each row of
    \([[-2,1,1],[1,-2,1],[1,1,-2]]\) sums to zero.  The triangle diagram with
    every bond \(3\) is therefore parabolic and not elliptic.
    """
    lattice = Lattices(ZZ)([[-2, 1, 1], [1, -2, 1], [1, 1, -2]])
    diagram = CoxeterDiagrams()([[1, 3, 3], [3, 1, 3], [3, 3, 1]])

    assert lattice.gram_matrix().determinant() == 0
    assert lattice.signature_pair() == signature_pair(0, 2)
    assert lattice.radical().module_rank() == 1
    assert diagram.is_parabolic()
    assert not diagram.is_elliptic()


def test_two_roots_pairing_to_three_span_a_hyperbolic_plane_and_a_hyperbolic_diagram() -> None:
    r"""Roots with Gram \([[-2,3],[3,-2]]\) span a lattice of determinant \(-5\) and signature \((1,1)\).

    Since \(3^2 > (-2)(-2)\) the mirrors are ultraparallel, so the diagram of
    the two roots is neither elliptic nor parabolic but hyperbolic.
    """
    lattice = Lattices(ZZ)([[-2, 3], [3, -2]])
    diagram = CoxeterDiagrams()(lattice.module_generators())

    assert lattice.gram_matrix().determinant() == -5
    assert lattice.signature_pair() == signature_pair(1, 1)
    assert not diagram.is_elliptic()
    assert not diagram.is_parabolic()
    assert diagram.is_hyperbolic()
