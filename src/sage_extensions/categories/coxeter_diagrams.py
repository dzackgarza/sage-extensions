r"""Finite Coxeter diagrams, optionally rooted in an integral lattice."""

from itertools import combinations

from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.root_system.coxeter_matrix import CoxeterMatrix
from sage.graphs.graph import Graph
from sage.matrix.constructor import matrix as sage_matrix
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.infinity import Infinity
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.graph_categories import LabelledGraphs
from sage_extensions.categories.lattices import Lattices
from sage_extensions.categories.rings.ring_foundation import (
    OwnedRings,
    _cross_engine_ring_value,
    _engine_element,
    _engine_numeral,
    _engine_ring,
    _owned_engine_element,
    _own_ring,
    _owned_integers,
    _owned_real_algebraic_numbers,
)
from sage_extensions.categories.sets.cardinals import Cardinalities, aleph0, cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    finite_indexed_family_from_values,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import (
    PartiallyOrderedSets,
    Sets,
    finite_ordinal_set,
)
from sage_extensions.logic import conjunction, negation
from sage_extensions.validation import validator
from sage_extensions.tensors.tensor import _engine_component_matrix, tensor
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def _engine_cartan_type_data(value):
    r"""Lower owned session numerals before Sage parses Cartan presentation data."""
    match value:
        case list():
            return [_engine_cartan_type_data(entry) for entry in value]
        case tuple():
            return tuple(_engine_cartan_type_data(entry) for entry in value)
    parent = element_parent(value)
    if parent is not None and parent in OwnedRings():
        return _engine_numeral(_owned_integers(), value)
    return value


@cached_function
def _coxeter_entry(ring, q1, q2, pairing):
    r"""Return the Coxeter matrix entry of the mirrors of two roots with squares ``q1``, ``q2``.

    The angle \(\theta\) between the mirrors satisfies
    \(4\cos^2\theta = 4b^2/(q_1 q_2)\) for the pairing \(b\).  The entry
    is the \(m\geq 2\) with \(4\cos^2(\pi/m)\) equal to it, for any natural
    number \(m\), and \(m=\aleph_0\) when the value is at least \(4\)
    (parallel or divergent mirrors).  Private adapter: the values of the
    owned ring ``ring`` are compared in Sage's real algebraic numbers, and a
    candidate \(m\) read off a floating approximation of the angle is
    accepted only when \(\left(\zeta_{2m}+\zeta_{2m}^{-1}\right)^2\) equals the
    value exactly.  An angle that is not \(\pi/m\) has no Coxeter entry.
    """
    from math import acos, pi

    from sage.rings.qqbar import AA as SageAA, QQbar

    q1, q2, pairing = (SageAA(_engine_element(ring, value)) for value in (q1, q2, pairing))
    assert q1 != 0 and q2 != 0, (
        f"cannot compute the Coxeter angle of two vectors with squares {q1} and {q2}: "
        f"a root must have nonzero square"
    )
    four_cos_squared = 4 * pairing**2 / (q1 * q2)
    if four_cos_squared >= 4:
        return aleph0
    order = round(pi / acos(float(four_cos_squared.sqrt()) / 2))
    zeta = QQbar.zeta(2 * order)
    if order >= 2 and (zeta + ~zeta) ** 2 == QQbar(four_cos_squared):
        return cardinal(order)
    raise ValueError(
        f"two roots with squares {q1}, {q2} and pairing {pairing} meet at an angle that is not "
        f"pi/m for any natural number m: 4 cos^2 of the angle is {four_cos_squared}"
    )


def _engine_coxeter_matrix_entry(entry):
    r"""Lower a Coxeter matrix entry to Sage's matrix entry, which writes \(\aleph_0\) as ``-1``.

    The entry \(m_{vw}\) is the order of \(s_v s_w\), so an owned cardinal is finite or
    \(\aleph_0\); an integer literal is lowered to Sage's integers.
    """
    match entry:
        case _ if entry in Cardinalities() and entry.is_countably_infinite():
            return SageZZ(-1)
        case _ if entry in Cardinalities():
            assert entry.is_finite(), (
                f"{entry} is not the order of an element of a Coxeter group: that order is a "
                f"positive integer or aleph_0"
            )
            return SageZZ(int(entry))
        case _:
            return _engine_cartan_type_data(entry)


def _engine_coxeter_matrix_of(coxeter_matrix):
    r"""Lower an owned Coxeter matrix \(m\colon V\times V\to\mathrm{Card}\) to Sage.

    The result is the Sage ``CoxeterMatrix`` on the index set \(V\), read off
    the first coordinates of the pairs in their order, with entry
    \(m(v,w)\) and \(\aleph_0\) written ``-1``.
    """
    values = {(pair[0], pair[1]): value for pair, value in coxeter_matrix.items()}
    vertices = tuple(dict.fromkeys(left for left, _right in values))
    return CoxeterMatrix(
        [[_engine_coxeter_matrix_entry(values[left, right]) for right in vertices] for left in vertices],
        index_set=vertices,
    )


def _coxeter_entry_cardinal(entry):
    r"""Read one Coxeter matrix entry \(m_{vw}\) as an owned cardinal.

    \(m_{vw}\) is the order of \(s_v s_w\): a positive integer, or
    \(\aleph_0\) (``aleph0``) for an element of infinite order.  An entry
    computed by a private Sage adapter may arrive as Sage's ``Infinity`` or
    as ``-1``, Sage's spelling of \(\infty\) in a ``CoxeterMatrix``.
    """
    match entry:
        case _ if entry in Cardinalities():
            return entry
        case _ if entry is Infinity or entry == -1:
            return aleph0
        case _:
            order = int(entry)
            assert order >= 1, (
                f"{entry} is not a Coxeter matrix entry: m_vw is the order of s_v s_w, a positive "
                f"integer, or aleph0 when that order is infinite"
            )
            return cardinal(order)


def _coxeter_entries_of(coxeter_matrix):
    r"""The values \(m(v,w)\) of an owned Coxeter matrix, keyed by the pair of vertices.

    Private realization of the function \(m\colon V\times V\to\mathrm{Card}\)
    stored by a diagram: it is read once from the defining family, and every
    entry lookup reads it.
    """
    return {(pair[0], pair[1]): _coxeter_entry_cardinal(value) for pair, value in coxeter_matrix.items()}


def _owned_coxeter_matrix(vertices, entries):
    r"""The owned Coxeter matrix \(m\colon V\times V\to\mathrm{Card}\) on the owned finite set ``vertices``.

    ``entries`` is keyed by pairs of elements of ``vertices``.
    """
    return indexed_family(
        vertices**2,
        lambda pair: entries[pair[0], pair[1]],
        name="Coxeter matrix",
    )


def _coxeter_matrix_of_rows(rows):
    r"""The owned Coxeter matrix whose vertices are the row positions of ``rows``."""
    rows = tuple(tuple(row) for row in rows)
    vertices = finite_ordered_set(tuple(position for position, _row in enumerate(rows)))
    labels = tuple(vertices)
    return _owned_coxeter_matrix(
        vertices,
        {
            (labels[left], labels[right]): _coxeter_entry_cardinal(entry)
            for left, row in enumerate(rows)
            for right, entry in enumerate(row)
        },
    )


def _coxeter_matrix_of_cartan_label(label):
    r"""The owned Coxeter matrix of the Cartan type named by the plain data ``[letter, rank(, affine)]``.

    Private adapter: Sage's ``CartanType`` and ``CoxeterMatrix`` read the
    label and supply the entries, which are raised to owned cardinals on the
    index set Sage assigns to the type.
    """
    engine = CoxeterMatrix(CartanType(_engine_cartan_type_data(list(label))))
    engine_vertices = tuple(engine.index_set())
    vertices = finite_ordered_set(engine_vertices)
    owned = dict(zip(engine_vertices, vertices, strict=True))
    return _owned_coxeter_matrix(
        vertices,
        {
            (owned[left], owned[right]): _coxeter_entry_cardinal(engine[left, right])
            for left in engine_vertices
            for right in engine_vertices
        },
    )


class CoxeterDiagramMorphism:
    r"""A vertex map preserving every Coxeter matrix entry.

    A Coxeter diagram is its symmetric matrix ``(m_vw)``.  A morphism sends
    vertices to vertices and preserves that entire matrix, including the
    entries ``m=2`` that are omitted from the drawn graph.  Thus composition
    is ordinary composition of the underlying vertex maps.
    """

    def __init__(self, parent, function) -> None:
        self._vertex_function = function
        super().__init__(
            parent,
            Sets().Mor(parent.domain(), parent.codomain())(function),
        )

    def __call__(self, vertex):
        source_vertex = self.domain().index_set()(vertex)
        return self.codomain().index_set()(self._vertex_function(source_vertex))

    def __mul__(self, other):
        if not _precomposable(self, other) or other.domain() not in CoxeterDiagrams():
            return NotImplemented
        return CoxeterDiagrams().Mor(other.domain(), self.codomain())(
            lambda vertex: self(other(vertex))
        )

    def __eq__(self, other):
        if element_parent(other) is not self.parent():
            return False
        return conjunction(
            self(vertex) == other(vertex) for vertex in self.domain().index_set()
        )

    def __ne__(self, other):
        return negation(self == other)

    def __hash__(self) -> int:
        return hash(
            (
                id(self.parent()),
                tuple(self(vertex) for vertex in self.domain().index_set()),
            )
        )

    def images(self):
        r"""Return the images in source-vertex order."""
        return finite_ordered_set(
            tuple(self(vertex) for vertex in self.domain().index_set())
        )

    def is_identity(self):
        if self.domain() is not self.codomain():
            return False
        return conjunction(
            self(vertex) == vertex for vertex in self.domain().index_set()
        )

    def preservation_decision(self):
        r"""Return whether every Coxeter matrix entry is preserved."""
        return conjunction(
            self.domain().coxeter_entry(left, right)
            == self.codomain().coxeter_entry(self(left), self(right))
            for left in self.domain().index_set()
            for right in self.domain().index_set()
        )

    @validator
    def validate_preservation(self) -> None:
        r"""Check that every Coxeter matrix entry is preserved (``OWN-22``)."""
        if self.preservation_decision() is False:
            raise ValueError(
                f"{self} is not a morphism of Coxeter diagrams: it does not preserve every Coxeter matrix entry"
            )


class CoxeterDiagramMor(CategoricalMor):
    r"""The bond-preserving maps between two represented Coxeter diagrams."""

    ElementMethods = CoxeterDiagramMorphism

    def _element_constructor_(self, datum):
        r"""The vertex map given by a callable, or by the images of the vertices in their order."""
        if element_parent(datum) is self:
            return datum
        if isinstance(datum, Map):
            raise TypeError(f"{datum} is an arrow of another Mor; give the vertex images")
        if callable(datum):
            function = datum
        else:
            assignment = dict(zip(self.domain().index_set(), datum, strict=True))
            function = assignment.__getitem__
        morphism = self.element_class(self, function)
        morphism.validate_preservation(check=False)
        return morphism

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism from {self.domain()} to {self.codomain()}: an "
                f"identity needs its domain and codomain to be the same Coxeter diagram"
            )
        return self(lambda vertex: vertex)


class CoxeterDiagramMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = CoxeterDiagramMor


class CoxeterDiagrams(OwnedCategory):
    r"""Finite Coxeter diagrams: labelled graphs encoding a symmetric angle matrix."""

    _MorCategory = CoxeterDiagramMorCategoryConstruction

    def _call_(self, datum, *, names=None, positions=None):
        r"""Construct the diagram of owned defining data.

        The admitted data are the owned Coxeter matrix
        \(m\colon V\times V\to\mathrm{Card}\) (an indexed family), the rows of
        its entries, a family of roots of one lattice, and a Cartan type given
        as the plain label ``[letter, rank]`` or ``[letter, rank, 1]``.  Roots
        give a rooted diagram; the other data give an unrooted one.  No Sage
        ``CoxeterMatrix`` or ``CartanType`` is admitted (``API-05``).

        EXAMPLES::

            sage: from dzack_research.preamble.all import CoxeterDiagrams
            sage: C = CoxeterDiagrams()
            sage: C([[1, 3], [3, 1]]).coxeter_entry(0, 1) == 3
            True
            sage: C(["A", 2]).coxeter_entry(1, 2) == 3
            True
            sage: roots = Lattices(ZZ)([[-2, 2], [2, -2]]).module_generators()
            sage: C(roots).is_rooted()
            True
        """
        match datum:
            case IndexedFamily():
                first_value = next(iter(datum.values()), None)
                match first_value:
                    case _ if first_value in Cardinalities():
                        return self.from_coxeter_matrix(datum, names=names, positions=positions)
                    case _:
                        return self.from_roots(datum, names=names, positions=positions)
            case [str(), *_] | (str(), *_):
                return self.from_cartan_type(list(datum), names=names, positions=positions)
            case list() | tuple():
                entries = tuple(datum)
                match entries[0] if entries else None:
                    case list() | tuple() | None:
                        return self.from_coxeter_matrix(entries, names=names, positions=positions)
                    case _:
                        first_parent = element_parent(entries[0])
                        assert first_parent is not None and first_parent in Lattices(first_parent.base_ring()), (
                            f"{datum!r} is neither the rows of a Coxeter matrix nor a family of lattice roots"
                        )
                        return self.from_roots(
                            finite_indexed_family_from_values(None, entries), names=names, positions=positions
                        )
            case _:
                raise TypeError(
                    f"{datum!r} is not a Coxeter matrix, its rows, a Cartan type label or a family of roots"
                )

    def an_object(self):
        r"""The diagram of ``A_2``: two vertices joined by an edge of order 3."""
        return self.from_cartan_type(["A", 2])

    @classmethod
    def _repr_object_names(cls):
        return "Coxeter diagrams"

    def super_categories(self):
        return [LabelledGraphs()]

    def Rooted(self):
        r"""The rooted Coxeter diagrams, the data category :class:`RootedCoxeterDiagrams`."""
        return RootedCoxeterDiagrams()

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"there are no morphisms of Coxeter diagrams from {domain} to {codomain}: both "
                f"must be Coxeter diagrams"
            )
        return self.MorCategory().Of(domain, codomain)

    @cached_method
    def minimal_edge_lattices(self):
        r"""Return the five minimal integral rank-two mirror configurations."""
        from sage_extensions.categories.sets.indexed_families import indexed_family

        labels = finite_ordered_set(
            ("orthogonal", "single", "double", "parallel", "ultraparallel")
        )
        grams = {
            "orthogonal": ((-2, 0), (0, -2)),
            "single": ((-2, 1), (1, -2)),
            "double": ((-2, 2), (2, -4)),
            "parallel": ((-2, 2), (2, -2)),
            "ultraparallel": ((-2, 3), (3, -2)),
        }
        integers = _owned_integers()
        return indexed_family(
            labels,
            lambda label: Lattices(integers)(grams[str(label)], names=("r1", "r2")),
            name="Minimal Coxeter edge lattices",
        )

    class ParentMethods:
        def __init__(
            self,
            coxeter_matrix,
            names=None,
            positions=None,
            type_label=None,
            root_gram_matrix=None,
            **rest,
        ) -> None:
            r"""Retain the owned Coxeter matrix \(m\colon V\times V\to\mathrm{Card}\).

            ``coxeter_matrix`` is the defining datum; ``_entries`` is its
            private realization, read once.  The vertex set, edges and labels
            are the Coxeter graph's, held by the ``LabelledGraphs``
            realization this construction threads through.  ``names`` is an
            owned ordered set of vertex names in vertex order; ``positions``
            is drawing data, checked by :meth:`validate_positions` on request.
            """
            self._coxeter_matrix = coxeter_matrix
            self._entries = _coxeter_entries_of(coxeter_matrix)
            self._type_label = type_label
            # Rooted constructors may supply the exact private engine matrix
            # already used to build the owned root-Gram tensor. Retain it so
            # exact inertia algorithms do not lower every tensor coordinate
            # through the finite-ordinal indexing boundary again.
            self._root_gram_engine_matrix = root_gram_matrix
            vertices = tuple(dict.fromkeys(left for left, _right in self._entries))
            self._names = (
                finite_ordered_set(tuple(f"s_{vertex}" for vertex in vertices))
                if names is None
                else names
            )
            self._preferred_positions = (
                None
                if positions is None
                else {vertex: (coordinates[0], coordinates[1]) for vertex, coordinates in positions.items()}
            )
            self._computed_positions = None
            super().__init__(**rest)

        @validator
        def validate_positions(self) -> None:
            r"""Check that the drawing positions place every vertex at one point of the plane."""
            if self._preferred_positions is not None and set(self._preferred_positions) != set(self.index_set()):
                raise ValueError(
                    f"the drawing positions {self._preferred_positions} do not place the vertices "
                    f"{self.index_set()}: every vertex needs exactly one position"
                )

        def index_set(self):
            r"""The vertex set \(V\), the vertices of the Coxeter graph."""
            return self.vertices()

        def vertex(self, position):
            return self.index_set()[int(position)]

        def is_rooted(self) -> bool:
            r"""Whether this diagram was constructed with a realization by roots."""
            return self in RootedCoxeterDiagrams()

        def __eq__(self, other):
            r"""Equality by defining data: the vertex set and \(m\), and the roots of a rooted diagram.

            Two Coxeter matrices are equal exactly when their entries are
            (Mathlib ``CoxeterMatrix``, ``@[ext]``).  A rooted and an unrooted
            diagram are distinct objects.
            """
            if other is self:
                return True
            if other not in CoxeterDiagrams():
                return False
            if self.is_rooted() != other.is_rooted():
                return False
            if not self.index_set() == other.index_set():
                return False
            vertices = self.index_set()
            if not all(
                self.coxeter_entry(left, right) == other.coxeter_entry(left, right)
                for left in vertices
                for right in vertices
            ):
                return False
            if self.is_rooted():
                return all(self.root(vertex) == other.root(vertex) for vertex in vertices)
            return True

        def __ne__(self, other):
            return not self == other

        def __hash__(self) -> int:
            r"""Hash of the vertex set and the entries of \(m\), consistent with ``==``."""
            vertices = self.index_set()
            return hash(
                (
                    vertices,
                    self.is_rooted(),
                    tuple(self.coxeter_entry(left, right) for left in vertices for right in vertices),
                )
            )

        def num_vertices(self):
            return self.cardinality()


        def vertex_weight(self, vertex):
            r"""Return the Vinberg invariant \([4:1]\) of the mirror ``vertex`` with itself."""
            return self.vinberg_invariant_matrix().vertex_label(vertex)

        def edge_weight(self, left, right):
            r"""Return the Vinberg invariant of the two joined mirrors, a point of \(\mathbb P^1(R)\)."""
            return self.vinberg_invariant_matrix().edge_label(left, right)

        def vertex_names(self):
            return self._names

        def coxeter_matrix(self):
            r"""Return the Coxeter matrix, the function \(m\colon V\times V\to\mathrm{Card}\).

            \(m(v,w)\) is the order of \(s_v s_w\) in the Coxeter group;
            \(m(v,v)=1\), and an element of infinite order has the value
            \(\aleph_0\).  It is the defining datum the diagram was constructed
            from.
            """
            return self._coxeter_matrix

        @cached_method
        def _engine_coxeter_matrix(self):
            r"""Return the Sage ``CoxeterMatrix`` realizing :meth:`coxeter_matrix`.

            Private adapter of ``CoxeterDiagrams`` (``OWN-05``, ``OWN-06``): it
            lowers the owned matrix to Sage on request, with \(\aleph_0\)
            written ``-1``, for the computations this module delegates to Sage
            (Coxeter type recognition).  It is computed from the defining
            datum, never stored as it; no caller outside this module uses it.
            """
            return _engine_coxeter_matrix_of(self._coxeter_matrix)

        def coxeter_entry(self, left, right):
            r"""Return \(m_{vw}\), the order of \(s_v s_w\) in the Coxeter group, as a cardinal.

            An order is a cardinality: a positive integer, or \(\aleph_0\) when
            \(s_v s_w\) has infinite order.
            """
            key = (left, right)
            if key not in self._entries:
                key = (self.index_set()(left), self.index_set()(right))
            return self._entries[key]

        def preferred_positions(self):
            r"""Return stored presentation coordinates, or a computed graph layout."""
            if self._preferred_positions is not None:
                return dict(self._preferred_positions)
            if self._computed_positions is None:
                layout = self._engine_graph().layout()
                self._computed_positions = {vertex: (coordinates[0], coordinates[1]) for vertex, coordinates in layout.items()}
            return dict(self._computed_positions)

        def tikz_picture(self):
            r"""Return a TikZ view of this live Coxeter diagram.

            The Coxeter matrix remains the mathematical datum.  The rendering
            draws exactly the pairs with ``m_ij != 2``.  The conventional
            ``m=3`` bond is unlabeled; every other bond carries its Coxeter
            order, including ``infinity``.
            """
            positions = self.preferred_positions()
            ranking = self.index_set().ranking_map()
            node_names = {
                vertex: f"v{ranking(vertex)}" for vertex in self.index_set()
            }
            lines = [
                r"\begin{tikzpicture}[every node/.style={circle,draw,inner sep=1.5pt}]"
            ]
            for vertex in self.index_set():
                x, y = positions[vertex]
                label = self.vertex_names()[int(ranking(vertex))]
                lines.append(
                    rf"  \node ({node_names[vertex]}) at ({float(x):.6g},{float(y):.6g}) {{$ {label} $}};"
                )
            for left, right in combinations(self.index_set(), 2):
                bond = self.coxeter_entry(left, right)
                if bond == 2:
                    continue
                if bond == 3:
                    label = ""
                else:
                    bond_label = r"\infty" if bond.is_countably_infinite() else str(bond)
                    label = (
                        rf" node[midway,fill=white,draw=none] {{$ {bond_label} $}}"
                    )
                lines.append(
                    rf"  \draw ({node_names[left]}) --{label} ({node_names[right]});"
                )
            lines.append(r"\end{tikzpicture}")
            return "\n".join(lines)

        def graph(self):
            r"""Return the Coxeter graph: one vertex per mirror, edges labelled by the bond.

            This is the graph of the definition (Bourbaki, *Groupes et algèbres
            de Lie* IV.1.9; Humphreys, *Reflection Groups and Coxeter Groups*
            §2.3): vertices \(v,w\) are joined exactly when \(m_{vw}\neq 2\),
            and the edge carries the label \(m_{vw}\).  The label is the datum.
            The customary drawing that renders \(m=4\) as a double edge and
            \(m=6\) as a triple edge is a rendering of that label available for
            two of its values, and never a second kind of edge.

            The Coxeter matrix records only \(m\), so at \(m=\infty\) it cannot
            say whether the two mirrors are parallel or divergent.  That
            distinction is a fact about the roots, and a rooted diagram answers
            it through :meth:`mirrors_are_parallel` and
            :meth:`mirrors_are_divergent`.

            It is the image of this diagram under the forgetful functor to
            ``LabelledGraphs()``.
            """
            edges = tuple((edge[0], edge[1]) for edge in self.edges())
            return LabelledGraphs().from_labels(
                tuple(self.vertices()),
                edges,
                {vertex: self.vertex_label(vertex) for vertex in self.vertices()},
                {edge: self.edge_label(*edge) for edge in edges},
            )

        def _engine_graph(self):
            r"""Return the Coxeter graph of :meth:`graph` as a Sage ``Graph``.

            Private to ``CoxeterDiagrams``: its layout, connected components,
            isomorphism certificates and drawing are computed on it.  Edges
            carry the bond \(m_{vw}\) as their label.
            """
            graph = Graph(multiedges=False, loops=False)
            graph.add_vertices(tuple(self.index_set()))
            for left, right in combinations(self.index_set(), 2):
                bond = self.coxeter_entry(left, right)
                if bond != 2:
                    graph.add_edge(left, right, bond)
            return graph

        def connected_components(self):
            r"""Return the connected components, as induced subdiagrams.

            The vertex sets of the components are those of the Coxeter graph,
            answered by its ``LabelledGraphs`` realization.
            """
            return finite_ordered_set(
                tuple(
                    self.induced_subdiagram(component)
                    for component in self.connected_component_vertex_sets()
                )
            )

        def is_connected(self) -> bool:
            r"""Return whether this diagram has exactly one connected component.

            One component is the definition, so the diagram on no vertices is
            not connected: it has zero components, not one.
            """
            return self.connected_component_vertex_sets().cardinality() == 1

        def induced_subdiagram(self, vertices):
            r"""The subdiagram induced on ``vertices``, as a subobject of this diagram.

            Its Coxeter matrix is the restriction of \(m\) to the selected
            vertices, taken in the order of :meth:`index_set`; a rooted
            diagram restricts its roots too.  The result is the pair
            \((A, f)\) of the restricted diagram \(A\) and its vertex
            inclusion \(f\colon A\to D\), an object of the slice
            ``CoxeterDiagrams().SliceOver(D)``; \(f\) is its ``arrow()``,
            constructed with it and not checked (``OWN-22``), and
            ``arrow().codomain()`` is this diagram.
            """
            selected = set(vertices)
            if any(vertex not in self.index_set() for vertex in selected):
                raise ValueError(
                    f"cannot form the subdiagram of {self} induced on {vertices}: some of them are "
                    f"not vertices of {self}, whose vertices are {self.index_set()}"
                )
            ranking = self.index_set().ranking_map()
            positions = tuple(
                int(ranking(vertex)) for vertex in self.index_set() if vertex in selected
            )
            chosen = finite_ordered_set(tuple(self.index_set()[position] for position in positions))
            restricted = _owned_coxeter_matrix(
                chosen,
                {(left, right): self.coxeter_entry(left, right) for left in chosen for right in chosen},
            )
            names = finite_ordered_set(tuple(self.vertex_names()[position] for position in positions))
            preferred_positions = (
                None
                if self._preferred_positions is None
                else {vertex: self._preferred_positions[vertex] for vertex in chosen}
            )
            if self.is_rooted():
                root_gram = self.root_gram_tensor()
                roots = indexed_family(chosen, self.root, name="Roots")
                engine_root_gram = self._root_gram_engine_matrix
                if engine_root_gram is None:
                    gram = tensor(
                        root_gram.base_ring(),
                        (),
                        (chosen.cardinality(), chosen.cardinality()),
                        [[root_gram[i, j] for j in positions] for i in positions],
                    )
                    engine_subgram = None
                else:
                    # Restrict the already selected private Gram matrix by
                    # integer positions, then raise its entries to the owned
                    # tensor. Repeatedly indexing the full owned tensor here
                    # normalizes two finite ordinal indices for every matrix
                    # entry, which dominates construction of the hundreds of
                    # rooted elliptic subdiagrams in Sterk's archive.
                    engine_subgram = sage_matrix(
                        engine_root_gram.base_ring(),
                        [
                            [engine_root_gram[i, j] for j in positions]
                            for i in positions
                        ],
                    )
                    gram = tensor(
                        root_gram.base_ring(),
                        (),
                        (chosen.cardinality(), chosen.cardinality()),
                        [
                            [
                                _owned_engine_element(root_gram.base_ring(), engine_subgram[i, j])
                                for j in range(engine_subgram.ncols())
                            ]
                            for i in range(engine_subgram.nrows())
                        ],
                    )
                extra = (RootedCoxeterDiagrams(),)
            else:
                roots = None
                gram = None
                engine_subgram = None
                extra = ()
            restricted_diagram = _coxeter_diagram(
                restricted,
                names=names,
                roots=roots,
                root_gram=gram,
                root_gram_matrix=engine_subgram,
                positions=preferred_positions,
            )
            inclusion = restricted_diagram.Mor(self)(lambda vertex: vertex)
            return CoxeterDiagrams().SliceOver(self).object(inclusion, categories=extra)

        def schlafli_tensor(self):
            r"""Return the normalized reflection Gram tensor ``S_ii=1``.

            A rooted diagram retains more metric data than its Coxeter matrix:
            an infinite bond can mean parallel or divergent mirrors.  Normalize
            the actual root Gram in that case, using
            ``S_ij = -|b(r_i,r_j)|/sqrt(q(r_i)q(r_j))``.  An unrooted diagram
            has only the bond labels, so its infinite bond is necessarily the
            parallel boundary value ``-1``.
            """
            from sage.all import cos, pi
            from sage.rings.qqbar import AA as SageAA

            real_algebraics = _owned_real_algebraic_numbers()
            rooted_gram = self.root_gram_tensor() if self.is_rooted() else None
            rooted_gram_matrix = self._root_gram_engine_matrix
            ordered_mirrors = tuple(self.index_set())
            ranking = None if rooted_gram_matrix is not None else self.index_set().ranking_map()
            values = []
            for i, left in enumerate(ordered_mirrors):
                row = []
                for j, right in enumerate(ordered_mirrors):
                    if i == j:
                        row.append(real_algebraics.one())
                        continue
                    if rooted_gram is not None:
                        if rooted_gram_matrix is None:
                            left_square = SageAA(
                                _engine_element(rooted_gram.base_ring(), rooted_gram[i, i])
                            )
                            right_square = SageAA(
                                _engine_element(rooted_gram.base_ring(), rooted_gram[j, j])
                            )
                            pairing = SageAA(
                                _engine_element(rooted_gram.base_ring(), rooted_gram[i, j])
                            )
                        else:
                            left_square = SageAA(rooted_gram_matrix[i, i])
                            right_square = SageAA(rooted_gram_matrix[j, j])
                            pairing = SageAA(rooted_gram_matrix[i, j])
                        normalized = -abs(pairing) / (left_square * right_square).sqrt()
                        row.append(_cross_engine_ring_value(normalized))
                        continue
                    m = self.coxeter_entry(left, right)
                    if m.is_countably_infinite():
                        row.append(-real_algebraics.one())
                    else:
                        row.append(_cross_engine_ring_value(-SageAA(cos(pi / int(m)))))
                values.append(row)
            mirrors = self.cardinality()
            return tensor(real_algebraics, (), (mirrors, mirrors), values)

        @cached_method
        def _inertia_counts(self):
            r"""Return \((n_+,n_-,n_0)\) of the Schlaefli form, by Sylvester.

            The Coxeter diagram is classified by the inertia of its Schlaefli
            form, and that form is allowed to be degenerate, so the zero index
            \(n_0\) is part of the answer.  This is not a signature *pair*.
            """

            # For a rooted integral diagram, the retained root Gram supplies
            # an integral matrix congruent to the Schlaefli form by a positive
            # diagonal scaling. Compute inertia from it directly rather than
            # rebuilding the normalized tensor and lowering every entry.
            if (
                self._root_gram_engine_matrix is not None
                and self._root_gram_engine_matrix.base_ring() is SageZZ
            ):
                gram = self._root_gram_engine_matrix.change_ring(SageZZ)
                matrix = sage_matrix(
                    SageZZ,
                    [
                        [
                            abs(gram[i, i]) if i == j else -abs(gram[i, j])
                            for j in range(gram.ncols())
                        ]
                        for i in range(gram.nrows())
                    ],
                ).change_ring(QQ)
            else:
                matrix = _engine_component_matrix(self.schlafli_tensor())
            entries = [[matrix[i, j] for j in range(matrix.ncols())]
                       for i in range(matrix.nrows())]
            positive = negative = zero = 0
            while entries:
                n = len(entries)
                pivot = next((i for i in range(n) if entries[i][i] != 0), None)
                if pivot is None:
                    off = next(((i, j) for i in range(n)
                                for j in range(i + 1, n) if entries[i][j] != 0), None)
                    if off is None:
                        zero += n
                        break
                    i, j = off
                    # A nonzero off-diagonal pairing gives a nonisotropic
                    # vector e_i+e_j; change basis by replacing e_i.
                    for k in range(n):
                        entries[i][k] += entries[j][k]
                    for k in range(n):
                        entries[k][i] += entries[k][j]
                    pivot = i
                if pivot:
                    entries[0], entries[pivot] = entries[pivot], entries[0]
                    for row in entries:
                        row[0], row[pivot] = row[pivot], row[0]
                d = entries[0][0]
                if d > 0:
                    positive += 1
                else:
                    negative += 1
                entries = [[entries[i][j] - entries[i][0] * entries[0][j] / d
                            for j in range(1, n)] for i in range(1, n)]
            return cardinal(positive), cardinal(negative), cardinal(zero)

        def positive_inertia_index(self):
            r"""Return \(n_+\), the positive index of inertia of the Schlaefli form."""
            return self._inertia_counts()[0]

        def negative_inertia_index(self):
            r"""Return \(n_-\), the negative index of inertia of the Schlaefli form."""
            return self._inertia_counts()[1]

        def zero_inertia_index(self):
            r"""Return \(n_0\), the dimension of the radical of the Schlaefli form."""
            return self._inertia_counts()[2]

        def is_elliptic(self) -> bool:
            return self.negative_inertia_index() == 0 and self.zero_inertia_index() == 0

        def is_parabolic(self) -> bool:
            return self.negative_inertia_index() == 0 and self.zero_inertia_index() == 1

        def is_hyperbolic(self) -> bool:
            return self.negative_inertia_index() == 1

        @cached_method
        def induced_subdiagrams(self):
            r"""The owned finite ordered set of all induced subdiagrams, one per vertex subset.

            Ordered by the number of vertices and then lexicographically in
            vertex order; its ``ranking_map`` indexes the subdiagrams by an
            owned finite ordinal, on which :meth:`Aut` acts.
            """
            vertices = tuple(self.index_set())
            return finite_ordered_set(
                tuple(
                    self.induced_subdiagram(subset)
                    for size in range(int(self.cardinality()) + 1)
                    for subset in combinations(vertices, size)
                )
            )

        def _induced_subdiagrams(self, predicate, *, connected):
            r"""Return the induced subdiagrams satisfying ``predicate``.

            With ``connected=True``, enumerate connected vertex subsets by
            frontier growth in the Coxeter graph. Filtering all ``2^n`` subsets
            and constructing a rooted subdiagram for each is needlessly
            exponential for the five Sterk diagrams: only a small fraction of
            their subsets are connected. The index sets are still ordered by
            cardinality and then lexicographically, exactly as in
            :meth:`induced_subdiagrams`.
            """
            vertices = tuple(self.index_set())
            if not connected:
                return finite_ordered_set(
                    tuple(
                        diagram
                        for diagram in self.induced_subdiagrams()
                        if predicate(diagram)
                    )
                )

            adjacency = [set() for _vertex in vertices]
            for i, left in enumerate(vertices):
                for j in range(i + 1, len(vertices)):
                    if self.coxeter_entry(left, vertices[j]) != 2:
                        adjacency[i].add(j)
                        adjacency[j].add(i)

            # Grow from each singleton, deduplicating by integer vertex
            # positions rather than comparing represented diagram objects.
            seen = {frozenset((i,)) for i in range(len(vertices))}
            frontier = list(seen)
            while frontier:
                subset = frontier.pop()
                neighbors = set().union(*(adjacency[i] for i in subset)) - set(subset)
                for neighbor in neighbors:
                    enlarged = subset | {neighbor}
                    if enlarged not in seen:
                        seen.add(enlarged)
                        frontier.append(enlarged)

            ordered_subsets = sorted(seen, key=lambda subset: (len(subset), tuple(sorted(subset))))
            return finite_ordered_set(
                tuple(
                    diagram
                    for positions in ordered_subsets
                    if predicate(
                        diagram := self.induced_subdiagram(
                            tuple(vertices[i] for i in sorted(positions))
                        )
                    )
                )
            )

        def _connected_elliptic_subdiagrams(self):
            r"""Enumerate connected elliptic induced subdiagrams by positive-definite growth.

            A principal submatrix of a non-positive-definite symmetric matrix
            cannot become positive definite after adjoining more indices.
            Grow connected vertex sets only while their Schlaefli principal
            matrix is positive definite. This is exact Sylvester/LDL
            elimination over the selected real algebraic field, and avoids
            constructing every connected rooted subdiagram merely to reject it.
            """
            vertices = tuple(self.index_set())
            if (
                self._root_gram_engine_matrix is not None
                and self._root_gram_engine_matrix.base_ring() is SageZZ
            ):
                # For an integral rooted diagram, let G be its root Gram and
                # d_i=|G_ii|. Its Schlaefli matrix is congruent via the positive
                # diagonal matrix diag(sqrt(d_i)) to the integral matrix
                # A_ii=d_i, A_ij=-|G_ij|. Sylvester inertia is invariant under
                # this congruence, so exact rational LDL avoids algebraic
                # square roots entirely for Sterk's integral roots.
                gram = self._root_gram_engine_matrix
                if gram is None:
                    gram = _engine_component_matrix(self.root_gram_tensor())
                gram = gram.change_ring(SageZZ)
                matrix = sage_matrix(
                    SageZZ,
                    [
                        [
                            abs(gram[i, i]) if i == j else -abs(gram[i, j])
                            for j in range(gram.ncols())
                        ]
                        for i in range(gram.nrows())
                    ],
                ).change_ring(QQ)
            else:
                matrix = _engine_component_matrix(self.schlafli_tensor())
            adjacency = [set() for _vertex in vertices]
            for i, _left in enumerate(vertices):
                for j in range(i + 1, len(vertices)):
                    # The Schlaefli off-diagonal vanishes exactly when the
                    # Coxeter entry is 2. Read adjacency from the already
                    # computed exact matrix instead of reranking represented
                    # vertex labels through the public Coxeter-entry accessor.
                    if matrix[i, j] != 0:
                        adjacency[i].add(j)
                        adjacency[j].add(i)

            # Each accepted subset carries an exact LDL^T factorization in
            # its growth order. Adding one vertex needs only one Schur
            # complement; recomputing a full principal-matrix elimination for
            # every candidate repeats cubic work across all its subdiagrams.
            # A candidate rejected by its Schur complement is not expanded,
            # because a non-positive-definite principal submatrix cannot be a
            # principal submatrix of any elliptic diagram.
            states = {}
            frontier = []
            seen = set()
            for i in range(len(vertices)):
                subset = frozenset((i,))
                seen.add(subset)
                pivot = matrix[i, i]
                if pivot > 0:
                    states[subset] = ((i,), ((1,),), (pivot,))
                    frontier.append(subset)

            elliptic = []
            while frontier:
                subset = frontier.pop()
                order, lower, diagonal = states[subset]
                elliptic.append(tuple(sorted(subset)))
                neighbors = set().union(*(adjacency[i] for i in subset)) - set(subset)
                for neighbor in neighbors:
                    enlarged = subset | {neighbor}
                    if enlarged in seen:
                        continue
                    seen.add(enlarged)
                    column = tuple(matrix[i, neighbor] for i in order)
                    solved = []
                    for i, value in enumerate(column):
                        solved.append(
                            value
                            - sum(
                                (lower[i][j] * solved[j] for j in range(i)),
                                matrix.base_ring().zero(),
                            )
                        )
                    pivot = matrix[neighbor, neighbor] - sum(
                        (solved[i] * solved[i] / diagonal[i] for i in range(len(order))),
                        matrix.base_ring().zero(),
                    )
                    if pivot <= 0:
                        continue
                    new_lower_row = tuple(solved[i] / diagonal[i] for i in range(len(order)))
                    new_lower = tuple(row + (0,) for row in lower) + (new_lower_row + (1,),)
                    states[enlarged] = (order + (neighbor,), new_lower, diagonal + (pivot,))
                    frontier.append(enlarged)

            elliptic.sort(key=lambda subset: (len(subset), subset))
            return finite_ordered_set(
                tuple(
                    self.induced_subdiagram(tuple(vertices[i] for i in positions))
                    for positions in elliptic
                )
            )

        def elliptic_subdiagrams(self, *, connected=False):
            r"""Return the elliptic induced subdiagrams.

            The subdiagram on no vertices is elliptic: its Schlaefli form on the
            zero space has no negative and no zero index of inertia.  It is the
            minimum of :meth:`subdiagram_poset`, and it is excluded by
            ``connected=True`` because it has no connected component at all.
            """
            if connected:
                return self._connected_elliptic_subdiagrams()
            return self._induced_subdiagrams(lambda diagram: diagram.is_elliptic(), connected=False)

        def parabolic_subdiagrams(self, *, connected=False):
            r"""Return the parabolic induced subdiagrams."""
            return self._induced_subdiagrams(
                lambda diagram: diagram.is_parabolic(), connected=connected
            )

        def schlaflian(self):
            r"""Return \(\det C\) for the Schlaefli matrix \(C\) of this diagram.

            \(C_{vv}=2\) and \(C_{vw}=-2\cos(\pi/m_{vw})\), so \(C\) is twice
            the normalized :meth:`schlafli_tensor`.  This is the normalization
            the literature determinant tables use: \(n+1\) for \(A_n\), \(2\)
            for \(B_n\) and \(C_n\), \(4\) for \(D_n\), \(9-n\) for \(E_n\),
            \(5-n\) for \(F_n\) and \(3-n\) for \(G_n\).  It vanishes exactly
            on the diagrams with a radical, which is where each family passes
            from elliptic to parabolic.
            """
            normalized = _engine_component_matrix(self.schlafli_tensor())
            return _cross_engine_ring_value((2 * normalized).determinant())

        def vinberg_invariant_matrix(self):
            r"""Return the Vinberg invariant matrix of this diagram.

            The projective invariants \([4b(r_v,r_w)^2:q(r_v)q(r_w)]\) of the
            pairs of mirrors.  On a rooted diagram they come from the root
            Gram and are exact over the base ring; on an unrooted one only the
            bonds are available, and the invariants are the algebraic numbers
            \(4\cos^2(\pi/m)\).  The passage back to the Coxeter matrix loses
            the distinction between parallel and divergent mirrors.
            """
            from sage_extensions.categories.vinberg_invariants import (
                VinbergInvariantMatrices,
            )

            return VinbergInvariantMatrices().from_coxeter_diagram(self)

        def coxeter_group(self):
            r"""Return the Coxeter group \(W\) of this diagram.

            \(W=\langle s_v \mid s_v^2,\ (s_v s_w)^{m_{vw}}\rangle\), one
            involution per vertex.  The owned group carries that presentation:
            it answers ``presenting_free_group`` and ``defining_relations`` as
            well as ``order``, so the presented group and the reflection
            representation are one object here and not two constructions.
            """
            from sage_extensions.categories.group.groups import Groups

            return Groups.Coxeter(self.coxeter_matrix())

        def finitely_presented_coxeter_group(self):
            r"""Return the same owned Coxeter group, which retains its defining presentation."""
            return self.coxeter_group()

        @cached_method
        def _bond_preserving_permutation_group(self):
            r"""Return the owned automorphism group of the labelled Coxeter graph.

            Private adapter of ``CoxeterDiagrams`` (``OWN-06``); its one
            consumer is :meth:`Aut`, and it returns an owned group.  NetworkX enumerates graph automorphisms on the finite ordinal of
            vertex positions.  The public group is then the corresponding
            subgroup of the owned symmetric group.  This avoids Sage's current
            ``Graph.automorphism_group`` crash while keeping the maintained
            graph-isomorphism algorithm as the computation owner.
            """
            import networkx as nx

            from sage_extensions.categories.group.groups import Groups

            vertices = tuple(self.index_set())
            graph = nx.Graph()
            for position in range(len(vertices)):
                attributes = {}
                if self.is_rooted():
                    attributes["root_square"] = self.root_gram_tensor()[position, position]
                graph.add_node(position, **attributes)
            for left_position, right_position in combinations(range(len(vertices)), 2):
                bond = self.coxeter_entry(
                    vertices[left_position], vertices[right_position]
                )
                if bond != 2:
                    graph.add_edge(left_position, right_position, bond=bond)

            node_match = (
                nx.algorithms.isomorphism.categorical_node_match(
                    "root_square", None
                )
                if self.is_rooted()
                else None
            )
            edge_match = nx.algorithms.isomorphism.categorical_edge_match(
                "bond", None
            )
            matcher = nx.algorithms.isomorphism.GraphMatcher(
                graph, graph, node_match=node_match, edge_match=edge_match
            )
            symmetric = Groups.S(len(vertices))
            automorphisms = tuple(
                symmetric(
                    [mapping[position] + 1 for position in range(len(vertices))]
                )
                for mapping in matcher.isomorphisms_iter()
            )
            return symmetric.subgroup(automorphisms)

        def _aut_vertex_map(self, automorphism):
            r"""The permutation of the vertices that the element ``automorphism`` of :meth:`Aut` is.

            Part of the private adapter of :meth:`_bond_preserving_permutation_group`:
            that group is a subgroup of the symmetric group on the vertex
            positions numbered from one, and this reads its elements back as
            maps of vertices.
            """
            ranking = self.index_set().ranking_map()
            vertices = tuple(self.index_set())
            return lambda vertex: vertices[int(automorphism(int(ranking(vertex)) + 1)) - 1]

        def Aut(self):
            r"""Return the group of diagram automorphisms.

            The automorphisms of the Coxeter graph with its bond labels: for
            \(A_n\) with \(n\geq 2\) the path reversal, of order two; for
            \(D_4\) the symmetric group on the three outer nodes, triality; for
            \(E_8\) trivial.
            """
            return self._bond_preserving_permutation_group()

        @cached_method
        def _subdiagram_vertex_sets(self):
            r"""The vertex set of each induced subdiagram, indexed by its rank in :meth:`induced_subdiagrams`."""
            return tuple(frozenset(diagram.index_set()) for diagram in self.induced_subdiagrams())

        def _subdiagram_g_set(self, predicate, *, connected):
            r"""The finite :meth:`Aut`-set of the ranks of the induced subdiagrams satisfying ``predicate``.

            The points are owned ranks: elements of the finite ordinal that
            :meth:`induced_subdiagrams` is enumerated by.  An automorphism
            \(\sigma\) sends the rank of the subdiagram on \(S\) to the rank of
            the subdiagram on \(\sigma(S)\).  Ellipticity, parabolicity and
            connectedness are invariants of the subdiagram, so the selected
            ranks form a stable set.
            """
            from sage_extensions.categories.group.g_sets import FiniteGSets

            subdiagrams = self.induced_subdiagrams()
            ordinal = finite_ordinal_set(int(subdiagrams.cardinality()))
            vertex_sets = self._subdiagram_vertex_sets()
            rank_of = {vertices: ordinal(position) for position, vertices in enumerate(vertex_sets)}
            points = finite_ordered_set(
                tuple(
                    ordinal(position)
                    for position, diagram in enumerate(subdiagrams)
                    if predicate(diagram) and (not connected or diagram.is_connected())
                )
            )

            def act(automorphism, rank):
                vertex_map = self._aut_vertex_map(automorphism)
                return rank_of[frozenset(vertex_map(vertex) for vertex in vertex_sets[int(rank)])]

            return FiniteGSets(self.Aut())(points, act)

        def subdiagram_orbits(self):
            r"""The orbit set of :meth:`Aut` acting on the ranks of the induced subdiagrams.

            A point is the rank of a subdiagram in :meth:`induced_subdiagrams`;
            ``induced_subdiagrams().ranking_map().inverse()`` reads it as the
            subdiagram.
            """
            return self._subdiagram_g_set(lambda diagram: True, connected=False).orbits()

        def elliptic_subdiagram_orbits(self, *, connected=False):
            r"""Return the orbit set of :meth:`Aut` acting on the elliptic induced subdiagrams."""
            return self._subdiagram_g_set(lambda diagram: diagram.is_elliptic(), connected=connected).orbits()

        def parabolic_subdiagram_orbits(self, *, connected=False):
            r"""Return the orbit set of :meth:`Aut` acting on the parabolic induced subdiagrams."""
            return self._subdiagram_g_set(lambda diagram: diagram.is_parabolic(), connected=connected).orbits()

        def _maximal_by_vertex_inclusion(self, subdiagrams):
            r"""Return the members maximal for inclusion of vertex sets."""
            vertex_sets = tuple(frozenset(diagram.index_set()) for diagram in subdiagrams)
            return finite_ordered_set(
                tuple(
                    diagram
                    for diagram, vertices in zip(subdiagrams, vertex_sets, strict=True)
                    if not any(
                        vertices < other for other in vertex_sets
                    )
                )
            )

        def maximal_elliptic_subdiagrams(self, *, connected=False):
            r"""Return the elliptic induced subdiagrams maximal for inclusion."""
            return self._maximal_by_vertex_inclusion(
                self.elliptic_subdiagrams(connected=connected)
            )

        def maximal_parabolic_subdiagrams(self, *, connected=False):
            r"""Return the parabolic induced subdiagrams maximal for inclusion."""
            return self._maximal_by_vertex_inclusion(
                self.parabolic_subdiagrams(connected=connected)
            )

        def _subdiagram_poset_on(self, subdiagrams):
            r"""The poset of ``subdiagrams`` ordered by inclusion of their vertex sets."""

            def below(left, right) -> bool:
                return all(vertex in right.index_set() for vertex in left.index_set())

            return PartiallyOrderedSets()(subdiagrams, below)

        def subdiagram_poset(self):
            r"""Return every induced subdiagram, ordered by inclusion of vertices.

            The maximum is the diagram itself and the minimum is the subdiagram
            on no vertices.
            """
            return self._subdiagram_poset_on(
                self._induced_subdiagrams(lambda diagram: True, connected=False)
            )

        def elliptic_subdiagram_poset(self, *, connected=False):
            r"""Return the elliptic induced subdiagrams ordered by inclusion."""
            return self._subdiagram_poset_on(
                self.elliptic_subdiagrams(connected=connected)
            )

        def parabolic_subdiagram_poset(self, *, connected=False):
            r"""Return the parabolic induced subdiagrams ordered by inclusion."""
            return self._subdiagram_poset_on(
                self.parabolic_subdiagrams(connected=connected)
            )

        def subdiagram_orbit_poset(self, orbits):
            r"""The orbit set ``orbits`` of :meth:`Aut` on induced subdiagrams, under the order inclusion induces.

            \([H]\leq[K]\) when some member of \([H]\) is an induced
            subdiagram of some member of \([K]\).  :meth:`Aut` is transitive
            on each orbit and carries inclusions to inclusions, so the relation
            holds exactly when some member of \([H]\) has its vertices inside
            one chosen member of \([K]\), which is what is asked here.

            It is a partial order.  Reflexive, because an orbit meets itself.
            Antisymmetric, because every member of an orbit has the same number
            of vertices, so two containments force equality and hence one
            orbit.  Transitive, by the same transport of the containment along
            an automorphism.  ``orbits`` is an orbit set returned by
            :meth:`subdiagram_orbits` or its elliptic and parabolic variants.
            """
            assert all(orbit.acting_group() is self.Aut() for orbit in orbits), (
                f"{orbits} is not an orbit set of the automorphism group of {self}"
            )

            vertex_sets = self._subdiagram_vertex_sets()

            def below(left, right) -> bool:
                target = vertex_sets[int(right.representative())]
                return any(vertex_sets[int(rank)] <= target for rank in left.points())

            return PartiallyOrderedSets()(orbits, below)

        def elliptic_subdiagram_orbit_poset(self, *, connected=False):
            r"""Return the :meth:`Aut`-orbits of elliptic subdiagrams, ordered by the order inclusion induces on orbits."""
            return self.subdiagram_orbit_poset(
                self.elliptic_subdiagram_orbits(connected=connected)
            )

        def parabolic_subdiagram_orbit_poset(self, *, connected=False):
            r"""Return the :meth:`Aut`-orbits of parabolic subdiagrams, ordered by the order inclusion induces on orbits."""
            return self.subdiagram_orbit_poset(
                self.parabolic_subdiagram_orbits(connected=connected)
            )

        @cached_method
        def scaled_cartan_type(self):
            r"""Return the diagram of the type of this connected elliptic diagram.

            A connected elliptic Coxeter diagram is the diagram of exactly one
            finite irreducible Coxeter group (Humphreys, *Reflection Groups and
            Coxeter Groups*, §2.7), and the Coxeter diagram of that type is
            returned.  Its :meth:`label` names the type, as ``A2`` or ``I2(5)``.

            A rooted diagram is a root basis in its realization, and its roots
            determine more than the Coxeter matrix.  The type B/C splits by the
            root squares: \(B_n\) has one short simple root and \(C_n\) has one
            long one (Humphreys, *Introduction to Lie Algebras and
            Representation Theory*, §11.4).  At rank two they are one root
            system, whose diagram of the type is ``C2``.  For a rooted diagram,
            the diagram of the type is the diagram of the simple roots of the
            root lattice of the recognized type, twisted so that its shortest
            root has square \(2s\) for the :meth:`root_scale` \(s\);
            :meth:`isomorphism_from_type_diagram` identifies it with this
            diagram.  Recognition of a rooted diagram is implemented
            for crystallographic root bases.
            """
            assert self.is_connected() and self.is_elliptic(), (
                f"{self} has no type: only a connected elliptic Coxeter diagram is the diagram "
                f"of a finite irreducible Coxeter group"
            )
            engine_matrix_ = self._engine_coxeter_matrix()
            coxeter_type = engine_matrix_.coxeter_type()
            assert coxeter_type is not engine_matrix_, (
                f"{self} is elliptic, but its Coxeter matrix {self.coxeter_matrix()} was not "
                f"recognized as a finite Coxeter type"
            )
            cartan = coxeter_type.cartan_type()
            letter = str(cartan.type())
            rank = int(cartan.rank())
            match self.is_rooted(), letter:
                case False, "I":
                    order = self.coxeter_entry(self.vertex(0), self.vertex(1))
                    return _coxeter_diagram_of_type(letter, int(order))
                case False, _:
                    return _coxeter_diagram_of_type(letter, rank)
            assert letter not in ("H", "I"), (
                f"the type of the rooted {self} is recognized for crystallographic root bases, "
                f"and its Coxeter type {cartan} is not crystallographic"
            )
            engine_scale = self._engine_root_scale()
            squares = self._engine_root_squares()
            match letter:
                case "B" if rank == 2:
                    letter = "C"
                case "B":
                    short_count = sum(square == 2 * engine_scale for square in squares)
                    assert short_count in (1, rank - 1), (
                        f"{self} has Coxeter type B/C of rank {rank}, but its root squares "
                        f"{squares} match neither B (one short root) nor C (one long root)"
                    )
                    letter = "B" if short_count == 1 else "C"
            reference = _simple_root_diagram_of_type(letter, rank, engine_scale)
            assert reference._engine_root_intersection_graph().is_isomorphic(
                self._engine_root_intersection_graph(), edge_labels=True
            ), (
                f"{self} was recognized as type {letter}{rank} with root scale {engine_scale}, but "
                f"the simple roots of that type do not have the Gram data of the roots of {self}"
            )
            return reference

        def label(self):
            r"""Return the name of the type of this connected elliptic diagram.

            It is the label of the diagram of the type, :meth:`scaled_cartan_type`,
            as ``A2``, ``C2`` or ``I2(5)``.
            """
            return self.scaled_cartan_type()._type_label

        def isomorphism_from_type_diagram(self):
            r"""Return an isomorphism from the diagram of the type onto this diagram.

            For a rooted diagram it also preserves the root squares and
            pairings, so it carries the ordered simple roots of the diagram of
            the type to an ordering of the roots of this diagram.
            """
            reference = self.scaled_cartan_type()
            match self.is_rooted():
                case True:
                    source = reference._engine_root_intersection_graph()
                    target = self._engine_root_intersection_graph()
                case False:
                    source = reference._engine_graph()
                    target = self._engine_graph()
            isomorphic, certificate = source.is_isomorphic(
                target, edge_labels=True, certificate=True
            )
            assert isomorphic, f"the diagram of the type {reference} is not isomorphic to {self}"
            return reference.Mor(self)(certificate.__getitem__)

        def component_scaled_cartan_types(self):
            r"""Return the component-indexed family of the diagrams of the types of the components."""
            from sage_extensions.categories.sets.indexed_families import indexed_family

            components = self.connected_components()
            labels = finite_ordered_set(tuple(range(int(components.cardinality()))))
            return indexed_family(
                labels,
                lambda position: components[int(position)].scaled_cartan_type(),
                name="Diagrams of the types of the Coxeter components",
            )

        def drawing_conventions(self):
            return {
                "root squares": "the vertex labels of root_intersection_graph(), omitted from TikZ",
                "ordinary Coxeter bond": "m=3 is drawn without a label",
                "other Coxeter bonds": "the Coxeter matrix entry m_vw labels the edge",
            }

        def equivariant_positions(self, automorphism):
            r"""Return exact planar positions intertwining a finite diagram automorphism.

            A position is a point ``(x, y)`` of the real plane with exact real
            coordinates.  An automorphism of order ``n >= 3`` acts as the
            rotation by ``2 pi/n``: the ``k``-th vertex of an orbit of length
            ``n`` on the circle of radius ``r`` sits at
            ``(r cos(2 pi k/n), r sin(2 pi k/n))``, and a fixed vertex at the
            origin.  An involution acts as the reflection ``y -> -y``: a fixed
            vertex sits at ``(c, 0)`` and a 2-cycle at ``(c, 1)``, ``(c, -1)``.
            """
            from sage_extensions.rings.real import RR

            order = int(automorphism.order())
            if order < 2:
                raise ValueError(
                    f"cannot place the vertices of {self} symmetrically under {automorphism}: it "
                    f"has order {order}, and a symmetric layout needs an automorphism of order at least 2"
                )
            unseen = set(self.index_set())
            orbits = []
            while unseen:
                start = next(iter(unseen))
                orbit = []
                point = start
                while point not in orbit:
                    orbit.append(point)
                    unseen.discard(point)
                    point = automorphism(point)
                if point != start:
                    raise ArithmeticError(
                        f"{automorphism} is not a permutation of the vertices of {self}: following it "
                        f"from {start} does not return to {start}"
                    )
                orbits.append(tuple(orbit))
            positions = {}
            if order == 2:
                place = 0
                for orbit in sorted(orbits, key=len):
                    if len(orbit) == 1:
                        positions[orbit[0]] = (RR(place), RR(0))
                    elif len(orbit) == 2:
                        positions[orbit[0]] = (RR(place), RR(1))
                        positions[orbit[1]] = (RR(place), RR(-1))
                    else:
                        raise ValueError(
                            f"{automorphism} has order 2 but an orbit {orbit} of length {len(orbit)}: "
                            f"an involution has only fixed points and 2-cycles"
                        )
                    place += 1
            else:
                fixed = tuple(orbit for orbit in orbits if len(orbit) == 1)
                if any(len(orbit) not in (1, order) for orbit in orbits) or len(fixed) > 1:
                    raise ValueError(
                        f"cannot place the vertices of {self} as a rotation by {automorphism}: a "
                        f"rotation of order {order} needs every orbit of length 1 or {order} and at most "
                        f"one fixed vertex, but the orbits are {orbits}"
                    )
                radius = 1
                for orbit in orbits:
                    if len(orbit) == 1:
                        positions[orbit[0]] = (RR(0), RR(0))
                        continue
                    for exponent, vertex in enumerate(orbit):
                        angle = 2 * RR.pi() * exponent / order
                        positions[vertex] = (RR(radius) * angle.cos(), RR(radius) * angle.sin())
                    radius += 1
            return positions

        def subdiagram(self, vertices):
            return self.induced_subdiagram(vertices)

        def plot(self, **options):
            r"""Draw the Coxeter graph.

            A drawing is a display artifact, not a mathematical value, like the
            string :meth:`tikz_picture` returns; so it is Sage's ``Graphics``
            of the graph, and ``OWN-04`` does not apply to it (ruled
            2026-10-14).
            """
            return self._engine_graph().plot(**options)

        def tikz(self, **_options):
            return self.tikz_picture()

        def _repr_(self):
            rooted = "rooted " if self.is_rooted() else ""
            return f"{rooted}Coxeter diagram on {self.cardinality()} vertices"

    def from_coxeter_matrix(self, coxeter_matrix, names=None, positions=None):
        r"""Return the diagram of a Coxeter matrix.

        An entry \(m_{vw}\) is the order of \(s_v s_w\): a positive integer, or the
        cardinal \(\aleph_0\) (``aleph0``) for an element of infinite order.
        The matrix is the owned function \(m\colon V\times V\to\mathrm{Card}\)
        that :meth:`coxeter_matrix` returns, whose diagram has vertex set
        \(V\), or its rows, whose diagram has the row positions as vertices.
        """
        match coxeter_matrix:
            case IndexedFamily():
                pass
            case list() | tuple():
                coxeter_matrix = _coxeter_matrix_of_rows(coxeter_matrix)
            case _:
                raise TypeError(
                    f"{coxeter_matrix!r} is not a Coxeter matrix: give the owned function "
                    f"m: V x V -> Card or the rows of its entries"
                )
        return _coxeter_diagram(coxeter_matrix, names=names, positions=positions)

    def from_cartan_type(self, cartan_type, names=None, *, rooted=False, scale=None, positions=None):
        r"""Return the diagram of the Cartan type named by the plain label ``[letter, rank(, affine)]``.

        With ``rooted=True`` or a ``scale`` the diagram is rooted by the simple
        roots of the root lattice of the type, twisted by ``scale``.
        """
        match cartan_type:
            case [str(), *_] | (str(), *_):
                label = list(cartan_type)
            case _:
                raise TypeError(
                    f"{cartan_type!r} is not a Cartan type label: write it as [letter, rank] or "
                    f"[letter, rank, 1]"
                )
        if scale is not None:
            scale = _owned_integers()(scale)
            if scale < 1:
                raise ValueError(
                    f"cannot scale the root lattice of type {label} by {scale}: the scale "
                    f"must be a positive integer"
                )
            rooted = True
        coxeter_matrix = _coxeter_matrix_of_cartan_label(label)
        if not rooted:
            return _coxeter_diagram(coxeter_matrix, names=names, positions=positions)

        match label:
            case [letter, rank]:
                lattice = Lattices.root_lattice(letter, rank)
            case _:
                raise ValueError(
                    f"{label} is an affine Cartan type: a rooted diagram is the diagram of the simple "
                    f"roots of a finite root lattice"
                )
        if scale is not None and scale != 1:
            lattice = lattice.twist(scale)
        return self.from_roots(lattice.module_generators(), names=names, positions=positions)

    def from_roots(self, roots, names=None, positions=None):
        r"""Return the rooted diagram of the owned family ``roots`` of roots of one lattice.

        The vertices are the labels of the family, and \(m_{vw}\) is read off
        the pairing of \(r_v\) and \(r_w\).  This is the one construction of
        a rooted diagram, crystallographic or not.
        """
        return _root_basis_diagram(roots, names=names, positions=positions)


def _root_basis_diagram(roots, names=None, positions=None, type_label=None):
    r"""Return the rooted diagram of the owned family ``roots``, named ``type_label`` when it is the diagram of a type."""
    # Rooted-diagram callers commonly already have a labelled IndexedFamily.
    # Rewrapping it creates a new callback-backed family and then probes that
    # callback for constancy/category evidence, repeatedly evaluating costly
    # metric-dual root constructions. Preserve the selected family verbatim;
    # only literal iterables need to be interpreted here.
    if not isinstance(roots, IndexedFamily):
        roots = finite_indexed_family_from_values(None, roots)
    else:
        from sage_extensions.categories.sets.set_categories import EnumeratedSets

        assert roots.cardinality().is_finite() is True
        assert roots.index_set() in EnumeratedSets()
    assert roots.cardinality() != 0, (
        "cannot form a Coxeter diagram from roots: no roots were given, and the "
        "diagram needs at least one to determine its lattice"
    )
    mirrors = roots.index_set()
    # Materialize the finite selected family exactly once. Repeatedly walking
    # an owned IndexedFamily can rerun label normalization and value dispatch;
    # the roots are subsequently needed both for the common-parent proof and
    # for the coordinate matrix, so keep the same selected tuple for both.
    # Iterate the selected family instead of calling ``value(index)`` for
    # every already-normalized label: IndexedFamily's iteration path enters
    # its rank cache directly, whereas ``value`` re-applies the index-set
    # constructor and ranking-map machinery to each label.
    root_values = tuple(roots)
    realization = root_values[0].parent()
    assert all(root.parent() is realization for root in root_values), (
        f"the roots {roots} do not all lie in one lattice: the first lies in "
        f"{realization}, and a Coxeter diagram of roots needs a single lattice"
    )
    # A root lattice may have a pairing valued in a scalar extension, such
    # as QQ restricted to ZZ. Evaluate its scalar Gram tensor in that ring;
    # the values of the restricted module are not elements of the base ring.
    form_gram = realization.gram_tensor()
    ring = form_gram.base_ring()
    # A lattice element already owns its chosen-basis coordinates. Calling
    # ``framing_morphism().lift(root)`` invokes the generic module-morphism
    # preimage solver, which rebuilds framing data for every root; the element
    # API explicitly exposes ``to_vector()`` for this exact coordinate query.
    chosen_vectors = tuple(root.to_vector() for root in root_values)
    coordinate_vectors = tuple(
        vector.parent()._selected_module_coefficients(vector)
        for vector in chosen_vectors
    )
    basis_labels = tuple(realization.module_generating_set())
    # The lattice pairing is symmetric. Contract each unordered pair once
    # and retain both matrix entries; this halves the expensive exact tensor
    # contractions for the larger rooted diagrams (including Sterk's).
    # Contracting two tensors independently for every root pair repeatedly
    # traverses the owned tensor index machinery. Lower the selected scalar
    # Gram and coordinate rows once, then use exact matrix multiplication.
    # The coordinate matrix has one row per root and the original framing
    # order, so its Gram is precisely C G C^T.
    engine_ring = _engine_ring(ring)
    coordinate_matrix = sage_matrix(
        engine_ring,
        [
            [
                _engine_numeral(ring, vector.get(label, ring.zero()))
                for label in basis_labels
            ]
            for vector in coordinate_vectors
        ],
    )
    engine_gram = _engine_component_matrix(form_gram).change_ring(engine_ring)
    paired_matrix = coordinate_matrix * engine_gram * coordinate_matrix.transpose()
    pairings = {
        (left, right): _owned_engine_element(ring, paired_matrix[i, j])
        for i, left in enumerate(mirrors)
        for j, right in enumerate(mirrors)
    }
    gram = tensor(
        ring,
        (),
        (mirrors.cardinality(), mirrors.cardinality()),
        [[pairings[left, right] for right in mirrors] for left in mirrors],
    )
    # The angle is symmetric in the two roots. Exact conversion to AA and
    # QQbar in `_coxeter_entry` is comparatively expensive, so compute each
    # unordered pair once and populate both matrix positions from that value.
    entries = {}
    ordered_mirrors = tuple(mirrors)
    for i, left in enumerate(ordered_mirrors):
        entries[left, left] = cardinal(1)
        for right in ordered_mirrors[i + 1 :]:
            value = _coxeter_entry(
                ring,
                pairings[left, left],
                pairings[right, right],
                pairings[left, right],
            )
            entries[left, right] = value
            entries[right, left] = value
    return _coxeter_diagram(
        _owned_coxeter_matrix(mirrors, entries),
        names=names,
        roots=roots,
        root_gram=gram,
        root_gram_matrix=paired_matrix,
        positions=positions,
        type_label=type_label,
    )


@cached_function
def _coxeter_diagram_of_type(letter, index):
    r"""Return the Coxeter diagram of the finite irreducible Coxeter type ``(letter, index)``.

    ``index`` is the rank, except for the dihedral type \(I_2(p)\), whose index
    is \(p\).  The diagram is labelled ``I2(p)`` or by letter and rank.
    """
    match letter:
        case "I":
            type_label = f"I2({index})"
        case _:
            type_label = f"{letter}{index}"
    return _coxeter_diagram(_coxeter_matrix_of_cartan_label([letter, index]), type_label=type_label)


@cached_function
def _simple_root_diagram_of_type(letter, rank, engine_scale):
    r"""Return the diagram of the simple roots of type ``letter``/``rank`` at root scale ``engine_scale``.

    The roots are the simple roots of ``Lattices.root_lattice(letter, rank)``,
    whose shortest root has square \(-2\), twisted by \(-s\) so that the
    shortest root has square \(2s\).  A fractional \(s\) first extends the
    scalars to the rationals.
    """
    reference = Lattices.root_lattice(letter, rank)
    integers = reference.base_ring()
    twist = -engine_scale
    match twist.denominator():
        case 1:
            factor = integers(int(twist))
        case denominator:
            fraction_map = integers.fraction_field_map()
            reference = reference.base_change(fraction_map)
            factor = fraction_map(integers(int(twist.numerator()))) / reference.base_ring()(
                int(denominator)
            )
    reference = reference.twist(factor)
    return _root_basis_diagram(reference.module_generators(), type_label=f"{letter}{rank}")



class RootedCoxeterDiagrams(OwnedCategory):
    r"""Coxeter diagrams with a chosen realization of their mirrors by roots of one lattice.

    A family of roots \(r_v\) of a lattice determines the Coxeter matrix by
    \(4\cos^2(\pi/m_{vw}) = 4b(r_v,r_w)^2/(q(r_v)q(r_w))\), and retains more:
    at \(m=\infty\) the roots tell parallel mirrors from divergent ones.
    The roots are a chosen datum on the diagram, so this is a data category,
    not an axiom (``CAT-17``, ``CAT-29``); its objects are constructed with
    their roots.  ``lean-categories`` does not yet formalize rooted diagrams;
    the request is recorded in research issue #439.
    """

    def super_categories(self):
        return [CoxeterDiagrams()]

    def an_object(self):
        return CoxeterDiagrams().from_cartan_type(["A", 2], rooted=True)

    @classmethod
    def _repr_object_names(cls):
        return "rooted Coxeter diagrams"

    class ParentMethods:
        def __init__(self, roots, root_gram, **rest) -> None:
            self._roots = roots
            self._root_gram = root_gram
            super().__init__(**rest)

        def roots(self):
            r"""The chosen roots, the owned family \(v\mapsto r_v\) over the vertices."""
            return self._roots

        def root_gram_tensor(self):
            return self._root_gram

        def root_realization(self):
            r"""Return the lattice in which the diagram roots are realized."""
            roots = self.roots()
            assert roots.cardinality() != 0, (
                f"{self} has no vertices, so it has no roots and no lattice in which they lie"
            )
            return next(iter(roots.values())).parent()

        def root_lattice(self):
            r"""Return the abstract lattice presented by the root Gram."""
            return Lattices(self.root_realization().base_ring())(
                self.root_gram_tensor()
            )

        def root_morphism(self):
            r"""Return the form morphism carrying each formal root to its realization."""
            return self.root_lattice().Mor(self.root_realization())(
                {position: root for position, root in enumerate(self.roots().values())}
            )

        def root(self, vertex):
            r"""Return the selected realizing root attached to ``vertex``."""
            return self.roots().value(vertex)

        def _engine_root_squares(self):
            if self._root_gram_engine_matrix is not None:
                return tuple(
                    QQ(self._root_gram_engine_matrix[index, index])
                    for index in range(int(self.cardinality()))
                )
            gram = self.root_gram_tensor()
            return tuple(
                QQ(_engine_element(gram.base_ring(), gram[index, index]))
                for index in range(int(self.cardinality()))
            )

        def _engine_root_scale(self):
            squares = self._engine_root_squares()
            assert squares and (
                all(square > 0 for square in squares)
                or all(square < 0 for square in squares)
            ), (
                f"{self} has no root scale: its root squares {squares} must be nonempty and of "
                "one sign, as the squares of a root basis are"
            )
            return min(squares, key=abs) / 2

        def root_scale(self):
            r"""Return the owned exact rational ``q(r)/2`` for a shortest root.

            The private root-square computation is carried out in Sage's
            rational field; cross that boundary through the owned rational
            constructor. Equality with exact Python rational literals is
            implemented by the owned scalar's canonical operand realization,
            not by exposing a foreign ``Fraction`` as this public result.
            """
            return _cross_engine_ring_value(self._engine_root_scale())

        def node_color(self, vertex):
            r"""Return the archived rooted-diagram fill convention determined by root square."""
            square = self.root(vertex).q()
            colors = {-4: "#F8F9FE", -2: "#BFC9CA"}
            square_key = int(square)
            if square_key not in colors:
                raise ValueError(
                    f"cannot draw the vertex {vertex} of {self}: node colors are defined for "
                    f"roots of square -2 and -4, and this root has square {square}"
                )
            return colors[square_key]

        def root_intersection_graph(self):
            r"""Return the root Gram matrix as a labelled graph."""
            gram = self.root_gram_tensor()
            positioned = tuple(enumerate(self.index_set()))
            edges = {
                (left, right): gram[i, j]
                for (i, left), (j, right) in combinations(positioned, 2)
                if gram[i, j] != 0
            }
            return LabelledGraphs().from_labels(
                tuple(self.index_set()),
                tuple(edges),
                {vertex: gram[position, position] for position, vertex in positioned},
                edges,
            )

        def _engine_root_intersection_graph(self):
            # Graph isomorphism and exact type recognition compare edge/loop
            # labels in Sage's graph backend. Use the selected private Gram
            # realization when available: owned scalar wrappers intentionally
            # retain their parent and do not compare equal to equal-valued
            # Sage scalars, which otherwise makes an identical reference root
            # graph fail its labelled isomorphism test.
            gram = self._root_gram_engine_matrix
            if gram is None:
                gram = _engine_component_matrix(self.root_gram_tensor())
            graph = Graph(multiedges=False, loops=True)
            graph.add_vertices(tuple(self.index_set()))
            for position, vertex in enumerate(self.index_set()):
                graph.add_edge(vertex, vertex, gram[position, position])
            for (i, left), (j, right) in combinations(enumerate(self.index_set()), 2):
                if gram[i, j] != 0:
                    graph.add_edge(left, right, gram[i, j])
            return graph

        def _root_pair_discriminant(self, left, right):
            gram = self.root_gram_tensor()
            ranking = self.index_set().ranking_map()
            i = ranking(left)
            j = ranking(right)
            return gram[i, j] ** 2 - gram[i, i] * gram[j, j]

        def mirrors_are_parallel(self, left, right) -> bool:
            return self._root_pair_discriminant(left, right) == 0

        def mirrors_are_divergent(self, left, right) -> bool:
            return self._root_pair_discriminant(left, right) > 0


__all__ = ["CoxeterDiagrams", "RootedCoxeterDiagrams"]


def _coxeter_diagram(coxeter_matrix, *, category=None, roots=None, root_gram=None, **data):
    r"""Construct the diagram of the owned Coxeter matrix ``coxeter_matrix`` through ``LabelledGraphs``.

    The Coxeter graph of \(m\) (vertices \(V\), an edge where
    \(m_{vw}\neq 2\), labelled \(m_{vw}\)) is constructed by
    ``LabelledGraphs().object``, which owns the finite-graph realization; the
    diagram adds the matrix and, for a rooted diagram, its roots
    (``OWN-14``).  ``category`` is ``RootedCoxeterDiagrams()`` when roots are
    supplied and ``CoxeterDiagrams()`` otherwise, unless a subcategory
    (such as Satake diagrams) constructs through here with its own data.
    """
    entries = _coxeter_entries_of(coxeter_matrix)
    vertices = tuple(dict.fromkeys(left for left, _right in entries))
    edges = tuple(
        (left, right) for left, right in combinations(vertices, 2) if entries[left, right] != 2
    )
    construction_data = dict(data, coxeter_matrix=coxeter_matrix)
    if roots is not None:
        construction_data.update(roots=roots, root_gram=root_gram)
    if category is None:
        category = RootedCoxeterDiagrams() if roots is not None else CoxeterDiagrams()
    return LabelledGraphs().object(
        vertices,
        edges,
        {vertex: "Coxeter vertex" for vertex in vertices},
        {edge: entries[edge] for edge in edges},
        categories=(category,),
        construction_data=construction_data,
    )
