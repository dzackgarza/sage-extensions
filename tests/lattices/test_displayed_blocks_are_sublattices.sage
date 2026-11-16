r"""The summands a displayed Gram matrix exhibits are sublattices of the lattice.

``LK3`` is presented by the block diagonal Gram matrix of
$U \oplus U \oplus U \oplus E_8(-1) \oplus E_8(-1)$: the components of its Gram
graph cut the displayed basis after positions 2, 4, 6 and 14, so the display
exhibits five summands, of ranks 2, 2, 2, 8, 8.  A summand is the span of its
components with the restricted form, so it is a sublattice with an inclusion
into the lattice and not a new Gram presentation of the same numbers, and the
summands pair to zero across each other.

The components need not be intervals: in
$\begin{pmatrix}-2&0&1\\0&-2&0\\1&0&-2\end{pmatrix}$ they are $\{0,2\}$ and
$\{1\}$, and the display still exhibits a summand of rank 2 and one of rank 1.
"""

from sage_extensions.all import *


def test_the_displayed_blocks_of_the_k3_gram_are_five_sublattices() -> None:
    lattice = NamedLattices.LK3
    summands = lattice.indecomposable_summands()
    ranks = tuple(int(summand.module_rank()) for summand in summands)

    assert ranks == (2, 2, 2, 8, 8)
    assert sum(ranks) == int(lattice.module_rank())
    assert all(summand.inclusion().codomain() is lattice for summand in summands)
    for summand in summands:
        for x in summand.module_generators():
            for y in summand.module_generators():
                assert summand.b(x, y) == lattice.b(summand.inclusion()(x), summand.inclusion()(y))
    for left in range(summands.cardinality()):
        for right in range(summands.cardinality()):
            if left == right:
                continue
            for x in summands[left].module_generators():
                for y in summands[right].module_generators():
                    assert lattice.b(
                        summands[left].inclusion()(x), summands[right].inclusion()(y)
                    ) == 0
    assert all(
        summands[position].is_isometric_to(NamedLattices.U)
        for position in range(3)
    )


def test_a_display_whose_blocks_are_not_intervals_exhibits_them_anyway() -> None:
    lattice = Lattices(ZZ)([[-2, 0, 1], [0, -2, 0], [1, 0, -2]])
    summands = lattice.indecomposable_summands()

    assert tuple(int(summand.module_rank()) for summand in summands) == (2, 1)
    assert all(summand.inclusion().codomain() is lattice for summand in summands)
    assert summands[0].is_isometric_to(Lattices(ZZ)("A2"))
    assert summands[1].is_isometric_to(Lattices(ZZ)("A1"))
