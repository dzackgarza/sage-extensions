r"""Stabilizers and transporters of coloured families of lattice vectors in ``O(L)``.

A family of vectors of a lattice ``L`` is a set map ``v: I -> U(L)`` from a
finite set ``I``, an element of ``Sets().Mor(I, L)``.  A colouring is a set map
``c: I -> C``; a coloured family is the family of pairs ``(v_i, c_i)``, a map
``I -> U(L) x C`` that need not be injective (a Lorentzian perfect cell has
more rays than its rank, and a vector may repeat).  ``O(L)`` acts on these
families by ``g . (v_i, c_i) = (g v_i, c_i)``, and the questions asked are up
to colour-preserving reindexing (``CAT-30``):

- ``L.O().stabilizer(family)`` is
  ``O(L)_[v] = {g in O(L) : g o v = v o sigma for some colour-preserving bijection sigma of I}``;
- ``L.O().transporter(family, other)`` is one ``g`` with ``g o v = w o sigma``
  for some colour-preserving bijection ``sigma: I -> J``, or ``None``.

These are the images under ``(g, sigma) |-> g`` of the stabilizer and the
transporter of ``v`` under ``O(L) x Sym_C(I)`` acting on ``L^I`` by
``g o v o sigma^-1``.  The kernel of that projection on the stabilizer is
``K_v = {sigma in Sym_C(I) : v o sigma = v}``, the product of the full
symmetric groups on the sets ``{i : (v_i, c_i) = (x, col)}``; it is trivial
exactly when the coloured family is injective, and then
``sigma = (v, c)^-1 o (g x id) o (v, c)`` is determined by ``g``
(``L.O().index_action(family)``).  The product of the infinite group ``O(L)``
with ``Sym_C(I)`` is not represented, so pairs ``(g, sigma)`` are not built and
``K_v`` is stated, not constructed.

A family enters as the set map it is: an element of ``Sets().Mor(I, L)`` (one
colour) or of ``Sets().Mor(I, Sets().product((L, C)))`` (a coloured family).

The computation (Indefinite.jl@374a5ebb/indef/lib/AutomorphismPolytope.g,
KernelLinPolytopeIntegral_Automorphism_Subspaces :366-412 and
KernelLinPolytopeIntegral_Isomorphism_Subspaces :288-339).  The labelled
pairing graph ``Gamma`` has a vertex per index, labelled by its colour and
square, and an edge labelled by each nonzero pairing ``b(v_i, v_j)``;
``Aut(Gamma)`` is the group of colour- and pairing-preserving permutations of
``I`` (Sage's bliss/nauty backend, inside :class:`_LabelledPairingGraph`).
When the vectors span the nondegenerate rational space ``L tensor Q``, each
``sigma`` in ``Aut(Gamma)`` determines a unique rational isometry ``T_sigma``
with ``T_sigma(v_i) = v_sigma(i)``, computed by exact solving in the
rational space; ``rho: Aut(Gamma) -> O(L tensor Q)`` has kernel ``K_v`` and
image ``G``, and ``O(L)_[v] = G cap GL(L)`` is the stabilizer of the
integral structure ``L`` under ``G``, computed by
:class:`IntegralStructureAction` with the ``G``-stable bound ``K/e`` (``K``
the span of the vectors, ``e`` the exponent of ``L/K``).  The graph group is
never enumerated.  A family spanning an isotropic hyperplane of a
nondegenerate rational space also determines a unique ambient isometry.
For this case the graph additionally records the linear relations among the
vectors, and its isometries are extended by the codimension-one Witt
construction (polyhedral_common@1592b246, fund_domain_vertices.h,
``GetInitialComputation`` and ``MappingPermutationGenerators``).  Exact
lattice orbits impose integrality without requiring the family to have
finite index in the ambient lattice.  Other proper subspaces have a
nontrivial pointwise orthogonal stabilizer and remain outside this finite
configuration computation.

A family of at most eight vectors is searched on engine data, the
weighted-matrix test of the pinned source (fund_domain_vertices.h:507-530,
711-839).  The family rows, the colours of the indices and the pairing
tables are read once.  A backtrack enumerates the colour- and
table-preserving bijections of the positions.  Each gives ``T_sigma`` as an
integer row action: ``B^-1 B'`` on a spanning family, the coisotropic Witt
extension on an isotropic hyperplane.  ``T_sigma`` lies in ``O(L)`` or
``Isom(L, M)`` when that matrix is integral and unimodular.  Every element of
``O(L)_[v]`` is such a ``T_sigma``, so the integral ones are the whole
stabilizer, and a transporter exists exactly when some bijection gives an
integral one.  Only the returned isometries are raised, each once from its
matrix.  The stabilizer generators are chosen greedily from the elements, so
they can differ from those of the graph route; they generate the same group.
A larger family takes the labelled pairing graph and the integral-structure
action above.
"""

from itertools import permutations
from math import factorial, gcd

from sage.graphs.graph import Graph
from sage.graphs.bliss import canonical_form
from sage.groups.perm_gps.permgroup_named import SymmetricGroup
from sage.matrix.constructor import matrix as engine_matrix
from sage.misc.cachefunc import cached_method, weak_cached_function
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ

from sage_extensions.categories.modules.pure.modules import Modules, ModulesOverIntegralDomains
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _owned_engine_element,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets


class _LabelledPairingGraph:
    """Private adapter (OWN-06): the labelled pairing graph of a coloured family.

    Declared engine boundary, and the only site in this module holding a Sage
    ``Graph`` or integer vertex coordinates.  ``LabelledGraphs`` presents
    label-preserving ``Mor`` but no computed isomorphism or automorphism group
    (recorded in COMPLAINTS), so the bliss/nauty computations run here.

    Data: an owned finite ordered set of indices, the lattice's Gram tensor,
    the owned family morphism and the owned colouring map. The pairing
    matrix is the exact pullback F^t G F inside this adapter; constructing
    an intermediate owned tensor would allocate a scalar object per pair.
    For a proper span the family also records its linear relations.
    The lattice tensor is lowered once (``_engine_component_matrix``);
    the indices are lowered by their ``ranking_map``.  Leaving the adapter:
    an owned subgroup of the symmetric group on the indices, the induced
    permutations of the indices as set maps, and isomorphisms as set maps of
    indices.
    """

    def __init__(self, positions, gram, colouring, family, *, preserve_relations):
        self._positions = positions
        self._gram = gram
        self._colouring = colouring
        self._family = family
        self._preserve_relations = preserve_relations

    def _size(self):
        return int(self._positions.cardinality())

    @cached_method
    def _rankings(self):
        r"""The positions in ranking order and their ranks, read once from the ranking map."""
        unranking = self._positions.ranking_map().inverse()
        positions = tuple(unranking(vertex) for vertex in range(self._size()))
        return positions, {position: vertex for vertex, position in enumerate(positions)}

    def _vertex(self, position):
        return self._rankings()[1][position]

    def _position(self, vertex):
        return self._rankings()[0][int(vertex)]

    @cached_method
    def _pairings(self):
        from sage_extensions.tensors.tensor import _engine_component_matrix
        from sage_extensions.categories.modules.pure.modules import _engine_matrix

        family = _engine_matrix(self._family)
        return family.transpose() * _engine_component_matrix(self._gram) * family

    def rank(self):
        r"""The rank of the family pairing matrix, used only inside this engine adapter."""
        return self._pairings().rank()

    @cached_method
    def _pairing_tables(self):
        r"""Pairings and, when necessary, the canonical relation pairing.

        If ``F`` is the row family and ``C`` consists of independent columns,
        ``C (C^t C)^-1 C^t`` is the orthogonal projection onto the column
        space of ``F``.  A permutation preserves this matrix exactly when
        it preserves all linear relations among the rows.  This is the
        pairing induced by ``GetQmatrix_NotFullRank`` in the pinned
        ``PolytopeEquiStab.h``; it is independent of the selected columns.
        The original Gram matrix alone loses relations in a degenerate span.
        """
        if not self._preserve_relations:
            return (self._pairings(),)
        from sage_extensions.categories.modules.pure.modules import _engine_matrix

        family = _engine_matrix(self._family).transpose().change_ring(SageQQ)
        columns = family.matrix_from_columns(family.pivots())
        relations = columns * (columns.transpose() * columns).inverse() * columns.transpose()
        return self._pairings(), relations

    def _graph(self):
        tables = self._pairing_tables()
        size = self._size()
        # GenericGraph.__eq__ compares edge labels only for weighted graphs.
        # The canonical forms must retain their actual colours and pairings.
        graph = Graph(loops=True, multiedges=False, weighted=True)
        graph.add_vertices(range(size))
        edge_colours = {}
        for left in range(size):
            colour = self._colouring(self._position(left))
            graph.add_edge(left, left, ("vertex", colour, tuple(table[left, left] for table in tables)))
            for right in range(left):
                pairings = tuple(table[left, right] for table in tables)
                if any(pairings):
                    # Sage retains the supplied Python label on every edge.
                    # Equal pairings therefore share one exact label object.
                    label = edge_colours.setdefault(pairings, ("pairing", pairings))
                    graph.add_edge(left, right, label)
        return graph

    @cached_method
    def _symmetric_group(self):
        from sage_extensions.categories.group.groups import SymmetricGroups

        return SymmetricGroups()(self._positions)

    @cached_method
    def _small_automorphisms(self):
        r"""All exact table automorphisms when the family has at most eight positions."""
        size = self._size()
        if size > 8:
            return None
        tables = self._pairing_tables()
        colours = tuple(self._colouring(self._position(vertex)) for vertex in range(size))
        return tuple(
            permutation
            for permutation in permutations(range(size))
            if all(colours[vertex] == colours[permutation[vertex]] for vertex in range(size))
            and all(
                table[left, right]
                == table[permutation[left], permutation[right]]
                for table in tables
                for left in range(size)
                for right in range(size)
            )
        )

    @cached_method
    def engine_automorphism_group(self):
        r"""The exact engine permutation group of the labelled pairing table."""
        automorphisms = self._small_automorphisms()
        if automorphisms is None:
            return self._graph().automorphism_group(edge_labels=True)
        symmetric = SymmetricGroup(self._size())
        return symmetric.subgroup(
            tuple(symmetric([image + 1 for image in permutation]) for permutation in automorphisms)
        )

    def engine_permutation(self, element):
        r"""The zero-based tuple represented by an engine automorphism."""
        if self._small_automorphisms() is None:
            return tuple(int(element(vertex)) for vertex in range(self._size()))
        return tuple(int(element(vertex + 1)) - 1 for vertex in range(self._size()))

    @cached_method
    def automorphism_group(self):
        r"""``Aut(Gamma)``: the subgroup of ``S_m`` generated by the engine's automorphisms."""
        symmetric = self._symmetric_group()
        size = self._size()
        automorphisms = self._small_automorphisms()
        if automorphisms is not None:
            return symmetric.subgroup(
                tuple(
                    symmetric([permutation[vertex] + 1 for vertex in range(size)])
                    for permutation in automorphisms
                ),
                cardinality_decision=lambda: cardinal(len(automorphisms)),
            )
        engine = self.engine_automorphism_group()
        return symmetric.subgroup(tuple(
            symmetric([image + 1 for image in self.engine_permutation(generator)])
            for generator in engine.gens()
        ))

    @cached_method
    def automorphism_order(self):
        r"""The order of the labelled pairing-table automorphism group."""
        automorphisms = self._small_automorphisms()
        if automorphisms is not None:
            return cardinal(len(automorphisms))
        return cardinal(int(self.engine_automorphism_group().order()))

    @cached_method
    def automorphism_permutations(self):
        r"""All labelled pairing-table automorphisms as zero-based tuples."""
        small = self._small_automorphisms()
        if small is not None:
            return small
        engine = self.engine_automorphism_group()
        return tuple(
            self.engine_permutation(automorphism)
            for automorphism in engine
        )

    def position_permutation(self, automorphism):
        r"""The permutation of the indices induced by an element of ``Aut(Gamma)``."""
        return Sets().Mor(self._positions, self._positions)(
            automorphism
        )

    def isomorphism(self, other):
        r"""A colour- and pairing-preserving bijection of indices onto ``other``'s, or ``None``."""
        if self._size() != other._size():
            return None
        source_tables = self._pairing_tables()
        target_tables = other._pairing_tables()
        if len(source_tables) != len(target_tables):
            return None
        # Sage's Bliss canonical_form returns the exact vertex certificate.
        # Release its edge list and input graph before constructing the other
        # graph. The original tables certify the resulting bijection directly.
        source_certificate = canonical_form(
            self._graph(), use_edge_labels=True, certificate=True
        )[1]
        target_certificate = canonical_form(
            other._graph(), use_edge_labels=True, certificate=True
        )[1]
        inverse_target = {image: vertex for vertex, image in target_certificate.items()}
        images = tuple(inverse_target[source_certificate[vertex]] for vertex in range(self._size()))
        if any(
            self._colouring(self._position(vertex)) != other._colouring(other._position(image))
            for vertex, image in enumerate(images)
        ):
            return None
        if any(
            source != target.matrix_from_rows_and_columns(images, images)
            for source, target in zip(source_tables, target_tables, strict=True)
        ):
            return None
        source_ranking = self._positions.ranking_map()
        target_unranking = other._positions.ranking_map().inverse()
        return Sets().Mor(self._positions, other._positions)(
            lambda position: target_unranking(inverse_target[source_certificate[int(source_ranking(position))]])
        )


class _ColouredFamilyRealization:
    """Private realization of the linear algebra of a coloured family ``(v_i, c_i)_{i in I}`` in ``L``.

    The free modules on ``I`` here are computational: the Gram matrix of the
    family and the exact solving behind ``T_sigma`` are read through the
    module maps ``F(I) -> L`` and ``F_Q(I) -> L tensor Q``, ``e_i |-> v_i``;
    they are not how a family is defined.  Every value leaving this class is
    a preamble object.  Nothing is computed at construction (``OWN-22``).
    """

    def __init__(self, lattice, family):
        self._lattice = lattice
        self._family = family
        self._indices = family.domain()
        assert self._indices.cardinality().is_finite() is True, (
            f"stabilizers of families in O({lattice}) are computed for finite index sets, but {family} is "
            f"a map out of {self._indices}"
        )
        values = family.codomain()
        if values is lattice:
            self._colours = Sets.Δ[0]
            point = next(iter(self._colours))
            self._vector = family
            self._colour = lambda _index: point
        else:
            assert values.factor(0) is lattice, (
                f"{family} is neither a family of vectors of {lattice} nor of points of {lattice} x C: it is a "
                f"map into {values}"
            )
            self._colours = values.factor(1)
            vector_projection, colour_projection = values.projection(0), values.projection(1)
            self._vector = lambda index: vector_projection(family(index))
            self._colour = lambda index: colour_projection(family(index))

    def indices(self):
        return self._indices

    def vector(self, index):
        return self._vector(index)

    def colour(self, index):
        return self._colour(index)

    @cached_method
    def colouring(self):
        r"""The colouring ``c: I -> C``."""
        return Sets().Mor(self._indices, self._colours)(self.colour)

    @cached_method
    def free_module(self):
        r"""The free module on the indices, a computational device (see the class docstring)."""
        return self._lattice.base_ring().free_module(self._indices)

    @cached_method
    def family_morphism(self):
        r"""The module morphism ``F(I) -> L``, ``e_i |-> v_i``, through which the Gram matrix is pulled back.

        Column ``i`` of its framed matrix is the coordinate row of ``v_i``,
        read once for the family matrix.
        """
        from sage_extensions.categories.modules.pure.modules import _morphism_from_engine_matrix

        return _morphism_from_engine_matrix(
            Modules(self._lattice.base_ring()).Mor(self.free_module(), self._lattice),
            self._family_coordinate_matrix().transpose(),
        )

    @cached_method
    def span(self):
        r"""The sublattice ``K`` spanned by the family, with its inclusion into ``L``."""
        return self._lattice.subobject_on(tuple(self.vector(index) for index in self._indices))

    def assert_unique_rational_extension(self):
        lattice = self._lattice
        assert lattice.base_ring() is _owned_integers(), (
            f"stabilizers and transporters of coloured families of vectors are computed for lattices over ZZ, "
            f"but {lattice} is over {lattice.base_ring()}"
        )
        assert lattice.is_nondegenerate() is True, (
            f"the pairing permutation action of a family in {lattice} is faithful only when the lattice is "
            f"nondegenerate, and {lattice} is not known to be"
        )
        family_rank = self._family_coordinate_matrix().rank()
        ambient_rank = int(lattice.module_rank())
        pairing_rank = self._engine_pairing_rank()
        assert family_rank == ambient_rank or (
            family_rank == ambient_rank - 1 and pairing_rank == ambient_rank - 2
        ), (
            f"the vectors of {self._family} span a rational subspace of rank {family_rank} of {lattice}, "
            f"of rank {ambient_rank}, with pairing rank {pairing_rank}: this computation requires the full "
            f"space or an isotropic hyperplane, whose pointwise orthogonal stabilizer is trivial"
        )

    @cached_method
    def spans_rational_space(self):
        return self._family_coordinate_matrix().rank() == int(self._lattice.module_rank())

    @cached_method
    def pairing_tensor(self):
        r"""The Gram tensor of the indexed family."""
        generators = self._lattice.module_generating_set()
        if self._indices is generators and all(
            self.vector(index) == self._lattice.module_generator(index)
            for index in self._indices
        ):
            # The family morphism is the selected framing identity, so its
            # pullback is literally the Gram tensor already retained by L.
            return self._lattice.gram_tensor()
        return self._lattice.gram_tensor().pullback(self.family_morphism())

    @cached_method
    def pairing_graph(self):
        # The graph is private computation data. Its returned index maps
        # retain the owned rankings, not these quadratic-size graph tables.
        # One graph per realization, so its pairing tables are computed once.
        return _LabelledPairingGraph(
            self._indices, self._lattice.gram_tensor(), self.colouring(),
            self.family_morphism(),
            preserve_relations=not self.spans_rational_space(),
        )

    def rationalization(self):
        r"""The lattice in its rational space, ``L -> Res(L tensor Q)``."""
        return ModulesOverIntegralDomains(self._lattice.base_ring())(self._lattice).generic_fibre_map()

    def rational_space(self):
        return self._lattice.base_change(self._lattice.base_ring().fraction_field_map())

    @cached_method
    def rational_family(self):
        r"""The family as the rational module morphism ``F_Q(I) -> L tensor Q``."""
        from sage_extensions.categories.modules.pure.modules import _morphism_from_engine_matrix

        rational = self.rational_space()
        positions = rational.base_ring().free_module(self._indices)
        # The base change keeps the lattice framing, so column i is the
        # coordinate row of v_i already read once for the family matrix.
        return _morphism_from_engine_matrix(
            Modules(rational.base_ring()).Mor(positions, rational),
            self._family_coordinate_matrix().transpose().change_ring(SageQQ),
        )

    @cached_method
    def family_section(self):
        r"""A section ``L tensor Q -> F_Q(I)`` of the surjective rational family, solved once on the framing.

        Fundamental.g:378-425 FindTransformation selects an independent
        subfamily before solving. If ``j: Q^B -> Q^I`` includes its indices
        and ``B`` is the square matrix of the basis vectors, then
        ``j B^-1`` is a right inverse of the whole family: its rows at the
        basis positions are those of ``B^-1``, read from the retained
        adjugate and determinant, and its other rows are zero.
        """
        from sage.matrix.constructor import zero_matrix
        from sage_extensions.categories.modules.pure.modules import _morphism_from_engine_matrix

        family = self.rational_family()
        rational = self.rational_space()
        basis_rows, adjugate, determinant = self._coordinate_basis_data()
        inverse = (adjugate.change_ring(SageQQ) / determinant).transpose()
        section = zero_matrix(SageQQ, int(self._indices.cardinality()), inverse.ncols())
        for position, row in enumerate(basis_rows):
            section.set_row(row, inverse.row(position))
        return _morphism_from_engine_matrix(
            Modules(rational.base_ring()).Mor(rational, family.domain()), section
        )

    def rational_transformation(self, target, sigma):
        r"""The rational isometry ``T_sigma`` with ``T_sigma(v_i) = w_sigma(i)``.

        ``sigma`` is a set map of this family's indices onto ``target``'s.  For
        a colour-, relation- and pairing-preserving bijection, the induced
        map of the spans is computed by lifting coefficients along the
        source family.  For an isotropic hyperplane its unique Witt
        extension supplies the ambient isometry.
        """
        self.assert_unique_rational_extension()
        target.assert_unique_rational_extension()
        target_family = target.rational_family()
        source_positions = self.rational_family().domain()
        target_positions = target_family.domain()
        rational_target = target.rational_space()
        rational_source = self.rational_space()
        from sage_extensions.categories.modules.pure.modules import _engine_matrix, _morphism_from_engine_matrix

        if not self.spans_rational_space():
            # The unique Witt extension of the hyperplane map, computed on
            # the family rows and raised once, as below.
            linear = _morphism_from_engine_matrix(
                Modules(rational_source.base_ring()).Mor(rational_source, rational_target),
                self._hyperplane_transformation_rows(target, sigma).transpose(),
            )
            isometries = rational_source.Isom(rational_target)
            return isometries.element_class(isometries, linear)
        # T_sigma = w o relabel o section, the product of the framed
        # matrices, raised once instead of evaluated per generator.  The
        # relabelling is a permutation matrix, so w o relabel is w with its
        # columns taken in the order sigma gives.
        target_columns = {index: column for column, index in enumerate(target_positions.module_generating_set())}
        relabelled = _engine_matrix(target_family).matrix_from_columns(
            [target_columns[sigma(index)] for index in source_positions.module_generating_set()]
        )
        product = relabelled * _engine_matrix(self.family_section())
        linear = _morphism_from_engine_matrix(
            Modules(rational_source.base_ring()).Mor(rational_source, rational_target), product
        )
        isometries = rational_source.Isom(rational_target)
        return isometries.element_class(isometries, linear)

    @cached_method
    def configuration_isometry(self, generator):
        r"""The rational isometry induced by a pairing-graph automorphism."""
        graph = self.pairing_graph()
        rational = self.rational_space()
        if self.spans_rational_space():
            # Fundamental.g:378-425 FindTransformation uses the selected
            # independent rows. Reuse that exact coordinate computation
            # before constructing the owned isometry on its framing.
            permutation = tuple(
                graph._vertex(generator(graph._position(vertex)))
                for vertex in range(graph._size())
            )
            transformation = self._coordinate_automorphism(permutation)
            # The induced map sends generator s to row s of the
            # transformation, so its framed column matrix is the transpose,
            # raised once as in ``rational_transformation``.
            from sage_extensions.categories.modules.pure.modules import _morphism_from_engine_matrix

            linear = _morphism_from_engine_matrix(
                Modules(rational.base_ring()).Mor(rational, rational), transformation.transpose()
            )
            orthogonal = rational.O()
            return orthogonal.element_class(orthogonal, linear)
        isometry = self.rational_transformation(self, graph.position_permutation(generator))
        return rational.O()({
            label: isometry(rational.module_generator(label))
            for label in rational.module_generating_set()
        })

    @cached_method
    def configuration_generators(self):
        r"""Images in ``O(L tensor Q)`` of generators of ``Aut(Gamma)``.

        These generate ``rho(Aut(Gamma))`` directly.  Retaining them avoids
        reconstructing that image as an engine subgroup when a consumer needs
        only supplied generators.
        """
        graph = self.pairing_graph()
        self.assert_unique_rational_extension()
        automorphisms = graph.automorphism_group()
        return finite_ordered_set(tuple(
            self.configuration_isometry(generator)
            for generator in automorphisms.group_generators()
        ))

    @cached_method
    def stabilizer_cardinality(self):
        r"""``|Aut(Gamma)| / |K_v|``, the order of the family stabilizer.

        The kernel ``K_v`` consists exactly of the independent permutations
        of indices carrying the same vector and colour.
        """
        automorphism_order = int(self.pairing_graph().automorphism_order())
        return cardinal(automorphism_order // self.permutation_kernel_order())

    @cached_method
    def permutation_kernel_order(self):
        r"""The order of the permutations preserving every coloured vector."""
        classes = []
        for index in self.indices():
            value = self.vector(index)
            colour = self.colour(index)
            for position, (representative, representative_colour, multiplicity) in enumerate(classes):
                if representative == value and representative_colour == colour:
                    classes[position] = (representative, representative_colour, multiplicity + 1)
                    break
            else:
                classes.append((value, colour, 1))
        kernel_order = 1
        for _value, _colour, multiplicity in classes:
            kernel_order *= factorial(multiplicity)
        return kernel_order

    @cached_method
    def spans_lattice(self):
        r"""Whether the family generates the whole integral lattice."""
        invariants = self._family_coordinate_matrix().elementary_divisors()
        rank = int(self._lattice.module_rank())
        return len(invariants) >= rank and all(abs(invariant) == 1 for invariant in invariants[:rank])

    @cached_method
    def _family_coordinate_matrix(self):
        r"""Rows of family vectors in the lattice framing, at the private engine boundary."""
        labels = tuple(self._lattice.module_generating_set())
        ring = self._lattice.base_ring()
        # One coordinate vector per family vector; each row reads it at the labels.
        coordinates = tuple(self.vector(index).to_vector() for index in self.indices())
        return engine_matrix(
            SageZZ,
            tuple(
                tuple(_engine_element(ring, vector(label)) for label in labels)
                for vector in coordinates
            ),
        )

    @cached_method
    def _coordinate_basis_data(self):
        r"""The selected family basis rows, adjugate and determinant, computed once."""
        family = self._family_coordinate_matrix()
        from sage_extensions.tensors.tensor import _engine_row_basis_positions

        basis_rows = tuple(_engine_row_basis_positions(family))
        basis = family.matrix_from_rows(basis_rows)
        return basis_rows, basis.adjugate(), basis.det()

    def _integral_coordinate_automorphism(self, permutation):
        r"""The induced integral matrix, or ``None`` when the rational symmetry does not preserve the lattice."""
        transformation = self._coordinate_automorphism(permutation)
        if any(not entry.is_integer() for entry in transformation.list()):
            return None
        return transformation.change_ring(SageZZ)

    def _coordinate_automorphism(self, permutation):
        r"""The rational matrix induced on the lattice framing by a family permutation."""
        if not self.spans_rational_space():
            graph = self.pairing_graph()
            self.assert_unique_rational_extension()
            return self._hyperplane_transformation_rows(
                self, lambda index: graph._position(permutation[graph._vertex(index)])
            )
        family = self._family_coordinate_matrix()
        basis_rows, adjugate, determinant = self._coordinate_basis_data()
        target = engine_matrix(
            SageZZ,
            tuple(family.row(permutation[index]) for index in basis_rows),
        )
        numerator = adjugate * target
        return numerator.change_ring(SageQQ) / determinant

    def _hyperplane_transformation_rows(self, target, sigma):
        r"""The row action of ``T_sigma`` for a family spanning an isotropic hyperplane.

        The rows of the selected independent family vectors span the
        hyperplane ``H``; their images are the rows of ``target`` at the
        indices ``sigma`` gives.  ``H`` contains its radical, the isotropic
        normal, so it is coisotropic and its isometry onto the target
        hyperplane has the unique extension of the codimension-one Witt
        construction (``_engine_coisotropic_witt_rows``, the computation of
        ``LatticeIsometryMethods.witt_extension`` on these matrices).
        """
        from sage_extensions.tensors.tensor import (
            _engine_coisotropic_witt_rows,
            _engine_component_matrix,
            _engine_row_basis_positions,
        )

        family = self._family_coordinate_matrix()
        target_family = target._family_coordinate_matrix()
        basis_rows = tuple(_engine_row_basis_positions(family))
        indices = tuple(self.indices())
        target_rows = {index: row for row, index in enumerate(target.indices())}
        left = family.matrix_from_rows(basis_rows).change_ring(SageQQ)
        right = target_family.matrix_from_rows(
            [target_rows[sigma(indices[row])] for row in basis_rows]
        ).change_ring(SageQQ)
        left_form = _engine_component_matrix(self._lattice.gram_tensor()).change_ring(SageQQ)
        right_form = _engine_component_matrix(target._lattice.gram_tensor()).change_ring(SageQQ)
        extension = _engine_coisotropic_witt_rows(left_form, right_form, left, right)
        assert extension is not None, (
            f"the family {self._family} spans an isotropic hyperplane of {self._lattice}, so its "
            f"isometry onto the target hyperplane is coisotropic and extends"
        )
        return extension

    @cached_method
    def _engine_tables(self):
        r"""The colours of the indices and the pairing tables of the family rows, on engine data.

        ``F`` holds the family rows and ``G`` the lattice Gram matrix.  The
        pairing table is ``F G F^t``; for a proper span the relation table
        ``C (C^t C)^-1 C^t`` of independent columns ``C`` of ``F`` is added,
        the tables of :class:`_LabelledPairingGraph` read from the rows.  The
        table entries are Python lists, read once for the bijection search;
        the rational Gram matrix and the pairing matrix are returned beside them.
        """
        from sage_extensions.tensors.tensor import _engine_component_matrix

        family = self._family_coordinate_matrix()
        gram = _engine_component_matrix(self._lattice.gram_tensor())
        tables = [family * gram * family.transpose()]
        if not self.spans_rational_space():
            columns = family.change_ring(SageQQ)
            columns = columns.matrix_from_columns(columns.pivots())
            tables.append(columns * (columns.transpose() * columns).inverse() * columns.transpose())
        colours = tuple(self.colour(index) for index in self.indices())
        return colours, tuple(table.list() for table in tables), gram.change_ring(SageQQ), tables[0]

    @cached_method
    def _engine_pairing_rank(self):
        r"""The rank of the pairing table ``F G F^t`` of the family rows."""
        _colours, _tables, _gram, pairing = self._engine_tables()
        return pairing.rank()

    def _engine_bijections(self, target):
        r"""The colour- and table-preserving bijections of the indices onto ``target``'s, as position tuples.

        The weighted-matrix equivalence test of the pinned source
        (fund_domain_vertices.h:507-530, 711-839, through
        ``LORENTZ_TestEquivalence`` and ``LinPolytope_Automorphism`` on the
        weight matrix of colours and pairings): a backtrack that assigns the
        positions in order and keeps an assignment only when its colour, its
        diagonal entries and its entries against the positions already
        assigned agree in every table.
        """
        colours, tables, _gram, _pairing = self._engine_tables()
        target_colours, target_tables, _target_gram, _target_pairing = target._engine_tables()
        size = len(colours)
        if len(target_colours) != size or len(tables) != len(target_tables):
            return
        assignment = [0] * size
        used = [False] * size

        def consistent(position, image):
            for table, target_table in zip(tables, target_tables, strict=True):
                if table[position * size + position] != target_table[image * size + image]:
                    return False
                for earlier in range(position):
                    if table[position * size + earlier] != target_table[image * size + assignment[earlier]]:
                        return False
            return True

        def extend(position):
            if position == size:
                yield tuple(assignment)
                return
            for image in range(size):
                if used[image] or target_colours[image] != colours[position] or not consistent(position, image):
                    continue
                assignment[position] = image
                used[image] = True
                yield from extend(position + 1)
                used[image] = False

        yield from extend(0)

    def _engine_integral_transformation(self, target, images):
        r"""The integral row action ``X`` with ``v_i X = w_images[i]``, or ``None`` when ``T_sigma`` is not integral or not invertible over ZZ.

        On a spanning family ``X = B^-1 B'`` for the selected independent rows
        ``B`` and their images ``B'``; on an isotropic hyperplane ``X`` is the
        unique coisotropic Witt extension of the hyperplane map.
        """
        from sage_extensions.tensors.tensor import _engine_coisotropic_witt_rows, _engine_row_basis_positions

        family = self._family_coordinate_matrix()
        target_family = target._family_coordinate_matrix()
        if self.spans_rational_space():
            basis_rows, adjugate, determinant = self._coordinate_basis_data()
            numerator = adjugate * target_family.matrix_from_rows([images[row] for row in basis_rows])
            if any(entry % determinant for entry in numerator.list()):
                return None
            transformation = numerator.change_ring(SageQQ) / determinant
        else:
            basis_rows = tuple(_engine_row_basis_positions(family))
            transformation = _engine_coisotropic_witt_rows(
                self._engine_tables()[2],
                target._engine_tables()[2],
                family.matrix_from_rows(basis_rows).change_ring(SageQQ),
                target_family.matrix_from_rows([images[row] for row in basis_rows]).change_ring(SageQQ),
            )
            assert transformation is not None, (
                f"the family {self._family} spans an isotropic hyperplane of {self._lattice}, so its "
                f"isometry onto the target hyperplane is coisotropic and extends"
            )
            if any(entry.denominator() != 1 for entry in transformation.list()):
                return None
        transformation = transformation.change_ring(SageZZ)
        if transformation.det() not in (1, -1):
            return None
        transformation.set_immutable()
        return transformation

    def engine_transporter_rows(self, target):
        r"""The row action of one integral ``g`` with ``g o v = w o sigma``, or ``None``: the first integral ``T_sigma``."""
        for images in self._engine_bijections(target):
            transformation = self._engine_integral_transformation(target, images)
            if transformation is not None:
                return transformation
        return None

    @cached_method
    def engine_stabilizer_rows(self):
        r"""Row actions generating ``O(L)_[v]``, chosen greedily from its elements.

        Every ``g`` in the stabilizer is ``T_sigma`` for a colour- and
        table-preserving permutation ``sigma``, so the integral ``T_sigma`` are
        the whole finite group.  A ``T_sigma`` is kept when it lies outside
        the group generated by those kept before it, which is closed by
        products of the row actions.
        """
        size = int(self._lattice.module_rank())
        identity = engine_matrix(SageZZ, size, size, 1)
        identity.set_immutable()
        generated = {identity}
        generators = []
        for images in self._engine_bijections(self):
            transformation = self._engine_integral_transformation(self, images)
            if transformation is None or transformation in generated:
                continue
            generators.append(transformation)
            frontier = list(generated)
            while frontier:
                reached = []
                for element in frontier:
                    for generator in generators:
                        product = element * generator
                        product.set_immutable()
                        if product not in generated:
                            generated.add(product)
                            reached.append(product)
                frontier = reached
        return tuple(generators)

    @staticmethod
    def _rational_transformation_matrix(isometry):
        r"""Lower an owned rational isometry to row coordinates at this private boundary."""
        from sage_extensions.categories.modules.pure.modules import _engine_matrix

        source, target = isometry.domain(), isometry.codomain()
        linear = Modules(source.base_ring()).Mor(source, target)(isometry)
        return _engine_matrix(linear).transpose()

    @staticmethod
    def _rational_lattice_key(transformation):
        r"""Canonical row-Hermite data for the image of the standard integral lattice."""
        denominator = transformation.denominator()
        hermite = (denominator * transformation).change_ring(SageZZ).hermite_form()
        common = abs(int(denominator))
        for entry in hermite.list():
            common = gcd(common, abs(int(entry)))
        return (
            int(denominator) // common,
            tuple(int(entry) // common for entry in hermite.list()),
        )

    @cached_method
    def _integral_configuration_group_data(self):
        r"""Order and generators of pairing symmetries preserving the ambient lattice.

        ``Aut(Gamma)`` acts on the finite orbit of ``L`` among rational
        lattices.  Its stabilizer is computed from orbit representatives by
        Schreier's lemma.  Thus a finite-index family does not enumerate the
        graph group merely to test every element for integrality.
        """
        self.assert_unique_rational_extension()
        graph = self.pairing_graph()
        engine = graph.engine_automorphism_group()
        generators = tuple(engine.gens())
        generators += tuple(
            inverse for inverse in (generator**-1 for generator in generators)
            if inverse not in generators
        )
        identity = engine.one()

        def lattice_key(element):
            return self._rational_lattice_key(
                self._coordinate_automorphism(graph.engine_permutation(element))
            )

        representatives = [identity]
        indices = {lattice_key(identity): 0}
        schreier = []
        cursor = 0
        while cursor < len(representatives):
            representative = representatives[cursor]
            for generator in generators:
                candidate = representative * generator
                key = lattice_key(candidate)
                target = indices.get(key)
                if target is None:
                    target = len(representatives)
                    indices[key] = target
                    representatives.append(candidate)
                stabilizer_generator = candidate * representatives[target] ** -1
                permutation = graph.engine_permutation(stabilizer_generator)
                if permutation != tuple(range(len(permutation))) and permutation not in schreier:
                    assert self._integral_coordinate_automorphism(permutation) is not None
                    schreier.append(permutation)
            cursor += 1
        order, remainder = divmod(int(engine.order()), len(representatives))
        assert remainder == 0
        return order, tuple(schreier)

    def integral_configuration_transporter(self, target, equivalence):
        r"""An integral map in the rational configuration coset, or ``None``.

        The target graph group is finite, and uniqueness of extension makes
        its rational isometries a group.  Therefore its orbit on the lattice
        ``equivalence(L)`` is finite even when the family spans a hyperplane.
        Traversing that lattice orbit is the integral transporter
        computation in ``fund_domain_vertices.h:FindIntegralEquivalence``;
        no finite-index bound for the span is needed.
        """
        self.assert_unique_rational_extension()
        target.assert_unique_rational_extension()
        graph = target.pairing_graph()
        generators = tuple(
            target._coordinate_automorphism(graph.engine_permutation(generator))
            for generator in graph.engine_automorphism_group().gens()
        )
        rational_source, rational_target = self.rational_space(), target.rational_space()
        identity_key = self._rational_lattice_key(
            self._rational_transformation_matrix(rational_target.Isom(rational_target).identity())
        )
        first = self._rational_transformation_matrix(equivalence)
        representatives = [first]
        seen = {self._rational_lattice_key(first)}
        cursor = 0
        while cursor < len(representatives):
            representative = representatives[cursor]
            if self._rational_lattice_key(representative) == identity_key:
                source_labels = tuple(rational_source.module_generating_set())
                target_labels = tuple(rational_target.module_generating_set())
                ring = rational_target.base_ring()
                isometry = rational_source.Isom(rational_target)({
                    label: rational_target.linear_combination({
                        target_label: _owned_engine_element(ring, representative[row, column])
                        for column, target_label in enumerate(target_labels)
                        if representative[row, column]
                    })
                    for row, label in enumerate(source_labels)
                })
                restricted = isometry.integral_restriction(self._lattice, target._lattice)
                assert restricted is not None
                return restricted
            for generator in generators:
                candidate = representative * generator
                key = self._rational_lattice_key(candidate)
                if key not in seen:
                    seen.add(key)
                    representatives.append(candidate)
            cursor += 1
        return None

    @cached_method
    def integral_stabilizer_cardinality(self):
        r"""The number of distinct integral isometries induced by the configuration."""
        order, _generators = self._integral_configuration_group_data()
        return cardinal(order // self.permutation_kernel_order())

    @cached_method
    def integral_configuration_generator_images(self):
        r"""Images of lattice basis vectors for generators of the integral configuration subgroup."""
        _order, permutations = self._integral_configuration_group_data()
        return self._integral_configuration_images(permutations)

    def _integral_configuration_images(self, permutations):
        r"""Lattice-framing images of the selected integral family permutations."""
        labels = tuple(self._lattice.module_generating_set())
        ring = self._lattice.base_ring()
        images = []
        for permutation in permutations:
            transformation = self._integral_coordinate_automorphism(permutation)
            assert transformation is not None
            images.append(
                {
                    label: self._lattice.linear_combination(
                        {
                            target: ring(int(transformation[row, column]))
                            for column, target in enumerate(labels)
                            if transformation[row, column]
                        }
                    )
                    for row, label in enumerate(labels)
                }
            )
        return tuple(images)

    @cached_method
    def integral_configuration_element_images(self):
        r"""All integral isometries induced by the finite pairing symmetries.

        When the family spans the lattice, every permutation preserving its
        pairing and colours preserves the integral span.  The small pairing
        table therefore supplies the complete stabilizer enumeration without
        enumerating the ambient orthogonal group.
        """
        assert self.spans_lattice(), (
            "the full pairing-symmetry enumeration is integral only when the "
            "family spans the lattice"
        )
        return self._integral_configuration_images(
            self.pairing_graph().automorphism_permutations()
        )

    @cached_method
    def configuration_group(self):
        r"""``G = rho(Aut(Gamma))`` for the group morphism ``rho: Aut(Gamma) -> O(L tensor Q)``."""
        graph = self.pairing_graph()
        self.assert_unique_rational_extension()
        automorphisms = graph.automorphism_group()
        orthogonal = self.rational_space().O()
        rho = automorphisms.Mor(orthogonal)(self.configuration_isometry)
        return rho.image()

    @cached_method
    def containing_bound(self):
        r"""The exponent ``e`` of ``L/K`` and the ``G``-stable module ``K/e`` containing ``L``.

        ``G`` permutes the family, so ``K`` and ``K/e`` are stable, and ``eL``
        lies in ``K``.
        """
        lattice = self._lattice
        span = self.span()
        exponent = span.inclusion().cokernel().exponent()
        assert exponent > lattice.base_ring().zero(), (
            f"the vectors of {self._family} span a sublattice of infinite index in {lattice}, so no finite "
            f"stable module contains {lattice}"
        )
        rationalization = self.rationalization()
        ambient_space = rationalization.codomain()
        rational = self.rational_space()
        scale = rational.base_ring().one() / rational.base_ring()(exponent)
        inclusion = span.inclusion()
        containing = Modules(lattice.base_ring()).Mono(span, ambient_space)(
            lambda label: ambient_space.wrap(rational.scalar_multiple(
                scale, rationalization(inclusion(span.module_generator(label))).underlying_element(),
            ))
        )
        return exponent, containing


@weak_cached_function(cache=0, key=lambda lattice, family: (id(lattice), id(family)))
def _realization(lattice, family):
    return _ColouredFamilyRealization(lattice, family)


def _matching(source, target, isometry):
    r"""The bijection ``sigma`` with ``(g v_i, c_i) = (w_sigma(i), d_sigma(i))``, or ``None``.

    ``g o v = w o sigma`` for a colour-preserving bijection exactly when such a ``sigma`` exists.  Equality of
    points of ``L x C`` is an equivalence, so matching each index to any
    unmatched index carrying the same coloured vector finds a bijection
    whenever one exists.
    """
    target_indices = tuple(target.indices())
    if source.indices().cardinality() != target.indices().cardinality():
        return None
    used = set()
    images = {}
    for index in source.indices():
        image = isometry(source.vector(index))
        colour = source.colour(index)
        partner = next(
            (
                position
                for position, candidate in enumerate(target_indices)
                if position not in used
                and target.vector(candidate) == image
                and target.colour(candidate) == colour
            ),
            None,
        )
        if partner is None:
            return None
        used.add(partner)
        images[index] = target_indices[partner]
    return images


def _stabilizer_generators(orthogonal_group, family):
    r"""Generators of ``O(L)_[v]``: the stabilizer of ``L`` in ``G = rho(Aut(Gamma))``."""
    from sage_extensions.categories.rational_integral_stabilizers import IntegralStructureAction

    lattice = orthogonal_group.lattice()
    realization = _realization(lattice, family)
    if int(realization.indices().cardinality()) <= _ENGINE_SEARCH_SIZE:
        realization.assert_unique_rational_extension()
        return tuple(_isometry_from_rows(orthogonal_group, rows) for rows in realization.engine_stabilizer_rows())
    if not realization.spans_lattice():
        return tuple(
            orthogonal_group(images)
            for images in realization.integral_configuration_generator_images()
        )
    generators = realization.configuration_generators()
    if all(generator.integral_restriction(lattice, lattice) is not None for generator in generators):
        integral = generators
    else:
        rational_group = realization.configuration_group()
        _exponent, containing = realization.containing_bound()
        integral = IntegralStructureAction(rational_group, realization.rationalization()).with_stable_containing_bound(
            containing
        ).stabilizer().group_generators()
    return tuple(_homset_element(orthogonal_group, lattice.integral_isometry(generator)) for generator in integral)


def _transporter(homset, source_family, target_family):
    r"""One ``g`` in ``Isom(L, M)`` with ``g o v = w o sigma`` for a colour-preserving bijection ``sigma``, or ``None``.

    ``v`` is a family in ``L``, the domain of ``homset``, and ``w`` a family in
    ``M``, its codomain (``L = M`` for ``O(L)``).  A colour- and
    pairing-preserving bijection ``sigma`` gives the rational isometry
    ``T_0 = T_sigma``; every rational ``g`` carrying ``(v, c)`` to ``(w, d)``
    up to colour-preserving reindexing is ``h T_0`` with ``h`` in the
    configuration group ``G`` of the target.  An integral one carries
    ``T_0(L)`` to ``M``: the transporter of the integral-structure action of
    ``G``, bounded by the ``G``-stable module ``K'/e'``.  The exponent ``e`` of
    ``L/K`` is an invariant of the transport, so different exponents decide
    that there is none (AutomorphismPolytope.g:288-339,
    ``KernelLinPolytopeIntegral_Isomorphism_Subspaces``).
    """
    from sage_extensions.categories.rational_integral_stabilizers import IntegralStructureAction

    source_lattice = homset.domain()
    target_lattice = homset.codomain()
    source = _realization(source_lattice, source_family)
    target = _realization(target_lattice, target_family)
    if source.indices().cardinality() != target.indices().cardinality():
        return None
    if int(source.indices().cardinality()) <= _ENGINE_SEARCH_SIZE:
        source.assert_unique_rational_extension()
        target.assert_unique_rational_extension()
        rows = source.engine_transporter_rows(target)
        return None if rows is None else _isometry_from_rows(homset, rows)
    sigma = source.pairing_graph().isomorphism(target.pairing_graph())
    if sigma is None:
        return None
    equivalence = source.rational_transformation(target, sigma)
    restricted = equivalence.integral_restriction(source_lattice, target_lattice)
    if restricted is not None:
        return _homset_element(homset, restricted)
    if not source.spans_rational_space():
        restricted = source.integral_configuration_transporter(target, equivalence)
        return None if restricted is None else _homset_element(homset, restricted)
    source_exponent, _source_containing = source.containing_bound()
    target_exponent, containing = target.containing_bound()
    if source_exponent != target_exponent:
        return None
    rational_source = source.rational_space()
    rational_target = target.rational_space()
    source_rationalization = source.rationalization()
    target_rationalization = target.rationalization()
    ambient_space = target_rationalization.codomain()
    moved = Modules(source_lattice.base_ring()).Mono(source_lattice, ambient_space)(
        lambda label: ambient_space.wrap(
            equivalence(source_rationalization(source_lattice.module_generator(label)).underlying_element())
        )
    )
    transporter = IntegralStructureAction(target.configuration_group(), moved).with_stable_containing_bound(
        containing
    ).transporter(target_rationalization)
    if transporter is None:
        return None
    composite = transporter * equivalence
    restricted = composite.integral_restriction(source_lattice, target_lattice)
    assert restricted is not None, (
        f"the transporter {transporter} of the integral structures does not restrict to an isometry "
        f"{source_lattice} -> {target_lattice}"
    )
    return _homset_element(homset, restricted)


# A family of at most this many vectors is searched on engine data
# (``_ColouredFamilyRealization.engine_stabilizer_rows`` and
# ``engine_transporter_rows``): the bijections of at most 8! position tuples,
# the bound of ``_LabelledPairingGraph._small_automorphisms``.  A larger
# family takes the labelled pairing graph and the integral-structure action.
_ENGINE_SEARCH_SIZE = 8


def _isometry_from_rows(homset, rows):
    r"""The element of ``homset`` whose row action on the framings is the unimodular integral matrix ``rows``, raised once.

    Row ``s`` of ``rows`` is the coordinate row of the image of generator
    ``s``, so the framed matrix of the module map is its transpose (columns
    are images), as in ``LatticeIsometryMethods.integral_restriction``.  A
    matrix between free modules is a linear map by construction (``OWN-22``),
    so both factors are raised by the pre-validated matrix constructor.
    """
    from sage_extensions.categories.modules.pure.modules import _linear_arrow_from_engine_matrix

    source, target = homset.domain(), homset.codomain()
    forward_matrix = rows.transpose()
    backward_matrix = rows.inverse().change_ring(SageZZ).transpose()
    forward_matrix.set_immutable()
    backward_matrix.set_immutable()
    forward = _linear_arrow_from_engine_matrix(source.module_category().Mor(source, target), forward_matrix)
    backward = _linear_arrow_from_engine_matrix(source.module_category().Mor(target, source), backward_matrix)
    module_isomorphism = Modules(source.base_ring()).Core().Mor(source, target)(forward, backward)
    return homset.element_class(homset, module_isomorphism)


def _homset_element(homset, isometry):
    r"""The element of ``homset`` (``Isom(L, M)``, or ``O(L)``) acting as the lattice isometry ``isometry``."""
    domain = homset.domain()
    return homset(lambda label: isometry(domain.module_generator(label)))


def _is_family_in(value, lattice):
    r"""Whether ``value`` is a family ``I -> L`` or a coloured family ``I -> L x C`` of vectors of ``lattice``."""
    from sage.categories.homset import Homset
    from sage.structure.element import parent as element_parent

    homset = element_parent(value)
    if not isinstance(homset, Homset):
        return False
    values = homset.codomain()
    return values is lattice or (values is not None and hasattr(values, "factor") and values.factor(0) is lattice)


def _index_permutation(orthogonal_group, family, isometry):
    r"""``sigma = (v, c)^-1 o (g x id) o (v, c)`` on ``I``, for an injective coloured family.

    The caller has asserted injectivity (:func:`_assert_injective`); ``g`` lies
    in the stabilizer, so the matching exists and is unique.
    """
    realization = _realization(orthogonal_group.lattice(), family)
    images = _matching(realization, realization, isometry)
    assert images is not None, (
        f"{isometry} does not carry the coloured family {family} to itself up to colour-preserving "
        f"reindexing, so it is not in its stabilizer"
    )
    return images


def _assert_injective(orthogonal_group, family):
    r"""Assert that no two indices carry the same coloured vector, so that ``K_v`` is trivial."""
    realization = _realization(orthogonal_group.lattice(), family)
    indices = tuple(realization.indices())
    repeated = next(
        (
            (left, right)
            for position, left in enumerate(indices)
            for right in indices[position + 1:]
            if realization.vector(left) == realization.vector(right)
            and realization.colour(left) == realization.colour(right)
        ),
        (),
    )
    assert repeated == (), (
        f"the family {family} carries one coloured vector at two indices {repeated}, so an element of its "
        f"stabilizer determines a permutation of the indices only up to K_v, the permutations of the indices "
        f"carrying equal coloured vectors; the action on indices is defined for injective coloured families"
    )
    return realization
