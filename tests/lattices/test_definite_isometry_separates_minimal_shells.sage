r"""A definite isometry decision separates two lattices of one genus whose minimal shells differ.

The orthogonal complements of the primitive vectors (-1, -5, 0, ..., 0) and
(-2, -3, -1, 1, 1, -2, -2, -2, 2, -1) of square 10 in the even unimodular lattice of signature
(1, 9) (Brandhorst--Gonzalez-Alonso's E10 Gram) are definite of rank 9 and determinant 10, and lie
in one genus. The Gram matrices below are those complements, negated and LLL-reduced. The first is
`E_8 + <10>`, with the 240 roots of `E_8`; the second has 128 vectors of square 2, the roots of
`E_7 + A_1` (J. H. Conway and N. J. A. Sloane, *Sphere packings, lattices and groups*, Ch. 4,
Table 4.10). An isometry preserves the set of minimal vectors, so they are not isometric. The
second does not split by Kneser's construction (its root span does not split off orthogonally), so
no summand-by-summand decision applies, and PARI's `qfisom` on the whole pair enumerates every
vector of `E_8 + <10>` up to square 10.
"""

from sage_extensions.all import *

E8_PLUS_10 = [
    [2, -1, 1, -1, -1, -1, 1, 1, 0],
    [-1, 2, 0, 0, 0, 1, -1, -1, 0],
    [1, 0, 2, 0, -1, -1, 1, 1, 0],
    [-1, 0, 0, 2, 1, 0, 0, 0, 0],
    [-1, 0, -1, 1, 2, 1, -1, 0, 0],
    [-1, 1, -1, 0, 1, 2, -1, -1, 0],
    [1, -1, 1, 0, -1, -1, 2, 1, 0],
    [1, -1, 1, 0, 0, -1, 1, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 10],
]
E7_PLUS_A1_GLUED = [
    [2, -1, 1, -1, -1, -1, -1, 0, 1],
    [-1, 2, 0, 0, 0, 1, 1, 0, -1],
    [1, 0, 2, 0, -1, -1, -1, 0, 1],
    [-1, 0, 0, 2, 1, 0, 0, 0, 0],
    [-1, 0, -1, 1, 2, 1, 0, 0, -1],
    [-1, 1, -1, 0, 1, 2, 1, 0, -1],
    [-1, 1, -1, 0, 0, 1, 2, 0, -1],
    [0, 0, 0, 0, 0, 0, 0, 2, 0],
    [1, -1, 1, 0, -1, -1, -1, 0, 4],
]


def test_complements_of_two_square_ten_vector_orbits_in_e10_are_not_isometric() -> None:
    first = Lattices(ZZ)(E8_PLUS_10)
    second = Lattices(ZZ)(E7_PLUS_A1_GLUED)
    assert first.genus() == second.genus()

    assert first.is_isometric_to(second) is False
