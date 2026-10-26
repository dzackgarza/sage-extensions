"""Shared operations on finite Gram tensors."""

from itertools import accumulate

import networkx as nx

from sage_extensions.categories.graph_categories import (
    LabelledGraphs,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.tensors.tensor import tensor


class _GramTensorGraphEngine:
    r"""Private Gram-specific data layered through ``LabelledGraphs.object``."""

    def __init__(self, base_ring, gram_tensor, **rest) -> None:
        self._gram_base_ring = base_ring
        self._gram_tensor = gram_tensor
        super().__init__(**rest)

    def base_ring(self):
        return self._gram_base_ring

    def edge_weight(self, left, right):
        r"""Return ``w({left, right})``, defined on the edges of this graph."""
        return self.edge_label(left, right)

    def tensor(self):
        r"""Recover the represented type-``(0,2)`` Gram tensor exactly."""
        return self._gram_tensor

    def _engine_graph(self):
        r"""Return the private NetworkX graph used for connectivity algorithms.

        Engine adapter (``OWN-06``): this is the one lowering of the owned
        labelled graph into ``networkx.Graph``.  Only connectivity data leaves
        this method.
        """
        graph = nx.Graph()
        graph.add_nodes_from(tuple(self.vertices()))
        graph.add_weighted_edges_from(
            (left, right, self.edge_weight(left, right))
            for left, right in self.edges()
        )
        return graph

    def connected_component_cuts(self):
        r"""Return cuts between consecutive connected diagonal blocks.

        NetworkX remains private to this owner; the mathematical output is
        only the ordered integer cut positions.
        """
        n = int(self.vertices().cardinality())
        if n <= 1:
            return finite_ordered_set(())
        graph = self._engine_graph()
        graph.remove_edges_from(list(nx.selfloop_edges(graph)))
        components = sorted(
            (sorted(component) for component in nx.connected_components(graph)),
            key=lambda component: component[0],
        )
        if [index for component in components for index in component] != list(range(n)):
            return finite_ordered_set(())
        return finite_ordered_set(
            tuple(NN(cut) for cut in accumulate(len(component) for component in components[:-1]))
        )

    def _repr_(self) -> str:
        return f"Gram graph on {self.vertices().cardinality()} framing positions"


def _gram_tensor_graph(gram):
    r"""Return the owned weighted graph presented by a symmetric Gram tensor."""
    if gram.tensor_valence() != (NN**2)((0, 2)):
        raise TypeError(
            f"a Gram tensor has type (0, 2), but {gram} has type {gram.tensor_valence()}"
        )
    n, m = gram.tensor_shape()
    if n != m:
        raise ValueError(f"a Gram tensor is square, but {gram} has shape {n} x {m}")
    if any(gram[i, j] != gram[j, i] for i in range(n) for j in range(i, n)):
        raise ValueError(f"a Gram tensor is symmetric, but {gram} is not")
    vertices = finite_ordered_set(tuple(range(n)))
    edge_space = vertices**2
    edges = finite_ordered_set(
        tuple(
            edge_space((i, j))
            for i in range(n)
            for j in range(i, n)
            if gram[i, j] != gram.base_ring().zero()
        )
    )
    return LabelledGraphs().object(
        vertices,
        edges,
        {vertex: vertex for vertex in vertices},
        {edge: gram[int(edge[0]), int(edge[1])] for edge in edges},
        construction_data={
            "base_ring": gram.base_ring(),
            "gram_tensor": gram,
        },
        _engine=_GramTensorGraphEngine,
    )


def _tensor_connected_component_cuts(gram):
    r"""Return cuts between consecutive connected diagonal blocks.

    Engine adapter (`OWN-06`): NetworkX computes the connected components of
    the Gram graph lowered by its declared NetworkX adapter; only
    integer positions leave this function.
    """
    if gram.tensor_order() != 2:
        raise TypeError(
            f"cutting a Gram tensor into connected blocks needs a tensor with two indices, but {gram} has "
            f"{gram.tensor_order()}"
        )
    return gram.gram_graph().connected_component_cuts()


__all__ = []
