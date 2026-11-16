r"""The weighted graph of a Gram tensor and the cuts between its consecutive blocks.

The Gram graph of a type-\((0,2)\) tensor \(G\) on a framed module has one vertex per
framing position and an edge \(\{i,j\}\) weighted \(G_{ij}\) whenever \(G_{ij}\ne0\).  A
cut is a position \(k\) such that the first \(k\) positions are a union of connected
components, so that \(G\) is block diagonal with blocks \([0,k)\) and \([k,n)\).

For \(A_2 \oplus A_1\) (Gram \(\operatorname{diag}(\begin{smallmatrix}-2&1\\1&-2\end{smallmatrix}, -2)\))
the only off-diagonal edge is \(\{0,1\}\), of weight 1, and the only cut is at 2.  For the
Gram \(\begin{pmatrix}-2&0&1\\0&-2&0\\1&0&-2\end{pmatrix}\) the components are \(\{0,2\}\)
and \(\{1\}\), which are not intervals, so there is no cut.
"""

from sage_extensions.all import *


def test_the_gram_graph_of_a2_plus_a1() -> None:
    lattice = Lattices(ZZ)("A2") + Lattices(ZZ)("A1")
    graph = lattice.gram_tensor().gram_graph()

    assert graph.has_edge(0, 1)
    assert not graph.has_edge(0, 2)
    assert not graph.has_edge(1, 2)
    assert graph.edge_weight(0, 1) == 1
    assert graph.edge_weight(2, 2) == -2


def test_the_only_block_cut_of_a2_plus_a1_is_after_the_a2_block() -> None:
    lattice = Lattices(ZZ)("A2") + Lattices(ZZ)("A1")
    cuts = lattice.gram_tensor().gram_connected_component_cuts()

    assert 2 in cuts
    assert not (1 in cuts)


def test_interleaved_components_give_no_block_cut() -> None:
    lattice = Lattices(ZZ)([[-2, 0, 1], [0, -2, 0], [1, 0, -2]])
    graph = lattice.gram_tensor().gram_graph()
    cuts = lattice.gram_tensor().gram_connected_component_cuts()

    assert graph.has_edge(0, 2)
    assert not (1 in cuts)
    assert not (2 in cuts)


def test_the_component_vertex_sets_of_a_gram_graph_do_not_depend_on_its_diagonal() -> None:
    r"""Every nonzero diagonal entry is a loop, and a loop joins no two vertices.

    The components of $A_2 \oplus A_1$ are $\{0,1\}$ and $\{2\}$; those of the
    Gram matrix with an interleaved block, $\{0,2\}$ and $\{1\}$, are not
    intervals, so they are components without a cut.
    """
    lattice = Lattices(ZZ)("A2") + Lattices(ZZ)("A1")
    interleaved = Lattices(ZZ)([[-2, 0, 1], [0, -2, 0], [1, 0, -2]])

    components = lattice.gram_tensor().gram_graph().connected_component_vertex_sets()
    assert {
        frozenset(int(position) for position in component)
        for component in components
    } == {frozenset({0, 1}), frozenset({2})}
    separate = interleaved.gram_tensor().gram_graph().connected_component_vertex_sets()
    assert {
        frozenset(int(position) for position in component)
        for component in separate
    } == {frozenset({0, 2}), frozenset({1})}


def test_a_graphs_component_vertex_sets_are_one_datum() -> None:
    r"""Asked twice, a graph's components are the datum it computed once.

    A component vertex set is derived object data of the graph, so the second
    reader of one graph reads what the first computed.  The datum is still the
    components themselves: each is a set of this graph's own vertices, and the
    two of $A_2 \oplus A_1$ are $\{0,1\}$ and $\{2\}$.
    """
    graph = (Lattices(ZZ)("A2") + Lattices(ZZ)("A1")).gram_tensor().gram_graph()
    components = graph.connected_component_vertex_sets()

    assert graph.connected_component_vertex_sets() is components
    assert {
        frozenset(int(position) for position in component) for component in components
    } == {frozenset({0, 1}), frozenset({2})}
    assert all(
        vertex in graph for component in components for vertex in component
    )
