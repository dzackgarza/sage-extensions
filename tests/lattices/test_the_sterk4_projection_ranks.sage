r"""The Sterk4 projection's ranks, read from the library's own roots and permutation.

Sterk cell 20 projects the twenty-two roots of the ``(18,2,0)`` arrangement up to a
twenty-dimensional lattice along the ``+1`` eigenspace of a permutation of the formal
root basis.  Its saved output is ``(20, 12) 11`` followed by a failed assertion that the
rank is ten, so the stored eleven is evidence of what the cell computed and not a
certified answer: the number is recomputed here from the roots the library retains and
the permutation the cell states.

The roots ``v1 .. v22`` span eighteen of the lattice's twenty dimensions, so the matrix
``W`` of the roots in the selected basis has rank eighteen and a four-dimensional kernel,
the relations among the roots.  The permutation's ``+1`` eigenspace is the space of
vectors constant on its cycles, twelve-dimensional.  The projected rank is
``12 - dim(Fix cap ker W)``, and that intersection is computed from the same roots: it is
two-dimensional, so the rank is ten.

The later cells 29--31 build ``R(P - I)`` from the same displayed permutation and assert
their own ranks.  That is a different map of a different basis, and nothing here is read
from it.
"""

from sage_extensions.all import *


def _the_sterk4_roots():
    r"""The twenty-two roots in the Sterk4 order, the lattice's basis, and the lattice."""
    roots = Sterk.roots_18_2_0()
    order = Sterk.sterk4_root_order()
    lattice = roots[order[0]].parent()
    basis = tuple(lattice.module_generating_set())
    return tuple(roots[label] for label in order), basis, lattice, order


def _the_coordinates(roots, basis, lattice):
    r"""The coordinate vector of each root in the lattice's selected basis."""
    module = ZZ.free_module(int(lattice.module_rank()))
    return tuple(
        module(tuple(int(root.to_vector()(label)) for label in basis)) for root in roots
    )


def test_the_twenty_two_sterk4_roots_span_eighteen_of_the_twenty_dimensions() -> None:
    r"""The roots are a root system of the lattice, and they span eighteen dimensions.

    Each named root is a root of the lattice's form, of norm ``-2`` or ``-4``, and the
    matrix of the twenty-two in the selected basis has rank eighteen, so its kernel --
    the relations among the roots -- is four-dimensional.  The saved ``(20,12)`` states
    the lattice's dimension and the fixed space's, not this rank.
    """
    roots, basis, lattice, order = _the_sterk4_roots()
    coordinates = _the_coordinates(roots, basis, lattice)
    count = sum(1 for _ in order)
    roots_module = ZZ.free_module(count)
    module = ZZ.free_module(int(lattice.module_rank()))
    projection = roots_module.Mor(module)(
        {index: coordinates[index] for index in range(count)}
    )

    assert int(lattice.module_rank()) == 20
    assert all(lattice.q(root) in (ZZ(-2), ZZ(-4)) for root in roots)
    assert tuple(sorted(order)) == tuple(sorted(Sterk.roots_18_2_0()))
    assert int(projection.image().module_rank()) == 18
    assert int(projection.kernel().module_rank()) == 4


def test_the_sterk4_projection_has_rank_ten_and_not_the_stored_eleven() -> None:
    r"""The fixed space is twelve-dimensional, its intersection with the relations is two, and the rank is ten.

    A vector is fixed by the permutation exactly when it is constant on each of its
    cycles, so the fixed space has one dimension per cycle -- twelve of them.  Projecting
    the sum of the roots on each cycle gives the image of the fixed space: it has rank
    ten, so two independent relations are fixed, and the projection's rank is ``12 - 2``.
    """
    permutation = Sterk.sterk4_root_permutation()
    roots, basis, lattice, order = _the_sterk4_roots()
    coordinates = _the_coordinates(roots, basis, lattice)
    count = sum(1 for _ in order)
    module = ZZ.free_module(int(lattice.module_rank()))

    seen = set()
    cycles = []
    for start in range(count):
        if start in seen:
            continue
        cycle = []
        index = start
        while index not in seen:
            seen.add(index)
            cycle.append(index)
            index = permutation[index]
        cycles.append(tuple(cycle))

    assert sum(1 for _ in cycles) == 12
    assert sorted(sum(1 for _ in cycle) for cycle in cycles) == sorted(
        [1, 1] + [2] * 10
    )

    fixed_module = ZZ.free_module(sum(1 for _ in cycles))
    projection_on_the_fixed_space = fixed_module.Mor(module)(
        {
            index: sum(
                (coordinates[root] for root in cycle), module.zero()
            )
            for index, cycle in enumerate(cycles)
        }
    )
    rank = int(projection_on_the_fixed_space.image().module_rank())

    assert rank == 10
    assert rank != 11
    assert sum(1 for _ in cycles) - rank == 2
    assert int(projection_on_the_fixed_space.kernel().module_rank()) == 2
