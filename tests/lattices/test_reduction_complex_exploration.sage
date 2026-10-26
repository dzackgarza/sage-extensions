r"""The four coordinate quadrants tile \(\mathbb R^2\) and their face pairings generate \(O(I_2)\)."""

from sage_extensions.all import *


def test_the_four_quadrants_pair_every_facet_and_their_transporters_generate_O_of_I2() -> None:
    r"""Each quadrant has two rays, each shared with exactly one neighbouring quadrant,
    so the cyclic chain of four adjacencies pairs all eight facet incidences.  The
    transporters between neighbours map one quadrant onto the next; together with the
    cell stabilizers they generate the signed permutation group \(O(I_2)\) of order 8.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    group = lattice.O()
    first = lattice.reduction_cell(((1, 0), (0, 1)))
    second = lattice.reduction_cell(((-1, 0), (0, 1)))
    third = lattice.reduction_cell(((-1, 0), (0, -1)))
    fourth = lattice.reduction_cell(((1, 0), (0, -1)))
    pairs = ((first, second), (second, third), (third, fourth), (fourth, first))

    cells = Sets()((first, second, third, fourth))
    adjacencies = Sets()(tuple(source.adjacency_to(target, group) for source, target in pairs))
    exploration = lattice.reduction_complex_exploration(cells, adjacencies, complete=True)

    assert group.cardinality() == 8
    assert exploration.is_complete()
    assert exploration.unpaired_facets().cardinality() == 0
    assert exploration.adjacencies().cardinality() == 4
    for adjacency in exploration.adjacencies():
        assert adjacency.common_face().dimension() == 1
        assert adjacency.source().transported_by(adjacency.transporter()).is_equal_to(
            adjacency.target()
        )
    assert exploration.generation_is_full(group)
