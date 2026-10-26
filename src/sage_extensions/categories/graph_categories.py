r"""Owned finite graphs, digraphs, and labelled graph structures.

A finite digraph is a finite vertex set together with a binary adjacency
relation; its morphisms are vertex maps preserving adjacency.  An undirected
graph is the symmetric case.  A labelled graph or digraph additionally carries
vertex and edge labels, and its morphisms preserve those labels.  These are the
standard graph-homomorphism notions (see Diestel, *Graph Theory*, Chapter 1,
and Bang-Jensen--Gutin, *Digraphs*, Chapter 1).
"""

from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.logic import conjunction, negation
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class _FiniteDigraphEngine:
    r"""Private realization of one finite directed or symmetric graph."""

    def __init__(
        self,
        vertices,
        edges,
        *,
        symmetric=False,
        vertex_labels=None,
        edge_labels=None,
        **rest,
    ) -> None:
        self._vertices = finite_ordered_set(vertices)
        self._edge_space = self._vertices**2
        self._edges = finite_ordered_set(edges)
        self._symmetric = bool(symmetric)
        self._vertex_labels = vertex_labels
        self._edge_labels = edge_labels
        super().__init__(facade=True, **rest)

    def vertices(self):
        return self._vertices

    def edges(self):
        return self._edges

    def edge_space(self):
        return self._edge_space

    def __contains__(self, vertex) -> bool:
        return vertex in self.vertices()

    def _element_constructor_(self, vertex):
        return self.vertices()(vertex)

    def __iter__(self):
        return iter(self.vertices())

    def _cardinality_decision(self):
        return self.vertices().cardinality()

    def connected_component_vertex_sets(self):
        r"""The vertex sets of the connected components of the underlying undirected graph.

        An owned finite ordered set of owned finite ordered sets of vertices,
        each in vertex order.  Private computation of the graph owner: Sage's
        ``Graph`` computes the components on the vertex positions.
        """
        from sage.graphs.graph import Graph

        vertices = tuple(self.vertices())
        rank = self.vertices().ranking_map()
        graph = Graph([range(len(vertices)), [(int(rank(edge[0])), int(rank(edge[1]))) for edge in self.edges()]], format="vertices_and_edges")
        return finite_ordered_set(
            tuple(
                finite_ordered_set(tuple(vertices[position] for position in sorted(component)))
                for component in graph.connected_components(sort=False)
            )
        )

    def has_edge(self, left, right) -> bool:
        edge = self.edge_space()((left, right))
        reverse = self.edge_space()((right, left))
        return edge in self.edges() or (
            self._symmetric and reverse in self.edges()
        )

    def is_directed(self) -> bool:
        return not self._symmetric

    def is_symmetric(self) -> bool:
        return self._symmetric

    def vertex_label(self, vertex):
        if self._vertex_labels is None:
            raise ValueError(
                f"the vertex {vertex} has no label: this graph was constructed without "
                f"vertex labels"
            )
        return self._vertex_labels[vertex]

    def edge_label(self, left, right):
        if self._edge_labels is None:
            raise ValueError(
                f"the edge ({left}, {right}) has no label: this graph was constructed "
                f"without edge labels"
            )
        edge = self.edge_space()((left, right))
        reverse = self.edge_space()((right, left))
        match edge in self._edge_labels:
            case True:
                return self._edge_labels[edge]
            case False if self._symmetric and reverse in self._edge_labels:
                return self._edge_labels[reverse]
            case False:
                raise ValueError(
                    f"the vertices {left} and {right} have no edge label: they are not "
                    f"joined by an edge"
                )


@cached_function
def _finite_digraph_engine_with(mixin):
    r"""Compose one consumer's private realization with the graph owner's engine.

    The consumer supplies only its additional private operations/data.  The
    graph owner retains authority over vertices, edges, adjacency, labels and
    the underlying Parent realization.
    """
    return type(
        f"_{mixin.__name__.lstrip('_')}OnFiniteDigraph",
        (mixin, _FiniteDigraphEngine),
        {},
    )


class GraphMorphism:
    r"""A vertex map preserving directed adjacency."""

    def __init__(self, parent, set_morphism) -> None:
        self._set_morphism = set_morphism
        super().__init__(parent, set_morphism)

    def underlying_set_morphism(self):
        return self._set_morphism

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return self.parent()._from_graph_map(
            self.underlying_set_morphism() * other.underlying_set_morphism()
        )

    def __eq__(self, other):
        if element_parent(other) is not self.parent():
            return False
        return other.underlying_set_morphism() == self.underlying_set_morphism()

    def __ne__(self, other):
        return negation(self == other)

    __hash__ = None


class DigraphMor(CategoricalMor):
    r"""Adjacency-preserving vertex maps between represented digraphs."""

    ElementMethods = GraphMorphism

    def _graph_map_decision(self, morphism):
        return conjunction(
            self.codomain().has_edge(morphism(left), morphism(right))
            for left, right in self.domain().edges()
        )

    def _verify_graph_map(self, morphism) -> None:
        if self._graph_map_decision(morphism) is False:
            raise ValueError(
                f"{morphism} is not a graph morphism {self.domain()} -> {self.codomain()}: "
                "some directed edge is not carried to an edge"
            )

    def _element_constructor_(self, datum, *, check=False):
        if element_parent(datum) is self:
            return datum
        set_morphism = Sets().Mor(self.domain(), self.codomain())(datum)
        morphism = self.element_class(self, set_morphism)
        if check:
            self._verify_graph_map(morphism)
        return morphism

    def _from_graph_map(self, set_morphism):
        return self.element_class(self, set_morphism)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism from {self.domain()} to {self.codomain()}: "
                f"an identity needs its domain and codomain to be the same graph"
            )
        return self._from_graph_map(
            Sets().Mor(self.domain(), self.domain()).identity()
        )


class LabelledDigraphMor(DigraphMor):
    r"""Digraph morphisms preserving the selected vertex and edge labels."""

    def _graph_map_decision(self, morphism):
        return conjunction((
            super()._graph_map_decision(morphism),
            conjunction(
                self.domain().vertex_label(vertex)
                == self.codomain().vertex_label(morphism(vertex))
                for vertex in self.domain().vertices()
            ),
            conjunction(
                self.domain().edge_label(left, right)
                == self.codomain().edge_label(morphism(left), morphism(right))
                for left, right in self.domain().edges()
            ),
        ))


class DigraphMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = DigraphMor


class LabelledDigraphMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = LabelledDigraphMor


class Digraphs(OwnedCategory):
    r"""Finite directed graphs with graph homomorphisms."""

    _MorCategory = DigraphMorCategoryConstruction

    def super_categories(self):
        return [Sets().Finite()]

    @classmethod
    def _repr_object_names(cls):
        return "finite directed graphs"

    def an_object(self):
        return self.from_edges((0, 1), ((0, 1),))

    def from_edges(self, vertices, edges):
        vertices = finite_ordered_set(vertices)
        edge_space = vertices**2
        normalized = finite_ordered_set(tuple(edge_space(edge) for edge in edges))
        if any(
            edge[0] not in vertices or edge[1] not in vertices
            for edge in normalized
        ):
            raise ValueError(
                f"the edges {normalized} do not define a directed graph on the vertices "
                f"{vertices}: some edge has an endpoint that is not a vertex"
            )
        return _object_of(
            self,
            _engine=(self, _FiniteDigraphEngine, None),
            vertices=vertices,
            edges=normalized,
            symmetric=False,
        )


class Graphs(OwnedCategory):
    r"""Finite undirected graphs, viewed as symmetric directed graphs."""

    _MorCategory = DigraphMorCategoryConstruction

    def super_categories(self):
        return [Digraphs()]

    @classmethod
    def _repr_object_names(cls):
        return "finite graphs"

    def an_object(self):
        return self.from_edges((0, 1), ((0, 1),))

    def from_edges(self, vertices, edges):
        vertices = finite_ordered_set(vertices)
        edge_space = vertices**2
        normalized = finite_ordered_set(tuple(edge_space(edge) for edge in edges))
        if any(
            edge[0] not in vertices or edge[1] not in vertices
            for edge in normalized
        ):
            raise ValueError(
                f"the edges {normalized} do not define a graph on the vertices "
                f"{vertices}: some edge has an endpoint that is not a vertex"
            )
        return _object_of(
            self,
            _engine=(self, _FiniteDigraphEngine, None),
            vertices=vertices,
            edges=normalized,
            symmetric=True,
        )


class LabelledDigraphs(OwnedCategory):
    r"""Finite digraphs with selected vertex and edge labels."""

    _MorCategory = LabelledDigraphMorCategoryConstruction

    def super_categories(self):
        return [Digraphs()]

    @classmethod
    def _repr_object_names(cls):
        return "labelled finite directed graphs"

    def an_object(self):
        return self.from_labels(
            (0, 1),
            ((0, 1),),
            {0: "source", 1: "target"},
            {(0, 1): "arrow"},
        )

    def from_labels(self, vertices, edges, vertex_labels, edge_labels):
        vertices = finite_ordered_set(vertices)
        edge_space = vertices**2
        edges = finite_ordered_set(tuple(edge_space(edge) for edge in edges))
        if any(
            edge[0] not in vertices or edge[1] not in vertices
            for edge in edges
        ):
            raise ValueError(
                f"the edges {edges} do not define a directed graph on the vertices "
                f"{vertices}: some edge has an endpoint that is not a vertex"
            )
        if set(vertex_labels) != set(vertices):
            raise ValueError(
                f"the vertex labels {vertex_labels} do not label the vertices {vertices}: "
                f"a labelled directed graph has exactly one label per vertex"
            )
        normalized_edge_labels = {
            edge_space(edge): label for edge, label in edge_labels.items()
        }
        if set(normalized_edge_labels) != set(edges):
            raise ValueError(
                f"the edge labels {edge_labels} do not label the edges {edges}: a "
                f"labelled directed graph has exactly one label per edge"
            )
        return _object_of(
            self,
            _engine=(self, _FiniteDigraphEngine, None),
            vertices=vertices,
            edges=edges,
            symmetric=False,
            vertex_labels=dict(vertex_labels),
            edge_labels=normalized_edge_labels,
        )


class LabelledGraphs(OwnedCategory):
    r"""Finite undirected graphs with selected vertex and edge labels."""

    _MorCategory = LabelledDigraphMorCategoryConstruction

    def super_categories(self):
        return [Graphs(), LabelledDigraphs()]

    @classmethod
    def _repr_object_names(cls):
        return "labelled finite graphs"

    def an_object(self):
        return self.from_labels(
            (0, 1),
            ((0, 1),),
            {0: "left", 1: "right"},
            {(0, 1): "edge"},
        )

    def object(
        self,
        vertices,
        edges,
        vertex_labels,
        edge_labels,
        *,
        categories=(),
        construction_data=None,
        _engine=None,
    ):
        r"""Construct a labelled graph, optionally with stronger owned structure.

        ``LabelledGraphs`` owns the private finite-graph realization.  A
        mathematical specialization supplies only its additional category and
        construction data; it never imports or subclasses that private engine.
        """
        vertices = finite_ordered_set(vertices)
        edge_space = vertices**2
        edges = finite_ordered_set(tuple(edge_space(edge) for edge in edges))
        if any(
            edge[0] not in vertices or edge[1] not in vertices
            for edge in edges
        ):
            raise ValueError(
                f"the edges {edges} do not define a graph on the vertices {vertices}: "
                f"some edge has an endpoint that is not a vertex"
            )
        if set(vertex_labels) != set(vertices):
            raise ValueError(
                f"the vertex labels {vertex_labels} do not label the vertices {vertices}: "
                f"a labelled graph has exactly one label per vertex"
            )
        normalized_edge_labels = {
            edge_space(edge): label for edge, label in edge_labels.items()
        }
        if set(normalized_edge_labels) != set(edges):
            raise ValueError(
                f"the edge labels {edge_labels} do not label the edges {edges}: a "
                f"labelled graph has exactly one label per edge"
            )
        category = Cat().meet((self, *tuple(categories)))
        realization = (
            _FiniteDigraphEngine
            if _engine is None
            else _finite_digraph_engine_with(_engine)
        )
        return _object_of(
            category,
            _engine=(self, realization, None),
            vertices=vertices,
            edges=edges,
            symmetric=True,
            vertex_labels=dict(vertex_labels),
            edge_labels=normalized_edge_labels,
            **dict(construction_data or {}),
        )

    def from_labels(self, vertices, edges, vertex_labels, edge_labels):
        return self.object(vertices, edges, vertex_labels, edge_labels)


__all__ = [
    "Digraphs",
    "Graphs",
    "LabelledDigraphs",
    "LabelledGraphs",
]
