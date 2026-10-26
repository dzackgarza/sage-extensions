r"""Lannér and quasi-Lannér diagrams among hyperbolic Coxeter simplices.

A connected Coxeter diagram of hyperbolic type is Lannér (compact simplex)
when every proper induced subdiagram is elliptic, and quasi-Lannér
(finite-volume, noncompact simplex) when every proper induced subdiagram is
elliptic or parabolic and at least one is parabolic (Vinberg, *Hyperbolic
reflection groups*, Russian Math. Surveys 40 (1985), §2 and Table 2).
"""

from sage_extensions.all import *


def triangle(first: int, second: int, third: int) -> list[list[int]]:
    r"""The Coxeter matrix of the triangle with bonds ``first`` (0-1), ``second`` (1-2), ``third`` (0-2)."""
    return [[1, first, third], [first, 1, second], [third, second, 1]]


def proper_subdiagrams(diagram):
    vertices = diagram.index_set()
    return [
        diagram.induced_subdiagram(
            Sets()([vertex for vertex in vertices if vertex != omitted])
        )
        for omitted in vertices
    ]


def test_the_two_three_seven_triangle_is_lanner() -> None:
    r"""The \((2,3,7)\) triangle is compact hyperbolic: \(1/2+1/3+1/7<1\), every edge elliptic."""
    diagram = CoxeterDiagrams()(triangle(3, 7, 2))

    assert diagram.is_hyperbolic()
    assert diagram.vinberg_invariant_matrix().is_compact_hyperbolic()
    assert not diagram.vinberg_invariant_matrix().is_crystallographic()
    assert all(subdiagram.is_elliptic() for subdiagram in proper_subdiagrams(diagram))


def test_the_tetrahedron_three_three_six_is_quasi_lanner() -> None:
    r"""The linear diagram \([3,3,6]\) is a finite-volume noncompact hyperbolic simplex.

    Its Schläfli form has signature \((3,1)\).  Omitting the first node leaves
    \([3,6]=\tilde G_2\), which is parabolic (an ideal vertex); the other three
    faces are \(A_1\times G_2\), \(A_2\times A_1\) and \(A_3\), all elliptic.
    It is the symmetry group of the hyperbolic honeycomb \(\{3,3,6\}\)
    (Vinberg, loc. cit., Table 2).
    """
    diagram = CoxeterDiagrams()(
        [[1, 3, 2, 2], [3, 1, 3, 2], [2, 3, 1, 6], [2, 2, 6, 1]]
    )
    faces = proper_subdiagrams(diagram)

    assert diagram.is_hyperbolic()
    assert diagram.vinberg_invariant_matrix().is_paracompact_hyperbolic()
    assert not diagram.vinberg_invariant_matrix().is_compact_hyperbolic()
    assert all(face.is_elliptic() or face.is_parabolic() for face in faces)
    assert sum(1 for face in faces if face.is_parabolic()) == 1


def test_a2_affine_a2_and_the_two_three_seven_triangle_are_elliptic_parabolic_and_hyperbolic() -> None:
    r"""\(A_2\) is elliptic, \(\tilde A_2\) is parabolic, \((2,3,7)\) is hyperbolic, and no two agree."""
    elliptic = CoxeterDiagrams()([[1, 3], [3, 1]])
    parabolic = CoxeterDiagrams()(triangle(3, 3, 3))
    hyperbolic = CoxeterDiagrams()(triangle(3, 7, 2))

    assert elliptic.is_elliptic()
    assert not elliptic.is_parabolic()
    assert not elliptic.is_hyperbolic()
    assert parabolic.is_parabolic()
    assert not parabolic.is_elliptic()
    assert not parabolic.is_hyperbolic()
    assert hyperbolic.is_hyperbolic()
    assert not hyperbolic.is_elliptic()
    assert not hyperbolic.is_parabolic()
