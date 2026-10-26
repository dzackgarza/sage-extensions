from sage_extensions.all import *


def _d16_plus_gram():
    r"""Gram rows of \(D_{16}^+\) on the basis \(2e_1,\ e_2-e_1,\dots,e_{15}-e_{14},\ h\)
    with \(h=\tfrac12(e_1+\dots+e_{16})\) in \(\mathbb Z^{16}\); these sixteen vectors
    span \(D_{16}\) together with \(h\)."""
    def entry(i, j):
        if i == j:
            return 4 if i in (0, 15) else 2
        if {i, j} == {0, 1}:
            return -2
        if {i, j} == {0, 15}:
            return 1
        if 1 <= i <= 14 and 1 <= j <= 14 and abs(i - j) == 1:
            return -1
        return 0

    return [[entry(i, j) for j in range(16)] for i in range(16)]


def test_isometric_complements_give_isometric_eichler_lattices() -> None:
    r"""An isometry \(K \to K'\) extends by the identity on \(2U\) to
    \(2U \oplus K \to 2U \oplus K'\); here \(K = A_2\) and \(K'\) is \(A_2\) given by
    its Gram matrix."""
    source = Lattices(ZZ)("A2").two_u_eichler_model().lattice()
    target = Lattices(ZZ)([[-2, 1], [1, -2]]).two_u_eichler_model().lattice()

    assert source.is_isometric_to(target)
    witness = source.isometry_to(target)
    assert witness.domain() is source
    assert witness.codomain() is target


def test_2U_plus_A2_is_not_isometric_to_2U_plus_2A1() -> None:
    r"""The determinants differ: \(\det(2U \oplus A_2) = 3\) while
    \(\det(2U \oplus A_1^2) = 4\)."""
    source = Lattices(ZZ)("A2").two_u_eichler_model().lattice()
    target = (Lattices(ZZ)("A1") + Lattices(ZZ)("A1")).two_u_eichler_model().lattice()

    assert not source.is_isometric_to(target)
    assert source.isometry_to(target) is None


def test_2U_plus_E8_squared_is_isometric_to_2U_plus_D16_plus_with_nonisometric_complements() -> None:
    r"""Both \(2U \oplus E_8(-1)^2\) and \(2U \oplus D_{16}^+(-1)\) are even unimodular,
    indefinite, of rank 20 and signature (2, 18). An indefinite inner product space
    over \(\mathbf Z\) is determined by its rank, type and signature
    (Milnor--Husemoller, *Symmetric Bilinear Forms*, Ch. II, intro and Sec. 4--5,
    proof following Serre), so they are isometric. Their complements are not:
    \(E_8 \oplus E_8\) and \(D_{16}^+\) are the two inequivalent even unimodular
    16-dimensional lattices (Conway--Sloane, *Sphere Packings*, Ch. 2, Sec. 2.3,
    after Witt). This is the pair on which deciding \(2U \oplus K\) by \(K\) fails
    (research#402)."""
    e8_squared = Lattices(ZZ)("E8").twist(-1) + Lattices(ZZ)("E8").twist(-1)
    d16_plus = Lattices(ZZ)(_d16_plus_gram()).twist(-1)
    source = e8_squared.two_u_eichler_model().lattice()
    target = d16_plus.two_u_eichler_model().lattice()

    assert not e8_squared.is_isometric_to(d16_plus)
    assert source.is_isometric_to(target)
    witness = source.isometry_to(target)
    assert witness.domain() is source
    assert witness.codomain() is target
