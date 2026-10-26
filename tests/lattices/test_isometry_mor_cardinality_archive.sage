r"""Cardinalities of sets of isometries ``Isom(L, M)`` of integral lattices."""

from sage_extensions.all import *


def test_the_even_and_odd_unimodular_planes_are_not_isometric() -> None:
    r"""``U`` is even and ``I_{1,1}`` is odd, so ``Isom(U, I_{1,1})`` is empty."""
    even = Lattices(ZZ)("U")
    odd = Lattices(ZZ)([[1, 0], [0, -1]])

    assert even.is_even()
    assert not odd.is_even()
    assert even.Isom(odd).is_empty()
    assert even.Isom(odd).cardinality() == 0


def test_A2_has_twelve_self_isometries() -> None:
    r"""``O(A_2) = W(A_2) x {+-1}`` has order ``2 * 3! = 12``.

    Conway--Sloane, SPLAG, Ch. 4, Sec. 6.1.
    """
    lattice = Lattices(ZZ)("A2")

    assert lattice.Isom(lattice).cardinality() == 12


def test_an_odd_indefinite_unimodular_plane_is_isometric_to_I_1_1() -> None:
    r"""``[[-3,-2],[-2,-1]]`` is odd, unimodular and indefinite, hence isometric to ``I_{1,1}``.

    It is ``diag(1,-1)`` in the basis ``(1,2),(0,1)``; odd indefinite unimodular
    lattices are classified by rank and signature (Serre, A Course in
    Arithmetic, Ch. V, Sec. 2.2).
    """
    source = Lattices(ZZ)([[1, 0], [0, -1]])
    target = Lattices(ZZ)([[-3, -2], [-2, -1]])

    assert not source.Isom(target).is_empty()
    assert source.Isom(target).cardinality() == 4
