from sage_extensions.all import *


def a1_plus_a2():
    return Lattices(ZZ)("A1") + Lattices(ZZ)("A2")


def test_the_sum_and_the_block_gram_agree() -> None:
    assert a1_plus_a2() == Lattices(ZZ)([[-2, 0, 0], [0, -2, 1], [0, 1, -2]])


def test_the_categories_of_a1_plus_a2() -> None:
    lattice = a1_plus_a2()
    assert lattice in Lattices(ZZ)
    assert lattice in EvenLattices(ZZ)
    assert lattice in DirectSumObjects(Lattices(ZZ))


def test_the_invariants_of_a1_plus_a2() -> None:
    r"""$\det = \det A_1 \cdot \det A_2 = (-2)\cdot 3$; $A = \mathbb Z/2 \oplus \mathbb Z/3$."""
    lattice = a1_plus_a2()
    assert lattice.module_rank() == 3
    assert lattice.determinant() == -6
    assert lattice.signature_pair() == signature_pair(0, 3)
    assert lattice.discriminant_group().cardinality() == 6
    assert lattice.number_of_summands() == 2
    assert lattice.summands().cardinality() == 2
    assert lattice.summand(0).is_isometric(Lattices(ZZ)("A1"))
    assert lattice.summand(1).determinant() == 3


def test_the_roots_and_isometries_of_a1_plus_a2() -> None:
    r"""Roots: $2 + 6$.  The summands are not isometric, so $O = O(A_1)\times O(A_2)$ of order $2 \cdot 12$."""
    lattice = a1_plus_a2()
    assert lattice.roots().cardinality() == 8
    assert lattice.O().order() == 24


def test_a1_plus_a2_has_one_endomorphism_category() -> None:
    lattice = a1_plus_a2()
    endomorphisms = lattice.Mor(lattice)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert lattice.Mor(lattice) is endomorphisms
    assert identity * identity == identity
