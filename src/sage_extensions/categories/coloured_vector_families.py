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
with ``Sym_C(I)`` is not represented (research issue #428, *Products of infinite
groups are not represented*), so pairs ``(g, sigma)`` are not built and
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
"""

from itertools import permutations
from math import factorial, gcd

from sage.graphs.graph import Graph
from sage.groups.perm_gps.permgroup_named import SymmetricGroup
from sage.matrix.constructor import matrix as engine_matrix
from sage.misc.cachefunc import cached_function, cached_method
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

    Data: an owned finite ordered set of indices, the owned Gram tensor on
    the free module on those indices, and the owned colouring map of the
    indices.  For a degenerate span the owned family morphism is also
    retained, to record its linear relations.  The tensor is lowered once (``_engine_component_matrix``);
    the indices are lowered by their ``ranking_map``.  Leaving the adapter:
    an owned subgroup of the symmetric group on the indices, the induced
    permutations of the indices as set maps, and isomorphisms as set maps of
    indices.
    """

    def __init__(self, positions, gram, colouring, family=None):
        self._positions = positions
        self._gram = gram
        self._colouring = colouring
        self._family = family

    def _size(self):
        return int(self._positions.cardinality())

    def _vertex(self, position):
        return int(self._positions.ranking_map()(position))

    def _position(self, vertex):
        return self._positions.ranking_map().inverse()(int(vertex))

    @cached_method
    def _pairings(self):
        from sage_extensions.tensors.tensor import _engine_component_matrix

        return _engine_component_matrix(self._gram)

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
        if self._family is None:
            return (self._pairings(),)
        from sage_extensions.categories.modules.pure.modules import _engine_matrix

        family = _engine_matrix(self._family).transpose().change_ring(SageQQ)
        columns = family.matrix_from_columns(family.pivots())
        relations = columns * (columns.transpose() * columns).inverse() * columns.transpose()
        return self._pairings(), relations

    @cached_method
    def _graph(self):
        tables = self._pairing_tables()
        size = self._size()
        # GenericGraph.__eq__ compares edge labels only for weighted graphs.
        # The canonical forms must retain their actual colours and pairings.
        graph = Graph(loops=True, multiedges=False, weighted=True)
        graph.add_vertices(range(size))
        for left in range(size):
            colour = self._colouring(self._position(left))
            graph.add_edge(left, left, ("vertex", colour, tuple(table[left, left] for table in tables)))
            for right in range(left):
                pairings = tuple(table[left, right] for table in tables)
                if any(pairings):
                    graph.add_edge(left, right, ("pairing", pairings))
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
        # Sage's is_isomorphic expands edge labels into a dense partition
        # search. Bliss canonical labels retain an exact certificate using
        # its sparse graph engine (GenericGraph.canonical_label).
        source, source_certificate = self._graph().canonical_label(
            algorithm="bliss", edge_labels=True, certificate=True
        )
        target, target_certificate = other._graph().canonical_label(
            algorithm="bliss", edge_labels=True, certificate=True
        )
        if source != target:
            return None
        inverse_target = {image: vertex for vertex, image in target_certificate.items()}
        return Sets().Mor(self._positions, other._positions)(
            lambda position: other._position(inverse_target[source_certificate[self._vertex(position)]])
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
            self._vector = lambda index: values.projection(0)(family(index))
            self._colour = lambda index: values.projection(1)(family(index))

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
        r"""The module morphism ``F(I) -> L``, ``e_i |-> v_i``, through which the Gram matrix is pulled back."""
        return Modules(self._lattice.base_ring()).Mor(self.free_module(), self._lattice)(self.vector)

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
        pairing_rank = self.pairing_graph().rank()
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
        return _LabelledPairingGraph(
            self._indices, self.pairing_tensor(), self.colouring(),
            None if self.spans_rational_space() else self.family_morphism(),
        )

    def rationalization(self):
        r"""The lattice in its rational space, ``L -> Res(L tensor Q)``."""
        return ModulesOverIntegralDomains(self._lattice.base_ring())(self._lattice).generic_fibre_map()

    def rational_space(self):
        return self._lattice.base_change(self._lattice.base_ring().fraction_field_map())

    @cached_method
    def rational_family(self):
        r"""The family as the rational module morphism ``F_Q(I) -> L tensor Q``."""
        rational = self.rational_space()
        rationalization = self.rationalization()
        positions = rational.base_ring().free_module(self._indices)
        return Modules(rational.base_ring()).Mor(positions, rational)(
            lambda index: rationalization(self.vector(index)).underlying_element()
        )

    @cached_method
    def rational_span(self):
        rational = self.rational_space()
        family = self.rational_family()
        return rational.subobject_on(tuple(
            family(family.domain().module_generator(index)) for index in self.indices()
        ))

    @cached_method
    def family_section(self):
        r"""A section ``L tensor Q -> F_Q(I)`` of the surjective rational family, solved once on the framing."""
        family = self.rational_family()
        rational = self.rational_space()
        return Modules(rational.base_ring()).Mor(rational, family.domain())({
            label: family.lift(rational.module_generator(label))
            for label in rational.module_generating_set()
        })

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
        relabel = Modules(source_positions.base_ring()).Mor(source_positions, target_positions)(
            lambda index: target_positions.module_generator(sigma(index))
        )
        rational_target = target.rational_space()
        rational_source = self.rational_space()
        if not self.spans_rational_space():
            source_span, target_span = self.rational_span(), target.rational_span()
            source_inclusion, target_inclusion = source_span.inclusion(), target_span.inclusion()
            family = self.rational_family()
            partial = source_span.Isom(target_span)(
                lambda label: target_inclusion.lift(target_family(relabel(family.lift(
                    source_inclusion(source_span.module_generator(label))
                ))))
            )
            return partial.witt_extension(source_inclusion, target_inclusion)
        section = self.family_section()
        return rational_source.Isom(rational_target)(
            lambda label: target_family(relabel(section(rational_source.module_generator(label))))
        )

    @cached_method
    def configuration_isometry(self, generator):
        r"""The rational isometry induced by a pairing-graph automorphism."""
        graph = self.pairing_graph()
        rational = self.rational_space()
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
        return engine_matrix(
            SageZZ,
            tuple(
                tuple(
                    _engine_element(ring, self.vector(index).to_vector()(label))
                    for label in labels
                )
                for index in self.indices()
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
            sigma = Sets().Mor(self.indices(), self.indices())(
                lambda index: graph._position(permutation[graph._vertex(index)])
            )
            return self._rational_transformation_matrix(self.rational_transformation(self, sigma))
        family = self._family_coordinate_matrix()
        basis_rows, adjugate, determinant = self._coordinate_basis_data()
        target = engine_matrix(
            SageZZ,
            tuple(family.row(permutation[index]) for index in basis_rows),
        )
        numerator = adjugate * target
        return numerator.change_ring(SageQQ) / determinant

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


@cached_function(key=lambda lattice, family: (id(lattice), id(family)))
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
    composite = rational_source.Isom(rational_target)(
        lambda label: transporter(equivalence(rational_source.module_generator(label)))
    )
    restricted = composite.integral_restriction(source_lattice, target_lattice)
    assert restricted is not None, (
        f"the transporter {transporter} of the integral structures does not restrict to an isometry "
        f"{source_lattice} -> {target_lattice}"
    )
    return _homset_element(homset, restricted)


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
