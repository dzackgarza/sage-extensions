r"""Primitive totally isotropic sublattices, flags, and full-orthogonal-group orbits.

The orbit representatives, the equivalence witness and the stabilizer are
mathematical operations of this file; the algorithm realizing each one is
asked for by name from the ordered capability layer, so no engine is named
here.  An operation no registered provider supplies refuses by naming its
capability and what would provision it, which is the owned behaviour until a
provider arrives.
"""

from dataclasses import dataclass
from itertools import pairwise, product
from operator import index

from sage.matrix.constructor import matrix
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import parent as element_parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.modules.pure.modules import ModuleSubobjects
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.set_categories import NN, Sets, FiniteSets, CountableSets
from sage_extensions.owned_category import _object_of, owned_category_join


def _held(lattice, element):
    return element if element_parent(element) is lattice else lattice(element)


def _is_lattice_subobject_of_rank(sublattice, lattice, rank) -> bool:
    r"""Whether ``sublattice`` is a module subobject of ``lattice`` of module rank ``rank``."""
    return sublattice in ModuleSubobjects(lattice.base_ring()) and sublattice.inclusion().codomain() is lattice and int(sublattice.module_rank()) == int(rank)


class _PrimitiveIsotropicVectorOrbitEngine:
    r"""Private set realization of one primitive-isotropic vector orbit."""

    def __init__(self, group, locus, representative, **rest) -> None:
        self._group = group
        self._locus = locus
        self._representative = representative
        super().__init__(facade=True, **rest)

    def group(self):
        return self._group

    def universe(self):
        return self._locus

    def representative(self):
        return self._representative

    def stabilizer(self):
        return self.group().stabilizer(self.representative())

    def transporter_from(self, vector):
        return self.group().vector_equivalence_witness(
            vector,
            self.representative(),
        )

    def __contains__(self, vector) -> bool:
        return vector in self.universe() and self.transporter_from(vector) is not None

    is_parent_of = __contains__

    def _element_constructor_(self, vector):
        if vector not in self:
            raise ValueError(f"{vector} is not in {self}")
        return self.universe()(vector)

    def _repr_(self) -> str:
        return f"Primitive-isotropic orbit of {self.representative()} under {self.group()}"


def _primitive_isotropic_vector_orbit(group, locus, representative):
    return _object_of(
        Sets(),
        _engine=(Sets(), _PrimitiveIsotropicVectorOrbitEngine, None),
        group=group,
        locus=locus,
        representative=representative,
    )


class _FiniteOrbitDecompositionSetEngine:
    r"""Private finite-set realization shared by represented orbit decompositions."""

    def __iter__(self):
        return iter(self._orbits)

    def __contains__(self, orbit) -> bool:
        return orbit in self._orbits

    is_parent_of = __contains__

    def _element_constructor_(self, orbit):
        if orbit not in self:
            raise ValueError(f"{orbit} is not an orbit of {self}")
        return orbit

    def orbits(self):
        return self


class _PrimitiveIsotropicVectorOrbitDecompositionEngine(_FiniteOrbitDecompositionSetEngine):
    r"""The finite ``O(L)``-orbit decomposition of primitive isotropic vectors.

    Rank-one primitive isotropic sublattice orbits and primitive isotropic
    vector orbits coincide for the full orthogonal group: a line generator can
    only be sent to either generator of the target primitive line, and ``-id``
    belongs to ``O(L)``.  Thus the existing exact rank-one isotropic backend
    supplies the representatives, while vector stabilizers and transporters
    remain the already-owned group operations.
    """

    def __init__(self, group, locus, **rest) -> None:
        # The cached public locus can be a finite represented subset or a
        # condition set; its identity retains the same exact lattice in both.
        if locus is not group.lattice().primitive_isotropic_vectors():
            raise ValueError(f"{group} cannot act on {locus}: it is not the primitive isotropic vector locus of {group.lattice()}")
        self._group = group
        self._locus = locus
        representatives = []
        for line in group.isotropic_orbit_representatives(1):
            generator = line.module_generator(0)
            representatives.append(line.inclusion()(generator))
        self._orbits = finite_ordered_set(tuple(_primitive_isotropic_vector_orbit(group, locus, representative) for representative in representatives))
        super().__init__(facade=True, **rest)

    def group(self):
        return self._group

    def locus(self):
        return self._locus

    def representatives(self):
        return finite_ordered_set(tuple(orbit.representative() for orbit in self))

    def orbit_of(self, vector):
        if vector not in self.locus():
            raise ValueError(f"{vector} has no orbit in {self}: it is not a primitive isotropic vector of {self.group().lattice()}")
        for orbit in self:
            if vector in orbit:
                return orbit
        raise ArithmeticError(f"the primitive isotropic vector {vector} lies in none of the computed orbits {tuple(self)}, so the orbit decomposition is incomplete")

    def stabilizer(self, representative):
        return self.orbit_of(representative).stabilizer()

    def transporter(self, source, target):
        if source not in self.locus() or target not in self.locus():
            raise ValueError(f"cannot find an isometry carrying {source} to {target}: both must be primitive isotropic vectors of {self.group().lattice()}")
        return self.group().vector_equivalence_witness(source, target)


def _primitive_isotropic_vector_orbit_decomposition(group, locus):
    return _object_of(
        Sets().Finite(),
        _engine=(Sets(), _PrimitiveIsotropicVectorOrbitDecompositionEngine, None),
        group=group,
        locus=locus,
    )


class _IsotropicSublatticeLocusEngine:
    r"""Private set realization of isotropic sublattices of one fixed rank."""

    def __init__(self, lattice, rank, *, primitive=False, **rest) -> None:
        rank = index(rank)
        if rank < 0:
            raise ValueError(f"the isotropic sublattice rank must be nonnegative, got {rank} in {lattice}")
        self._lattice = lattice
        self._rank = NN(rank)
        self._primitive = bool(primitive)
        super().__init__(facade=True, **rest)

    def lattice(self):
        return self._lattice

    def rank(self):
        return self._rank

    def requires_primitive(self) -> bool:
        return self._primitive

    def __contains__(self, sublattice) -> bool:
        return (
            _is_lattice_subobject_of_rank(sublattice, self.lattice(), self.rank())
            and sublattice.is_totally_isotropic()
            and (not self.requires_primitive() or sublattice.is_primitive())
        )

    is_parent_of = __contains__

    def _element_constructor_(self, sublattice):
        if sublattice not in self:
            raise ValueError(f"{sublattice} is not in {self}")
        return sublattice

    def _repr_(self) -> str:
        qualifier = "primitive " if self.requires_primitive() else ""
        return f"{qualifier}totally isotropic rank-{self.rank()} sublattices of {self.lattice()}"


class _PrimitiveIsotropicSublatticeLocusEngine(_IsotropicSublatticeLocusEngine):
    r"""The primitive locus, with its arithmetic-group orbit construction."""

    def orbit_decomposition(self, group):
        r"""Return the decomposition of this locus into ``group``-orbits, its cusps."""
        return _primitive_isotropic_sublattice_orbit_decomposition(group, self)


class _PrimitiveIsotropicSublatticeOrbitDecompositionEngine(_FiniteOrbitDecompositionSetEngine):
    r"""The finite cusp decomposition of one primitive isotropic sublattice locus."""

    def __init__(self, group, locus, **rest) -> None:
        if group.supergroup().domain() is not locus.lattice():
            raise ValueError(f"{group} cannot act on {locus}: the group acts on {group.supergroup().domain()}, but the isotropic sublattices lie in {locus.lattice()}")
        self._group = group
        self._locus = locus
        self._orbits = group.cusps(rank=locus.rank())
        super().__init__(facade=True, **rest)

    def group(self):
        return self._group

    def locus(self):
        return self._locus

    def representatives(self):
        return finite_ordered_set(tuple(cusp.representative() for cusp in self))

    def orbit_of(self, sublattice):
        if sublattice not in self.locus():
            raise ValueError(f"{sublattice} has no orbit in {self}: it is not one of the primitive isotropic sublattices {self.locus()}")
        for cusp in self:
            if sublattice in cusp:
                return cusp
        raise ArithmeticError(f"the primitive isotropic sublattice {sublattice} lies in none of the computed cusps {tuple(self)}, so the cusp decomposition is incomplete")

    def stabilizer(self, sublattice):
        return self.orbit_of(sublattice).stabilizer()

    def transporter(self, source, target):
        if source not in self.locus() or target not in self.locus():
            raise ValueError(f"cannot find an isometry carrying {source} to {target}: both must be among the primitive isotropic sublattices {self.locus()}")
        return self.group().isotropic_equivalence_witness(source, target)


def _primitive_isotropic_sublattice_orbit_decomposition(group, locus):
    return _object_of(
        Sets().Finite(),
        _engine=(Sets(), _PrimitiveIsotropicSublatticeOrbitDecompositionEngine, None),
        group=group,
        locus=locus,
    )


class _IsotropicFlagLocusEngine:
    r"""Nested represented isotropic sublattices with prescribed ranks."""

    def __init__(self, lattice, ranks, **rest) -> None:
        ranks = tuple(int(rank) for rank in ranks)
        if not ranks or any(rank <= 0 for rank in ranks):
            raise ValueError(f"there are no isotropic flags in {lattice} with ranks {ranks}: a flag needs at least one term, and every rank must be positive")
        if any(left >= right for left, right in zip(ranks, ranks[1:])):
            raise ValueError(f"there are no isotropic flags in {lattice} with ranks {ranks}: the ranks of a flag must be strictly increasing")
        self._lattice = lattice
        self._ranks = ranks
        super().__init__(facade=True, **rest)

    def lattice(self):
        return self._lattice

    def ranks(self):
        return self._ranks

    def __contains__(self, flag) -> bool:
        match flag:
            case IsotropicFlag():
                terms = tuple(flag.terms())
            case tuple() | list():
                terms = tuple(flag)
            case _:
                return False
        if len(terms) != len(self.ranks()):
            return False
        if any(term not in _isotropic_sublattice_locus(self.lattice(), rank) for term, rank in zip(terms, self.ranks(), strict=True)):
            return False
        return all(_factors_through(smaller.inclusion(), larger.inclusion()) for smaller, larger in zip(terms, terms[1:]))

    is_parent_of = __contains__

    def _element_constructor_(self, flag):
        if flag not in self:
            raise ValueError(f"{flag} is not in {self}")
        return flag

    def _repr_(self) -> str:
        return f"Totally isotropic flags of ranks {self.ranks()} in {self.lattice()}"


def _isotropic_locus_placement(lattice):
    r"""Finite-rank sublattices of a finite/countable lattice form a finite/countable set.

    A finite-rank sublattice is determined by a finite tuple of vectors;
    finite flags of such sublattices obey the same cardinality bound.
    """
    match lattice in FiniteSets(), lattice in CountableSets():
        case True, _:
            return FiniteSets()
        case _, True:
            return CountableSets()
        case _:
            return Sets()


def _primitive_isotropic_sublattice_locus(lattice, rank):
    return _object_of(
        _isotropic_locus_placement(lattice),
        _engine=(Sets(), _PrimitiveIsotropicSublatticeLocusEngine, None),
        lattice=lattice,
        rank=rank,
        primitive=True,
    )


def _isotropic_sublattice_locus(lattice, rank):
    return _object_of(
        _isotropic_locus_placement(lattice),
        _engine=(Sets(), _IsotropicSublatticeLocusEngine, None),
        lattice=lattice,
        rank=rank,
        primitive=False,
    )


def _isotropic_flag_locus(lattice, ranks):
    return _object_of(
        _isotropic_locus_placement(lattice),
        _engine=(Sets(), _IsotropicFlagLocusEngine, None),
        lattice=lattice,
        ranks=tuple(ranks),
    )


@dataclass(frozen=True)
class FlagType:
    r"""The strictly increasing ranks of the terms of a nonempty flag."""

    dimensions: tuple[int, ...]

    def __post_init__(self) -> None:
        dimensions = tuple(int(dimension) for dimension in self.dimensions)
        match dimensions:
            case ():
                raise ValueError("a flag type needs at least one positive dimension")
            case _ if any(dimension <= 0 for dimension in dimensions):
                raise ValueError(f"flag dimensions must be positive, got {dimensions}")
            case _ if any(
                dimensions[index] >= dimensions[index + 1]
                for index in range(len(dimensions) - 1)
            ):
                raise ValueError(f"flag dimensions must be strictly increasing, got {dimensions}")
            case _:
                object.__setattr__(self, "dimensions", dimensions)

    @classmethod
    def plane(cls, rank: int) -> "FlagType":
        r"""Return the type of a one-term flag of rank ``rank``."""
        return cls((int(rank),))

    @classmethod
    def complete(cls, rank: int) -> "FlagType":
        r"""Return the complete flag type ``1 < 2 < ... < rank``."""
        return cls(tuple(range(1, int(rank) + 1)))

    @property
    def block_sizes(self) -> tuple[int, ...]:
        r"""Return the successive rank increments of the flag."""
        previous = (0, *self.dimensions[:-1])
        return tuple(right - left for left, right in zip(previous, self.dimensions, strict=True))


class IsotropicFlag:
    r"""A primitive totally isotropic flag, recorded by its nested lattice subobjects."""

    def __init__(self, lattice, basis, *, flag_type=None) -> None:
        self._lattice = lattice
        self._basis = tuple(_held(lattice, element) for element in basis)
        if not self._basis:
            raise ValueError(f"cannot form an isotropic flag in {lattice} from an empty basis")
        if flag_type is None:
            flag_type = FlagType.complete(len(self._basis))
        if flag_type.dimensions[-1] != len(self._basis):
            raise ValueError(f"the flag type {flag_type} must end at the basis rank {len(self._basis)}")
        self._terms = tuple(lattice.primitive_isotropic_subobject(*self._basis[:rank]) for rank in flag_type.dimensions)

    def lattice(self):
        return self._lattice

    def isotropic_basis(self):
        return self._basis

    def basis(self):
        r"""Return the ordered isotropic basis defining the flag."""
        return self.isotropic_basis()

    def rank(self):
        r"""Return the rank of the top isotropic sublattice."""
        return self.top().module_rank()

    def terms(self):
        return finite_ordered_set(self._terms)

    def flag_length(self):
        r"""Return how many terms this flag has.

        This counts the steps of the flag and is not a rank: the terms are
        subobjects of growing rank, and the flag's own invariant is how many
        of them there are.
        """
        return finite_ordered_set(self._terms).cardinality()

    def top(self):
        return self._terms[-1]

    def flag_type(self) -> "FlagType":
        r"""Return the ranks of the nested primitive isotropic terms."""
        return FlagType(tuple(int(term.module_rank()) for term in self._terms))

    def face(self, index):
        r"""Return the flag with the term of position ``index`` removed (the face map ``d_index``)."""
        dimensions = self.flag_type().dimensions
        if not 0 <= index < len(dimensions) or len(dimensions) == 1:
            raise ValueError(f"{self} has no face of index {index}")
        remaining = dimensions[:index] + dimensions[index + 1:]
        return IsotropicFlag(self._lattice, self._basis[: remaining[-1]], flag_type=FlagType(remaining))

    def invariant(self):
        r"""Return the source's invariant of this flag under the orthogonal group."""
        from sage_indefinite_port.indefinite.marked_lattices import INDUCTION

        return INDUCTION.flag_invariant(self._lattice, self._basis, self.flag_type().dimensions)

    def graded_quotient_action(self, group):
        r"""Return the action ``Stab_G(F) -> GL(gr F + I_t^perp/I_t)`` on successive quotients.

        ``group`` is ``G <= O(L)``: ``O(L)`` itself, or a finite-index subgroup
        of it, whose stabilizer is ``G cap Stab_{O(L)}(F)``.

        The codomain is the general linear group of a free module with one
        coordinate block for each ``I_j/I_{j-1}``, in the adapted basis, and a
        final block for ``I_t^perp/I_t``. The morphism is block diagonal, so
        its image is the actual image in the product of the block groups.
        """
        ring = self._lattice.base_ring()
        ambient = self._lattice.O()
        full = ambient.subgroup(tuple(ambient.isotropic_stabilizer_generators(self, flag=True)))
        if group is ambient:
            stabilizer = full
        else:
            if group.supergroup() is not ambient:
                raise ValueError(f"{group} is not a subgroup of {ambient}")
            stabilizer = group.intersection(full)
        rank = len(self._basis)
        adapted_module = ring.free_module(rank)
        top_inclusion = self.top().inclusion()
        adapted = adapted_module.Mor(top_inclusion.domain())(
            dict(zip(adapted_module.module_generating_set(), (top_inclusion.lift(point) for point in self._basis), strict=True))
        )
        adapted_labels = tuple(adapted_module.module_generating_set())
        previous = (0, *self.flag_type().dimensions[:-1])
        block_of = tuple(
            index for index, (left, right) in enumerate(zip(previous, self.flag_type().dimensions, strict=True))
            for _ in range(left, right)
        )
        reduction = self.top().isotropic_reduction()
        quotient = reduction.quotient_lattice()
        quotient_labels = tuple(quotient.module_generating_set())
        graded = ring.free_module(rank + len(quotient_labels))
        graded_labels = tuple(graded.module_generating_set())
        general_linear = graded.general_linear_group()
        levi = reduction.levi_action()

        def graded_image(isometry):
            def isotropic_row(position):
                coordinates = adapted.lift(top_inclusion.lift(isometry(self._basis[position]))).to_vector()
                return tuple(
                    coordinates(label) if block_of[index] == block_of[position] else ring.zero()
                    for index, label in enumerate(adapted_labels)
                ) + (ring.zero(),) * len(quotient_labels)

            quotient_isometry = levi(isometry)

            def quotient_row(label):
                coordinates = quotient_isometry(quotient.module_generator(label)).to_vector()
                return (ring.zero(),) * rank + tuple(coordinates(other) for other in quotient_labels)

            rows = (*(isotropic_row(position) for position in range(rank)), *(quotient_row(label) for label in quotient_labels))
            return general_linear({
                label: graded.linear_combination(dict(zip(graded_labels, row, strict=True)))
                for label, row in zip(graded_labels, rows, strict=True)
            })

        return stabilizer.Mor(general_linear)(graded_image)

    def rational_stabilizer_right_cosets(self):
        r"""Return a transversal of ``G/H`` for the rational stabilizer ``G`` of this flag's perpendicular."""
        from sage_indefinite_port.indefinite.marked_lattices import isotropic_stabilizer_right_cosets

        return isotropic_stabilizer_right_cosets(
            _marked_isotropic_category(self._lattice, len(self._terms)), _marked_isotropic_object(self, flag=True)
        )

    def __repr__(self) -> str:
        return f"Primitive totally isotropic flag of length {self.flag_length()} in {self.lattice()}"


class RationalIsotropicFlagComplex:
    r"""The quotient by a group ``G <= O(L)`` of the flags of rational isotropic subspaces (#45).

    A simplex orbit is a flag orbit of a :class:`FlagType`. Faces forget a
    term of the chosen representative and are transported, with an actual
    isometry, to the chosen representative of the face orbit.
    """

    def __init__(self, group) -> None:
        self._group = group

    def group(self):
        return self._group

    def simplex_orbits(self, flag_type):
        r"""Return the chosen representatives of the orbits of flags of ``flag_type``."""
        return self._group.isotropic_orbit_representatives(flag_type, flag=True)

    def face_map(self, flag, index):
        r"""Return the representative of the orbit of ``d_index(flag)`` and an isometry carrying the face to it."""
        face = flag.face(index)
        for representative in self.simplex_orbits(face.flag_type()):
            witness = self._group.isotropic_equivalence_witness(face, representative, flag=True)
            if witness is not None:
                return representative, witness
        raise ArithmeticError(f"the face {face} lies in no listed orbit of {self._group}")

    def stabilizer_generators(self, flag):
        r"""Return generators of the setwise stabilizer of a simplex."""
        return self._group.isotropic_stabilizer_generators(flag, flag=True)

    def face_stabilizer_image(self, flag, index):
        r"""Return the image of the stabilizer of ``flag`` in the stabilizer of its face.

        Stabilizing a chain stabilizes each term, so the map is the
        restriction of the same isometries.
        """
        return self.stabilizer_generators(flag)

    def incidence_multiplicity(self, flag_type, index, face_representative):
        r"""Return the number of orbits of ``flag_type`` whose ``index`` face lies in the given orbit.

        This counts flag orbits. It is neither an orbifold weight nor a
        number of flags in an infinite orbit.
        """
        return sum(
            1 for flag in self.simplex_orbits(flag_type)
            if self._group.isotropic_equivalence_witness(flag.face(index), face_representative, flag=True) is not None
        )


def _isotropic_orbit_iterator(group, lattice, rank, height_bound):
    r"""Duplicate-free first members of the ``group``-orbits (#62); an unbounded walk certifies no completion."""
    from sage_indefinite_port.indefinite.orbit_iterators import (
        canonical_orbit_representatives,
        primitive_isotropic_hermite_subobjects,
    )

    return canonical_orbit_representatives(
        primitive_isotropic_hermite_subobjects(lattice, rank, height_bound),
        group.isotropic_are_equivalent,
    )


class OrientedIsotropicFlag:
    r"""A primitive isotropic flag with an orientation of each ``I_j/I_{j-1}``.

    The orientation is the one of the adapted basis. An oriented primitive
    isotropic sublattice is the case of one block.
    """

    def __init__(self, lattice, basis, *, flag_type=None) -> None:
        self._flag = IsotropicFlag(lattice, basis, flag_type=flag_type or FlagType((len(tuple(basis)),)))

    def flag(self):
        return self._flag

    def lattice(self):
        return self._flag.lattice()

    def basis(self):
        return self._flag.basis()

    def __repr__(self) -> str:
        return f"Oriented {self._flag}"


def _graded_orientation_signs(isometry, source, target):
    r"""The determinant sign of ``isometry`` on each block, from the source to the target adapted basis."""
    ring = source.lattice().base_ring()
    target_inclusion = target.top().inclusion()
    module = ring.free_module(len(target.basis()))
    adapted = module.Mor(target_inclusion.domain())(
        dict(zip(module.module_generating_set(), (target_inclusion.lift(point) for point in target.basis()), strict=True))
    )
    labels = tuple(module.module_generating_set())
    rows = tuple(
        tuple(adapted.lift(target_inclusion.lift(isometry(point))).to_vector()(label) for label in labels)
        for point in source.basis()
    )
    dimensions = source.flag_type().dimensions
    return tuple(
        int(matrix(SageZZ, [[int(entry) for entry in row[left:right]] for row in rows[left:right]]).determinant())
        for left, right in zip((0, *dimensions[:-1]), dimensions, strict=True)
    )


def _orientation_group_elements(group, flag):
    r"""Map each attained sign tuple of ``Stab(flag)`` to a stabilizer element, and return the generators."""
    generators = tuple(group.isotropic_stabilizer_generators(flag, flag=True))
    signs = {generator: _graded_orientation_signs(generator, flag, flag) for generator in generators}
    identity = tuple(1 for _ in flag.flag_type().dimensions)
    transversal = {identity: group.one()}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            moved = tuple(left * right for left, right in zip(signs[generator], current, strict=True))
            if moved not in transversal:
                transversal[moved] = generator * transversal[current]
                frontier.append(moved)
    return generators, signs, transversal


def _oriented_isotropic_orbit_representatives(group, flag_type):
    r"""One oriented flag per class: each flag class splits by the sign cosets of its stabilizer image."""
    lattice = group.domain()
    representatives = []
    for flag in group.isotropic_orbit_representatives(flag_type, flag=True):
        _generators, _signs, transversal = _orientation_group_elements(group, flag)
        seen = set()
        for orientation in product((1, -1), repeat=len(flag_type.dimensions)):
            if orientation in seen:
                continue
            seen.update(tuple(left * right for left, right in zip(orientation, attained, strict=True)) for attained in transversal)
            basis = list(flag.basis())
            for sign, stop in zip(orientation, flag_type.dimensions, strict=True):
                if sign == -1:
                    basis[stop - 1] = -basis[stop - 1]
            representatives.append(OrientedIsotropicFlag(lattice, basis, flag_type=flag_type))
    return finite_ordered_set(tuple(representatives))


def _oriented_isotropic_equivalence_witness(group, left, right):
    r"""An isometry carrying one oriented flag to another with both orientations, or ``None``."""
    witness = group.isotropic_equivalence_witness(left.flag(), right.flag(), flag=True)
    if witness is None:
        return None
    _generators, _signs, transversal = _orientation_group_elements(group, left.flag())
    correction = transversal.get(_graded_orientation_signs(witness, left.flag(), right.flag()))
    return None if correction is None else witness * correction


def _oriented_isotropic_stabilizer_generators(group, oriented):
    r"""Schreier generators of the kernel of ``Stab(F) -> {+-1}^blocks``."""
    generators, signs, transversal = _orientation_group_elements(group, oriented.flag())
    schreier = []
    for attained, representative in transversal.items():
        for generator in generators:
            moved = tuple(left * right for left, right in zip(signs[generator], attained, strict=True))
            element = ~transversal[moved] * generator * representative
            if element != group.one():
                schreier.append(element)
    return finite_ordered_set(tuple(schreier))


class _CuspEngine:
    r"""One ``O(L)``-orbit of primitive totally isotropic subobjects of a rank.

    A cusp is the orbit itself, so membership is its primary operation:
    ``subobject in cusp`` asks the exact indefinite backend for an isometry
    carrying the stated subobject to this orbit and answers whether one
    exists.  ``representative`` is the member that backend chose, and
    ``transporter_witness`` returns one isometry realizing a membership.

    The set of primitive isotropic subobjects is infinite whenever the lattice
    is indefinite and isotropic, so this orbit is not a finite ``G``-set
    quotient and does not present its points.  What is finite is the number of
    cusps, which is why ``cusps`` enumerates them and no cusp enumerates its
    members.

    For rank one the stabilizer is the cusp's arithmetic group ``Gamma_v =
    P_v``, delivered as the representative's ``parabolic_subgroup``; its
    ``unipotent_radical`` and Eichler transvections describe the boundary
    component, and ``reduction_lattice`` is the lattice ``v^perp/v`` in which
    that component's reflection group acts.
    """

    def __init__(self, representative, **rest) -> None:
        self._representative = representative
        super().__init__(facade=True, **rest)

    def universe(self):
        return _primitive_isotropic_sublattice_locus(
            self.lattice(),
            self.module_rank(),
        )

    def lattice(self):
        return self._representative.ambient_lattice()

    def module_rank(self):
        return self._representative.module_rank()

    def representative(self):
        r"""Return the selected representative of this orbit."""
        return self._representative

    def __eq__(self, other) -> bool:
        r"""Compare orbits in the same lattice, independently of representatives."""
        if self is other:
            return True
        if not (
            isinstance(other, _CuspEngine)
            and other.lattice() is self.lattice()
            and other.module_rank() == self.module_rank()
        ):
            return False
        if _same_subobject(self.representative(), other.representative()):
            return True
        return self.transporter_witness(other.representative()) is not None

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        # Representatives are not canonical.  Every orbit in this universe
        # therefore shares a hash, while exact equality distinguishes them.
        return hash((_CuspEngine, id(self.lattice()), int(self.module_rank())))

    def parabolic_subgroup(self):
        r"""Return ``Gamma = Stab_{O(L)}(I)`` of the representative."""
        return self._representative.parabolic_subgroup()

    stabilizer = parabolic_subgroup

    def stabilizer_generators(self):
        r"""Return generators of the representative's stabilizer."""
        return self.lattice().Aut().isotropic_stabilizer_generators(self._representative)

    def reduction_lattice(self):
        r"""Return ``I^perp/I``, the lattice this boundary component acts in."""
        return self._representative.isotropic_reduction()

    def transporter_witness(self, subobject):
        r"""Return one ``g`` in ``O(L)`` carrying ``subobject`` to the representative.

        The full transporter is a coset of the subobject's own parabolic
        subgroup, infinite whenever that group is; one witness together with
        ``parabolic_subgroup`` presents it.
        """
        return subobject.transporter_witness_to(self._representative)

    def __contains__(self, subobject) -> bool:
        if subobject not in self.universe():
            return False
        return self.transporter_witness(subobject) is not None

    is_parent_of = __contains__

    def _element_constructor_(self, subobject):
        if subobject not in self:
            raise ValueError(f"{subobject} is not in {self}")
        return subobject

    def _repr_(self) -> str:
        return f"Cusp of rank {self.module_rank()} in {self.lattice()}"


class _ArithmeticCuspEngine:
    r"""One orbit of primitive isotropic subobjects under an arithmetic subgroup.

    The subgroup is part of the object.  Its stabilizer is therefore the
    actual intersection ``Gamma cap P_I``, not the full parabolic in
    ``O(L)``.  Membership retains an explicit transporter lying in ``Gamma``.
    """

    def __init__(self, subgroup, representative, **rest) -> None:
        if subgroup.supergroup().domain() is not representative.ambient_lattice():
            raise ValueError(
                f"{representative} cannot represent a cusp of {subgroup}: the group acts on {subgroup.supergroup().domain()}, but {representative} lies in {representative.ambient_lattice()}"
            )
        self._subgroup = subgroup
        self._representative = representative
        super().__init__(facade=True, **rest)

    def universe(self):
        return _primitive_isotropic_sublattice_locus(
            self.lattice(),
            self.module_rank(),
        )

    def subgroup(self):
        return self._subgroup

    def lattice(self):
        return self.subgroup().supergroup().domain()

    def module_rank(self):
        return self.representative().module_rank()

    def representative(self):
        return self._representative

    def __eq__(self, other) -> bool:
        r"""Compare orbits of this subgroup using its exact transporter."""
        if self is other:
            return True
        if not (
            isinstance(other, _ArithmeticCuspEngine)
            and other.subgroup() is self.subgroup()
            and other.module_rank() == self.module_rank()
        ):
            return False
        if _same_subobject(self.representative(), other.representative()):
            return True
        return self.transporter_witness(other.representative()) is not None

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(
            (_ArithmeticCuspEngine, id(self.subgroup()), int(self.module_rank()))
        )

    def stabilizer(self):
        r"""Return ``Gamma cap P_I`` for the chosen representative ``I``."""
        from sage_extensions.categories.group.predicate_subgroups import (
            StabilizerSubgroups,
        )

        parabolic = self.representative().parabolic_subgroup()
        from sage_extensions.categories.group.classifying_categories import ClassifyingFunctor

        subgroup = self.subgroup()
        action = ClassifyingFunctor(subgroup.inclusion()).then(
            subgroup.supergroup().natural_module_action_functor()
        )
        stabilizer = StabilizerSubgroups(self.subgroup())(
            self.representative().inclusion(),
            action,
            lambda element: element in parabolic,
        )
        intersection = subgroup.intersection(parabolic)
        return stabilizer.select_group_generators(
            lambda: finite_ordered_set(
                tuple(stabilizer(generator) for generator in intersection.group_generators())
            )
        )

    parabolic_subgroup = stabilizer

    def reduction_lattice(self):
        return self.representative().isotropic_reduction()

    def transporter_witness(self, subobject):
        r"""Return one ``g in Gamma`` carrying ``subobject`` to the representative."""
        return self.subgroup().isotropic_equivalence_witness(
            subobject,
            self.representative(),
        )

    def __contains__(self, subobject) -> bool:
        if subobject not in self.universe():
            return False
        return self.transporter_witness(subobject) is not None

    is_parent_of = __contains__

    def _element_constructor_(self, subobject):
        if subobject not in self:
            raise ValueError(f"{subobject} is not in {self}")
        return subobject

    def _repr_(self) -> str:
        return f"Rank-{self.module_rank()} cusp of {self.subgroup()} in {self.lattice()}"


def _cusp(representative):
    return _object_of(
        Sets(),
        _engine=(Sets(), _CuspEngine, None),
        representative=representative,
    )


def _arithmetic_cusp(subgroup, representative):
    return _object_of(
        Sets(),
        _engine=(Sets(), _ArithmeticCuspEngine, None),
        subgroup=subgroup,
        representative=representative,
    )


class CuspIncidence(SageObject):
    r"""One rank-``(1,2)`` isotropic flag orbit in the quotient Tits building.

    The edge is not reduced to two vertex labels: it retains an actual flag
    ``I_1 < I_2`` in the lattice, the line and plane cusp orbits containing
    its two terms, transporters from those terms to the chosen cusp
    representatives, and generators of the stabilizer of the whole flag.
    Distinct flag orbits with the same pair of cusp vertices therefore remain
    distinct incidence records.
    """

    def __init__(
        self,
        flag,
        line_cusp,
        plane_cusp,
        line_transporter,
        plane_transporter,
        stabilizer_generators,
    ) -> None:
        terms = tuple(flag.terms())
        if len(terms) != 2:
            raise ValueError(f"the isotropic flag {flag} cannot be a cusp incidence: it must have exactly two terms, a line and a plane, but it has {len(terms)}")
        if int(terms[0].module_rank()) != 1 or int(terms[1].module_rank()) != 2:
            raise ValueError(
                f"the isotropic flag {flag} cannot be a cusp incidence: its terms must have ranks one and two, but they have ranks {terms[0].module_rank()} and {terms[1].module_rank()}"
            )
        terms[0].inclusion().factor_through(terms[1].inclusion())
        self._flag = flag
        self._line_cusp = line_cusp
        self._plane_cusp = plane_cusp
        self._line_transporter = line_transporter
        self._plane_transporter = plane_transporter
        self._stabilizer_generators = stabilizer_generators

    def lattice(self):
        return self._flag.lattice()

    def flag(self):
        return self._flag

    def line(self):
        return self.flag().terms()[0]

    def plane(self):
        return self.flag().terms()[1]

    def line_cusp(self):
        return self._line_cusp

    def plane_cusp(self):
        return self._plane_cusp

    def line_transporter(self):
        return self._line_transporter

    def plane_transporter(self):
        return self._plane_transporter

    def stabilizer_generators(self):
        return self._stabilizer_generators

    def __repr__(self) -> str:
        return f"Tits-building incidence {self.line_cusp()} < {self.plane_cusp()}"


class ArithmeticCuspIncidence(SageObject):
    r"""One rank-``(1,2)`` flag orbit in an arithmetic-subgroup quotient building."""

    def __init__(
        self,
        subgroup,
        flag,
        line_cusp,
        plane_cusp,
        line_transporter,
        plane_transporter,
    ) -> None:
        terms = tuple(flag.terms())
        if len(terms) != 2:
            raise ValueError(f"the isotropic flag {flag} cannot be a cusp incidence of {subgroup}: it must have exactly two terms, a line and a plane, but it has {len(terms)}")
        line, plane = terms
        if int(line.module_rank()) != 1 or int(plane.module_rank()) != 2:
            raise ValueError(
                f"the isotropic flag {flag} cannot be a cusp incidence of {subgroup}: its terms must have ranks one and two, but they have ranks {line.module_rank()} and {plane.module_rank()}"
            )
        line.inclusion().factor_through(plane.inclusion())
        if line_cusp.subgroup() is not subgroup or plane_cusp.subgroup() is not subgroup:
            raise ValueError(f"the cusps {line_cusp} and {plane_cusp} cannot both be vertices of a cusp incidence of {subgroup}: each must be a cusp of {subgroup}")
        if line_transporter not in subgroup or plane_transporter not in subgroup:
            raise ValueError(
                f"the isometries {line_transporter} and {plane_transporter} cannot carry the flag {flag} to cusps of {subgroup}: both must be elements of {subgroup}"
            )
        if not _same_subobject(
            line_transporter.transport_isotropic_object(line),
            line_cusp.representative(),
        ):
            raise ValueError(
                f"the isometry {line_transporter} does not carry the line {line} of the flag {flag} to the representative {line_cusp.representative()} of the cusp {line_cusp}"
            )
        if not _same_subobject(
            plane_transporter.transport_isotropic_object(plane),
            plane_cusp.representative(),
        ):
            raise ValueError(
                f"the isometry {plane_transporter} does not carry the plane {plane} of the flag {flag} to the representative {plane_cusp.representative()} of the cusp {plane_cusp}"
            )
        self._subgroup = subgroup
        self._flag = flag
        self._line_cusp = line_cusp
        self._plane_cusp = plane_cusp
        self._line_transporter = line_transporter
        self._plane_transporter = plane_transporter

    def subgroup(self):
        return self._subgroup

    def lattice(self):
        return self.subgroup().supergroup().domain()

    def flag(self):
        return self._flag

    def line(self):
        return self.flag().terms()[0]

    def plane(self):
        return self.flag().terms()[1]

    def line_cusp(self):
        return self._line_cusp

    def plane_cusp(self):
        return self._plane_cusp

    def line_transporter(self):
        return self._line_transporter

    def plane_transporter(self):
        return self._plane_transporter

    def stabilizer(self):
        r"""Return the subgroup of ``Gamma`` preserving both terms of the flag."""
        from sage_extensions.categories.group.predicate_subgroups import (
            StabilizerSubgroups,
        )

        line_stabilizer = self.line().parabolic_subgroup()
        plane_stabilizer = self.plane().parabolic_subgroup()
        from sage_extensions.categories.group.classifying_categories import ClassifyingFunctor

        subgroup = self.subgroup()
        action = ClassifyingFunctor(subgroup.inclusion()).then(
            subgroup.supergroup().natural_module_action_functor()
        )
        return StabilizerSubgroups(self.subgroup())(
            self.flag(),
            action,
            lambda element: element in line_stabilizer and element in plane_stabilizer,
        )

    def __repr__(self) -> str:
        return f"Arithmetic Tits-building incidence {self.line_cusp()} < {self.plane_cusp()}"


def _terms(obj, flag):
    match flag:
        case True:
            return tuple(obj.terms())
        case False:
            return (obj,)


def _factors_through(inclusion, target_inclusion) -> bool:
    r"""Whether the image of ``inclusion`` lies in the image of ``target_inclusion``."""
    source = inclusion.domain()
    return all(target_inclusion.is_in_image(inclusion(source.module_generator(label))) for label in source.module_generating_set())


def _same_subobject(left, right) -> bool:
    return (
        left.inclusion().codomain() is right.inclusion().codomain()
        and _factors_through(left.inclusion(), right.inclusion())
        and _factors_through(right.inclusion(), left.inclusion())
    )


def _zero_isotropic_shape(lattice, rank):
    r"""The rank-``rank`` zero-form lattice used as an isotropic marking shape."""
    from sage_extensions.categories.lattices import Lattices

    rank = int(rank)
    zero = lattice.base_ring().zero()
    return Lattices(lattice.base_ring())(
        tuple(tuple(zero for _column in range(rank)) for _row in range(rank))
    )


def _marked_isotropic_category(lattice, length):
    from sage_extensions.categories.abstract_categories.cat import Cat
    from sage_extensions.categories.abstract_categories.products import (
        FiniteOrdinalCategory,
    )
    from sage_extensions.categories.lattices import Lattices

    return Cat().Mor(
        FiniteOrdinalCategory(length + 1),
        Lattices(lattice.base_ring()),
    )


def _marked_isotropic_object(obj, *, flag):
    r"""Read a represented isotropic subobject/flag as the corresponding marked lattice."""
    match flag:
        case False:
            return _marked_isotropic_category(obj.ambient_lattice(), 1).object(
                obj.inclusion()
            )
        case True:
            from sage_extensions.categories.abstract_categories.products import FiniteSequenceDiagram
            from sage_extensions.categories.lattices import Lattices

            objects, arrows = _flag_diagram_data(obj)
            diagram = FiniteSequenceDiagram(objects, arrows, Lattices(obj.lattice().base_ring()))
            return _marked_isotropic_category(obj.lattice(), len(arrows))(diagram)


def _flag_diagram_data(flag):
    r"""The objects and adjacent arrows of the chain ``I_{d_1} -> ... -> I_{d_t} -> L`` of a flag."""
    terms = tuple(flag.terms())
    arrows = tuple(
        left.inclusion().factor_through(right.inclusion())
        for left, right in pairwise(terms)
    ) + (terms[-1].inclusion(),)
    return (arrows[0].domain(), *(arrow.codomain() for arrow in arrows)), arrows


def _isotropic_object_from_marked(marked, *, flag):
    r"""Return the isotropic object represented by a marked lattice."""
    match flag:
        case False:
            arrow = marked.arrow()
            lattice = arrow.codomain()
            vectors = tuple(
                arrow(arrow.domain().module_generator(label))
                for label in arrow.domain().module_generating_set()
            )
            return lattice.primitive_isotropic_subobject(*vectors)
        case True:
            diagram = marked.functor()
            arrows = tuple(
                diagram(diagram.domain().Mor(left, right).unique())
                for left, right in pairwise(diagram.domain().objects())
            )
            basis = tuple(arrows[0].domain().module_generators())
            dimensions = tuple(int(arrow.domain().module_rank()) for arrow in arrows)
            # Lift a basis of each primitive quotient to extend the adapted
            # integral basis. CombinedAlgorithms.h:659-717 retains precisely
            # these cumulative spaces and their block source actions.
            for arrow in arrows[:-1]:
                quotient = arrow.cokernel()
                if quotient.is_torsion_free() is not True:
                    raise ArithmeticError(
                        f"the marked flag {marked} needs primitive successive inclusions"
                    )
                trivialization = quotient.finite_free_trivialization()
                normalized = trivialization.codomain()
                complements = tuple(
                    arrow.cokernel_projection().preimage(trivialization.inverse()(point))
                    for point in normalized.module_generators()
                )
                basis = (*(arrow(point) for point in basis), *complements)
            return IsotropicFlag(
                arrows[-1].codomain(), tuple(arrows[-1](point) for point in basis),
                flag_type=FlagType(dimensions),
            )


def _hyperbolic_completion(lattice, line):
    r"""Return ``(v, <v, f>)`` when ``v`` splits off a hyperbolic plane at index one.

    ``v`` is the selected generator of the isotropic line ``line`` and ``f`` is an
    isotropic vector of ``lattice`` with ``b(v, f) != 0`` for which
    ``L = <v, f> + <v, f>^\perp`` is an orthogonal direct sum of index one, decided
    by ``det(L) = det(<v, f>) det(<v, f>^\perp)``.  ``None`` when no such ``f`` is
    exhibited among the chosen generators of ``L``.

    The split is what makes the plane branch complete.  With it, every ``x`` in
    ``v^\perp`` has ``x = a v + b f + k`` and ``b(x, v) = b m``, so ``b = 0`` and
    ``v^\perp = <v> + <v, f>^\perp``: the reduction ``K_v = v^\perp/<v>`` *is* the
    complement ``<v, f>^\perp``, and every isometry of that complement extends to
    ``L`` by the identity on ``<v, f>``, hence lies in ``Stab_{O(L)}(v)``.  The
    stabilizer therefore acts on ``K_v`` through all of ``O(K_v)``, and one
    representative per ``O(K_v)``-orbit of isotropic vectors is one representative
    per ``Stab_{O(L)}(v)``-orbit of planes through that line.  Without it the
    argument fails at that step and the caller keeps the marking-class route.
    """
    ring = lattice.base_ring()
    zero = ring.zero()
    selected = line.module_generating_set()[0]
    v = line.inclusion()(line.module_generator(selected))
    for label in lattice.module_generating_set():
        candidate = lattice.module_generator(label)
        if candidate.q() != zero or lattice.b(v, candidate) == zero:
            continue
        # <v, f> is a hyperbolic plane only when it is a direct summand.  Its Gram
        # determinant is -b(v, f)^2 and the index of <v, f> + <v, f>^\perp in L has
        # square equal to the determinant quotient, so index one is exactly the
        # equality below.  The span is built with the restricted form and not as a
        # primitive isotropic subobject: b(v, f) != 0 makes <v, f> not isotropic.
        span = lattice.subobject_on((v, candidate))
        if lattice.determinant() != span.determinant() * span.inclusion().orthogonal_complement().determinant():
            continue
        return v, span
    return None


def _planes_through_line(orthogonal_group, line):
    r"""One primitive isotropic plane per ``Stab_{O(L)}(v)``-orbit through ``line``.

    Scattone, *On the compactification of moduli spaces for algebraic K3
    surfaces*, Mem. AMS 374 (1987), Proposition 5.4.7 with Corollary 5.4.8(2),
    p. 78, as ``tests/fixtures/DATA_SOURCES.md`` records it: a primitive isotropic
    plane ``E`` containing a primitive isotropic vector ``v`` corresponds to the
    primitive isotropic line ``E/<v>`` of the reduction ``K_v = v^\perp/<v>``.
    The vectors of ``K_v`` are the selected quotient's, and the frame of the
    reduction lifts them into ``v^\perp <= L``, so each returned plane is
    ``<v, lift>`` in the lattice itself.

    ``isotropic_vector_classes(K_v)`` is the port's classification of the
    primitive isotropic vectors of ``K_v`` modulo ``O(K_v)``, which is the class
    set wanted here exactly when :func:`_hyperbolic_completion` has certified the
    split; the caller checks that first.
    """
    from sage_indefinite_port.indefinite.marked_lattices import INDUCTION

    lattice = orthogonal_group.domain()
    reduction = line.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    labels = tuple(quotient.module_generating_set())
    perpendicular = reduction.orthogonal_complement().inclusion()
    frame = reduction.coordinate_frame()
    lifts = {label: perpendicular(frame(label)) for label in labels}

    def lift(element):
        coordinates = element.to_vector()
        return sum(
            (
                lattice.scalar_multiple(coordinates(label), lifts[label])
                for label in labels
                if coordinates(label)
            ),
            lattice.zero(),
        )

    v = line.inclusion()(line.module_generator(line.module_generating_set()[0]))
    return tuple(
        lattice.primitive_isotropic_subobject(v, lift(isotropic))
        for isotropic in INDUCTION.isotropic_vector_classes(quotient)
    )


def _isotropic_plane_orbit_representatives(orthogonal_group):
    r"""One representative per ``O(L)``-orbit of primitive isotropic planes, or ``None``.

    The pairs ``(v, line of K_v)`` do not index the plane classes: a plane
    contains as many primitive isotropic vector orbits as the line orbits of
    ``O(L)`` meet it, and the same plane is reached from each of them.
    The candidates are therefore collected over the line representatives ``v`` and
    then *identified*: two candidates are the same class exactly when an isometry
    of ``L`` carries one plane onto the other, which is the exact plane
    equivalence and not a count or an invariant comparison.  Scattone's Corollary
    5.4.8(2) is the statement that this identification collapses the candidates
    to the plane classes.
    """
    lattice = orthogonal_group.domain()
    candidates = []
    for line in _isotropic_orbit_representatives(orthogonal_group, 1):
        if _hyperbolic_completion(lattice, line) is None:
            return None
        candidates.extend(_planes_through_line(orthogonal_group, line))
    kept = []
    for plane in candidates:
        if any(
            _isotropic_equivalence_witness(orthogonal_group, other, plane) is not None
            for other in kept
        ):
            continue
        kept.append(plane)
    return finite_ordered_set(tuple(kept))


def _hilbert_model_gram(field_discriminant):
    r"""Return the Gram matrix of ``U + (O_F, Tr)`` for a real quadratic discriminant.

    ``field_discriminant`` is the discriminant of ``F = QQ(sqrt(d))``, so
    ``omega = (1 + sqrt(d))/2`` for odd ``d`` and ``omega = sqrt(d)`` for
    ``d = 4 * field_discriminant``, and the basis is ``(E_11, E_22, 1, omega)``.
    The entries are ``Tr(x conj(y))`` of the ring of integers: ``Tr(1) = 2``,
    ``Tr(omega) = 1`` and ``Tr(omega conj(omega)) = 2 N(omega) = (1 - d)/2``
    for odd ``d``, and ``Tr(omega) = 0`` with
    ``Tr(omega conj(omega)) = -d/2`` for even ``d``.

    This is the lattice ``L = ZZ + ZZ + O_F`` of Bruinier, *Hilbert modular forms
    and their applications*, in *The 1-2-3 of Modular Forms* (Universitext,
    Springer, 2008), pp. 105-179, §2.7, printed pp. 143-144, for the form printed there,
    ``Q(a, b, nu) = nu conj(nu) - a b``.  This library's quadratic form is
    ``q(x) = b(x, x)``, so the matrix below is twice the source's, i.e.
    ``q = 2Q = -2 det`` on the Hermitian matrices ``X = [[a, beta],
    [conj(beta), d]]``: the even normalization.  Isotropy and the orthogonal
    group are the same for ``q`` and for ``2Q``.
    """
    if field_discriminant % 4 == 1:
        trace_of_omega, trace_of_norm = 1, (1 - field_discriminant) // 2
    else:
        trace_of_omega, trace_of_norm = 0, -field_discriminant // 2
    return matrix(
        SageZZ,
        [
            [0, -1, 0, 0],
            [-1, 0, 0, 0],
            [0, 0, 2, trace_of_omega],
            [0, 0, trace_of_omega, trace_of_norm],
        ],
    )


def _witt_one_hilbert_line_representatives(lattice):
    r"""One representative per ``O(L)``-orbit of primitive isotropic lines at Witt index one.

    A rank-four lattice of Witt index one has no second hyperbolic plane, so the
    Eichler envelope that classifies isotropic orbits on ``U + U + K`` does not
    apply to it, and the classification is the cusp count of the Hilbert modular
    group instead:

    * Bruinier, *Hilbert modular forms and their applications*, in *The 1-2-3 of
      Modular Forms* (Universitext, Springer, 2008), pp. 105-179, §2.7, printed pp. 143-144:
      the Hilbert lattice is ``L = ZZ + ZZ + O_F`` inside ``V = QQ + QQ + F`` with
      ``Q(a, b, nu) = nu conj(nu) - a b``, and ``Gamma_F = SL_2(O_F) =
      Spin_L``; the same section identifies ``H^2`` with ``K^+`` and states that
      the identification commutes with the action of ``SL_2(F)``.  Since
      ``Spin_L <= O(L)``, the group ``O(L)`` has no more orbits than
      ``Gamma_F``.
    * Bruinier, ibid., Corollary 1.4 (§1.1, printed pp. 106-109): the number of
      cusps of ``Gamma_F`` equals the class number ``h(F)``.  A cusp is a
      ``Gamma_F``-orbit of ``P^1(F)`` (§1.1, printed p. 106), the rational
      boundary points of ``K^+`` are ``P^1(F)`` (ibid. (1.9)), and the projective
      model matches those with the rational isotropic lines (ibid. Lemma 2.20
      and §2.7).  A rational isotropic line meets the lattice ``L`` in a
      rank-one primitive sublattice, and every primitive isotropic vector spans
      such a line, so the ``Gamma_F``-orbits of primitive isotropic lines of
      ``L`` number ``h(F)``.

    The printed pages above are the publisher's table-of-contents pages for the
    two sections: §1.1 begins on p. 106 and §1.2 on p. 109, and Corollary 1.4 is
    the last numbered statement of §1.1, so it stands on one of pp. 106-109;
    §2.7 begins on p. 143 and carries the lattice and ``Gamma_F = Spin_L`` over
    to p. 144.  The same count is stated with an exact printed page, without a
    statement number, in Hirzebruch-Van de Ven, *Hilbert modular surfaces and the
    classification of algebraic surfaces*, Invent. Math. 23 (1974), 1-29,
    pp. 12-13: the cusps "are in one-to-one correspondence with the ideal
    classes", and the compactified space has ``h(p)`` of them, in the case
    ``K = QQ(sqrt p)`` for a prime ``p = 1 mod 4`` that covers the ``F = 5``
    lattice.

    Hence ``h(F) = 1`` forces exactly one ``O(L)``-orbit of primitive isotropic
    lines, and *any* primitive isotropic vector of ``L`` represents it: the
    representative below is the one the exact isotropic-vector construction
    finds, not a chosen coordinate vector, and it is checked to be isotropic,
    primitive, and a primitive isotropic line of this lattice.

    The lattice is accepted only when it is the model: even, rank four,
    determinant the field discriminant ``F`` of a real quadratic field, and
    isometric to :func:`_hilbert_model_gram` of that discriminant under the
    library's own exact isometry decision (which rests on one genus with one
    spinor genus, Conway-Sloane, *Low-dimensional lattices IV*, Ch. 15,
    Theorem 14).  ``None`` when that is not established, which leaves the
    caller's marking-class route in charge.  A class number above one refuses by
    name: the count there is only bounded by ``h(F)``, and the exact quotient of
    the class set is not owned yet.
    """
    ring = lattice.base_ring()
    frame = tuple(lattice.module_generators())
    gram = matrix(SageZZ, [[int(lattice.b(left, right)) for right in frame] for left in frame])
    if gram != gram.transpose():
        return None
    determinant = int(gram.det())
    field_discriminant = abs(determinant)
    radicand = int(SageZZ(field_discriminant).squarefree_part())
    if radicand == 1 or determinant != field_discriminant:
        return None
    from sage_extensions.categories.rings.number_fields import QuadraticField

    field = QuadraticField(radicand, "s")
    if int(field.discriminant()) != field_discriminant:
        return None
    from sage_extensions.categories.lattices import Lattices

    model = Lattices(ring)([list(row) for row in _hilbert_model_gram(field_discriminant).rows()])
    if lattice.is_isometric(model) is not True:
        return None
    class_number = int(field.class_number())
    if class_number != 1:
        raise NotImplementedError(
            f"the O(L)-orbits of primitive isotropic lines of {lattice} are not enumerated: it is "
            f"the Hilbert model U + (O_F, Tr) of discriminant {field_discriminant}, where "
            f"F = QQ(sqrt({radicand})) has class number {class_number}, so the cusp count only bounds "
            "the number of orbits by h(F) and the class set of the model is not owned yet"
        )
    from sage.arith.functions import lcm
    from sage.arith.misc import gcd
    from sage.rings.rational_field import QQ
    from sage_indefinite_port.indefinite.exact_isotropic import find_isotropic_exact

    rational = find_isotropic_exact(matrix(QQ, gram))
    if rational is None:
        raise ArithmeticError(
            f"the exact isotropic-vector construction found no isotropic vector for {lattice}, "
            "whose Witt index is one"
        )
    common = int(lcm(tuple(QQ(entry).denominator() for entry in rational)))
    integral = tuple(int(QQ(entry) * common) for entry in rational)
    content = int(gcd(integral))
    zero = ring.zero()
    representative = lattice.zero()
    for generator, coordinate in zip(frame, integral, strict=True):
        if coordinate:
            representative = representative + lattice.scalar_multiple(ring(coordinate // content), generator)
    if representative.q() != zero:
        raise ArithmeticError(f"the isotropic-vector construction returned {representative} of square {representative.q()} in {lattice}")
    if representative.is_primitive() is not True:
        raise ArithmeticError(f"the isotropic-vector construction returned the imprimitive {representative} in {lattice}")
    line = lattice.primitive_isotropic_subobject(representative)
    if line.is_primitive() is not True:
        raise ArithmeticError(f"the line of {representative} is not primitive in {lattice}")
    return finite_ordered_set((line,))


def _isotropic_orbit_representatives(orthogonal_group, rank, *, flag=False):
    r"""Return full-``O(L)`` orbit representatives of primitive isotropic subobjects/flags."""
    lattice = orthogonal_group.domain()
    if flag:
        flag_type = rank if isinstance(rank, FlagType) else FlagType.complete(index(rank))
        dimensions = flag_type.dimensions
    else:
        rank = index(rank)
        if rank == 0:
            return finite_ordered_set((lattice.primitive_isotropic_subobject(),))
        if rank == 1 and int(lattice.module_rank()) == 4 and int(lattice.witt_index()) == 1:
            # Witt index one has no second hyperbolic plane, so the Eichler
            # envelope below does not reach it; the Hilbert model answers by cusp
            # count instead, and only where that count is proved to be one.
            representatives = _witt_one_hilbert_line_representatives(lattice)
            if representatives is not None:
                return representatives
        dimensions = (rank,)
    if dimensions[-1] < 0:
        raise ValueError(f"the isotropic sublattice rank must be nonnegative, got {rank} in {lattice}")
    if not flag and dimensions == (2,):
        # Scattone 5.4.7: planes are read from the lines of v^perp/Zv over the line
        # classes, not enumerated as plane classes directly.  The fast branch is
        # taken only when it is certified complete; a lattice whose line
        # representatives do not split off a hyperbolic plane keeps the port's
        # marking-class classification, which never returns a partial family.
        planes = _isotropic_plane_orbit_representatives(orthogonal_group)
        if planes is not None:
            return planes
    from sage_indefinite_port.indefinite.marked_lattices import (
        primitive_marking_classes,
    )

    category = _marked_isotropic_category(lattice, len(dimensions))
    if flag:
        from sage_extensions.categories.abstract_categories.products import FiniteSequenceDiagram

        # CombinedAlgorithms.h:590-717 retains arbitrary block dimensions;
        # seq_dims_flag(rank) is its complete-flag specialization.
        shapes = tuple(_zero_isotropic_shape(lattice, size) for size in dimensions)
        arrows = tuple(
            left.Mor(right)(dict(zip(left.module_generating_set(), right.module_generators())))
            for left, right in pairwise(shapes)
        )
        shape = (
            shapes[0] if len(dimensions) == 1
            else _marked_isotropic_category(lattice, len(dimensions) - 1)(
                FiniteSequenceDiagram(shapes, arrows, category.codomain_category())
            )
        )
    else:
        shape = _zero_isotropic_shape(lattice, int(rank))
    classes = primitive_marking_classes(category, shape, lattice)
    return finite_ordered_set(tuple(
        _isotropic_object_from_marked(marked, flag=flag)
        for marked in classes
    ))


def _isotropic_equivalence_witness(orthogonal_group, left, right, *, flag=False):
    r"""Return an isometry carrying one primitive isotropic subobject/flag to another."""
    if flag:
        left_terms = _terms(left, flag)
        right_terms = _terms(right, flag)
        if len(left_terms) != len(right_terms):
            return None
        if all(_same_subobject(source, target) for source, target in zip(left_terms, right_terms, strict=True)):
            return orthogonal_group.one()
    elif _same_subobject(left, right):
        return orthogonal_group.one()
    from sage_indefinite_port.indefinite.marked_lattices import (
        isometry,
    )

    category = _marked_isotropic_category(orthogonal_group.domain(), len(tuple(left.terms())) if flag else 1)
    return isometry(
        category,
        _marked_isotropic_object(left, flag=flag),
        _marked_isotropic_object(right, flag=flag),
    )


def _isotropic_stabilizer_generators(orthogonal_group, obj, *, flag=False):
    r"""Return generators of the full-orthogonal-group stabilizer of an isotropic subobject/flag."""
    from sage_indefinite_port.indefinite.marked_lattices import (
        automorphism_group_generators,
    )

    category = _marked_isotropic_category(orthogonal_group.domain(), len(tuple(obj.terms())) if flag else 1)
    return automorphism_group_generators(
        category,
        _marked_isotropic_object(obj, flag=flag),
    )


def _divided_discriminant_classes(lattice, plane):
    r"""Return the divided discriminant classes ``[u/div(u)]`` of a primitive isotropic plane.

    For a primitive ``u`` of ``L`` with divisibility ``d = div(u)`` the vector
    ``u/d`` lies in ``L^\#`` and its class ``[u/d]`` in ``A_L = L^\#/L`` depends
    only on the line ``\mathbb{Z} u``: ``div(mu) = m div(u)``, so
    ``mu/div(mu) = u/div(u)``.  The class set of a primitive isotropic
    subobject is therefore the set of these classes over its primitive
    directions, which is finite because ``2 u/div(u) \in L`` on a lattice whose
    discriminant group has exponent two: for such an ``L`` a class in ``A_L`` is
    fixed by the coset of ``u`` in ``P/2P``, so the three nonzero cosets carry
    every class and the third term below contributes nothing new.

    ``P1 = \mathbb{Z} e_1 + \mathbb{Z} e_3`` and
    ``P2 = \mathbb{Z}(2 e_1 + 2 e_2 + w) + \mathbb{Z} e_3`` of the Enriques
    period lattice (D. Dutour Sikirić and K. Hulek, *Moduli of polarised
    Enriques surfaces -- computational aspects*, J. London Math. Soc. 110
    (2024), arXiv:2302.01679, §3.6 (the Tits building), p. 22, and H. Sterk,
    *Compactifications of the period space of Enriques surfaces, Part I*,
    Math. Z. 207 (1991), Propositions 4.5 (p. 28) and 4.6 (p. 29)) have
    different class sets here, which is the whole reason the two planes are in
    different ``O(L)``-orbits.
    """
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    labels = tuple(domain.module_generating_set())
    basis = tuple(inclusion(domain.module_generator(label)) for label in labels)
    if len(basis) != 2:
        raise ValueError(
            f"a primitive isotropic plane needs two generators, but {plane} has {len(basis)}; "
            f"the divided class set is stated only for rank two"
        )
    discriminant = lattice.discriminant_group()
    classes = [discriminant.zero()]
    for vector in (basis[0], basis[1], basis[0] + basis[1]):
        classes.append(lattice.divided_discriminant_class(vector))
    return tuple(classes)


class IsotropicPlaneOrbit:
    r"""One orbit of primitive isotropic planes of a lattice under an arithmetic subgroup.

    The orbit is recorded by the point of the finite divided-class set that
    indexes it, and realized as an actual plane on demand.  See
    :meth:`sage_extensions.categories.group.predicate_subgroups.PredicateSubgroups.ParentMethods.isotropic_plane_orbits`
    for the reduction that makes one point stand for one orbit.
    """

    def __init__(self, decomposition, start, point) -> None:
        self._decomposition = decomposition
        self._start = start
        self._point = point

    def lattice(self):
        r"""Return the lattice whose planes are being classified."""
        return self._decomposition.lattice()

    def group(self):
        r"""Return the subgroup acting."""
        return self._decomposition.group()

    def divided_classes(self):
        r"""Return the divided discriminant classes of the realized representative."""
        plane = self.representative()
        return _divided_discriminant_classes(self.lattice(), plane)

    def representative(self):
        r"""Return a primitive isotropic plane in this orbit.

        The plane is the image of the ``O(L)``-orbit representative under an
        isometry whose discriminant image carries the representative's class
        set to this orbit's point.  The isometry is read as a word in the
        ambient generators (the section of the finite character image), and
        the transported plane is checked against the point it is supposed to
        reach before it is returned.
        """
        return self._decomposition.plane_of(self._start, self._point)

    def __repr__(self):
        return f"An orbit of primitive isotropic planes of {self.lattice()} under {self.group()}"


def _enriques_period_lattice_isometry(lattice):
    r"""Return an isometry from ``lattice`` onto the Enriques period lattice, or ``None``.

    The published plane-stabilizer indices used below are stated for the single
    lattice ``N = U \oplus U(2) \oplus E_8(-2)`` (Dutour Sikirić--Hulek,
    *Moduli of polarised Enriques surfaces -- computational aspects*,
    J. London Math. Soc. 110 (2024), arXiv:2302.01679, §3.6 (the Tits
    building), p. 22), so that lattice is the hypothesis to check.  It is
    checked by *exhibiting* an isometry: equal rank, signature, determinant and
    discriminant group do not determine an indefinite lattice's isometry class,
    and the predicate that compares those is not a class test.  The cheap
    invariants above it only avoid starting an isometry search that cannot
    succeed.
    """
    from sage_extensions.catalogue import NamedLattices

    patent = NamedLattices.TEn
    if lattice is patent:
        return lattice.Aut().one()
    if (
        int(lattice.module_rank()) != int(patent.module_rank())
        or tuple(lattice.signature_pair()) != tuple(patent.signature_pair())
        or lattice.determinant() != patent.determinant()
        or lattice.discriminant_group().cardinality()
        != patent.discriminant_group().cardinality()
    ):
        return None
    try:
        return lattice.Isom(patent).an_element()
    except (ValueError, ArithmeticError):
        return None


_ENRIQUES_PERIOD_LATTICE_PLANE_INDICES = (527, 23715)


class _DividedClassPlaneOrbitDecomposition:
    r"""The finite divided-class decomposition behind :class:`IsotropicPlaneOrbit`.

    The reduction is Dutour Sikirić--Hulek, arXiv:2302.01679, Lemma 3.6
    (printed p. 22, in §3.6 "The Tits building"): for ``G = O(L)``, its
    discriminant kernel ``U = \widetilde{O}(L)`` contained in ``K = \Gamma`` and
    the stabilizer ``H = G_x`` of the plane ``x``, the quotient map
    ``G -> G/U`` carries the double cosets ``K \backslash G / H`` bijectively
    onto those of ``K/U \backslash G/U / \overline{H}``, and the double cosets
    ``\Gamma \backslash O(L) / G_x`` are the ``\Gamma``-orbits on the
    ``O(L)``-orbit ``xG`` of the plane.  The ambient quotient is the
    discriminant image ``Q = \rho(O(L)) \subset O(A_L)``, of order
    ``46998591897600`` on ``T_{\mathrm{En}}``, and ``\Gamma`` is a character
    kernel, so the count is a finite permutation-group computation -- but only
    once ``\overline{H} = \rho(G_x)`` is known, which is what
    :meth:`_establish_plane_stabilizer_images` decides.
    """

    def __init__(self, subgroup, representatives, stabilizer_generators=None) -> None:
        from sage.libs.gap.libgap import libgap
        from sage_extensions.categories.group.groups import _element_to_engine

        self._group = subgroup
        lattice = representatives[0].inclusion().codomain()
        if any(plane.inclusion().codomain() is not lattice for plane in representatives):
            raise ValueError(
                f"the divided-class plane orbits of {subgroup} need every ambient representative to "
                f"be a plane of one lattice: the first is a plane of {lattice} and another is not"
            )
        self._lattice = lattice
        self._discriminant = lattice.discriminant_group()
        quotient = subgroup.finite_character_quotient()
        # The engine is the character quotient's own discriminant image, so the
        # classes cross into it through ITS orthogonal group; the classes
        # themselves are read on the representatives' lattice above.
        orthogonal = quotient.lattice.discriminant_group().O()
        engine, image, section, ambient = quotient._im_rho_engine_and_section()
        self._engine = engine
        self._image = libgap.Subgroup(engine, libgap.SmallGeneratingSet(image))
        self._section = section
        self._ambient = ambient
        self._orthogonal = orthogonal
        self._setwise_action = libgap.function_factory(
            "function(x, g) return Set(List(x, y -> ImageElm(g, y))); end"
        )
        self._starts = []
        for plane in representatives:
            classes = _divided_discriminant_classes(lattice, plane)
            self._starts.append((plane, classes, self._point_of_classes(classes)))
        subgroup_generators = tuple(subgroup.discriminant_image().group_generators())
        images = [_element_to_engine(orthogonal, generator) for generator in subgroup_generators]
        self._subgroup_image = libgap.Subgroup(engine, images)
        self._subgroup_image_generators = libgap.SmallGeneratingSet(self._subgroup_image)
        self._supplied_stabilizers = dict(stabilizer_generators or {})

    def lattice(self):
        return self._lattice

    def group(self):
        return self._group

    def _establish_plane_stabilizer_images(self, sizes) -> None:
        r"""Require ``\rho(G_x) = \mathrm{Stab}_Q(J_x)`` for each representative ``x``, or refuse.

        ``J_x`` is the divided class set of ``x`` and ``G_x = \mathrm{Stab}_{O(L)}(x)``.
        The inclusion ``\rho(G_x) \subseteq \mathrm{Stab}_Q(J_x)`` holds for
        every lattice: ``J_x`` is built from ``x`` by the lattice operations, so
        an isometry carrying ``x`` to ``x`` carries ``J_x`` to ``J_x``, and
        ``\widetilde{O}(L) = \ker \rho`` acts trivially.  Hence
        ``|Q . J_x| = [Q : \mathrm{Stab}_Q(J_x)] \le [Q : \rho(G_x)]``, and the
        count of ``\Gamma``-orbits on the finite set ``Q . J_x`` is the count of
        ``\Gamma``-orbits of planes exactly when the two indices agree --
        otherwise it is too small (Dutour Sikirić--Hulek, Lemma 3.6, p. 22, is
        the bijection that makes the two counts the same object).

        Three ways to close the inequality are accepted, and nothing else is:

        * ``\rho(G_x)`` from supplied stabilizer generators (:meth:`_establish_by_stabilizer_generators`);
        * a trivial discriminant image ``Q = 1``, where the equality is vacuous:
          ``\rho(G_x) = 1 = \mathrm{Stab}_Q(J_x)`` for every plane, so its class set
          is a single point (:meth:`_establish_when_the_image_is_trivial`);
        * the published indices of the two ``O(N)``-orbits of ``N = U \oplus U(2) \oplus E_8(-2)``,
          ``527 = 17 \cdot 31`` and ``23715 = 3^2 \cdot 5 \cdot 17 \cdot 31``
          (Dutour Sikirić--Hulek, §3.6, p. 22), on a lattice exhibited to be
          ``N`` (:meth:`_establish_by_published_indices`).

        A representative for which none applies raises, naming it and the
        missing fact, rather than returning a count.
        """
        if self._establish_when_the_image_is_trivial(sizes):
            return
        pending = []
        for position, size in enumerate(sizes):
            supplied = self._supplied_stabilizers.get(position)
            if supplied is None:
                pending.append(position)
                continue
            self._establish_by_stabilizer_generators(position, tuple(supplied), size)
        if pending:
            self._establish_by_published_indices(pending, sizes)

    def _establish_when_the_image_is_trivial(self, sizes) -> bool:
        r"""Decide the vacuous case ``\rho(O(L)) = 1``, and return whether it applied.

        If the discriminant representation has trivial image then
        ``\rho(G_x) = 1 = \mathrm{Stab}_Q(J_x)`` for every plane ``x``, as
        ``Q = \rho(O(L))`` is a single element, so the equality the count needs
        holds without any information about the stabilizer.  The class set of
        each representative is then a single point; anything else would
        contradict the trivial image and is reported rather than assumed away.
        """
        if int(self._image.Size()) != 1:
            return False
        unexpected = [size for size in sizes if size != 1]
        if unexpected:
            raise ArithmeticError(
                f"the discriminant image of O({self._lattice}) is trivial, so the divided classes of a "
                f"plane form a single point, but the class sets of the representatives have "
                f"{unexpected} points: the class set and the discriminant action disagree, and no orbit "
                f"count is returned from them"
            )
        return True

    def _establish_by_stabilizer_generators(self, position, stabilizers, size) -> None:
        r"""Establish the equality from generators of ``G_x``, or refuse.

        ``[\rho(O(L)) : \langle\rho(h)\rangle] = [\rho(O(L)) : \rho(G_x)]``
        when the generated subgroup is the whole image, so the sandwich closes:
        ``|Q . J_x| \le [Q : \rho(G_x)] \le [Q : \langle\rho(h)\rangle]``.
        Every supplied element is checked to stabilize the plane first, so a
        generator of some other subgroup contributes nothing.
        """
        from sage.libs.gap.libgap import libgap
        from sage_extensions.categories.group.groups import _element_to_engine

        plane = self._starts[position][0]
        inclusion = plane.inclusion()
        basis = tuple(inclusion(generator) for generator in inclusion.domain().module_generators())
        if self._lattice is not self._group.finite_character_quotient().lattice:
            raise ValueError(
                f"the stabilizer generators given for {plane} are isometries of {self._lattice}, but the "
                f"discriminant image of {self._group} is computed on "
                f"{self._group.finite_character_quotient().lattice}: the two lattices would have to be the "
                f"same object for the image of a supplied isometry to be read"
            )
        images = []
        for isometry in stabilizers:
            moved = self._lattice.primitive_isotropic_subobject(*[isometry(vector) for vector in basis])
            if not _same_subobject(moved, plane):
                raise ValueError(
                    f"the supplied isometry {isometry} does not stabilize the plane {plane}: it carries the "
                    f"plane to {moved}, so it is not a generator of the stabilizer whose discriminant image "
                    f"the orbit count needs"
                )
            images.append(_element_to_engine(self._orthogonal, self._lattice.discriminant_representation()(isometry)))
        hull = libgap.Subgroup(self._engine, images)
        index = int(self._image.Size()) // int(hull.Size())
        if index != size:
            raise ValueError(
                f"the discriminant image of the stabilizer of {plane} is not established: the supplied "
                f"generators generate a subgroup of index {index} in rho(O({self._lattice})), while the "
                f"orbit of the plane's divided classes has {size} points. The two indices agree only when "
                f"rho(G_x) = Stab(class set of x), which is what the count needs; supply generators of the "
                f"whole stabilizer, or a lattice whose published plane-stabilizer indices apply"
            )

    def _establish_by_published_indices(self, positions, sizes) -> None:
        r"""Establish the equality from the published indices of ``N = U \oplus U(2) \oplus E_8(-2)``, or refuse.

        Dutour Sikirić--Hulek, §3.6, p. 22: the two ``O(N)``-orbits of primitive
        isotropic planes are ``P_1`` and ``P_2``, and the images of their
        stabilizers have index ``527`` and ``23715`` in ``\rho(O(N))``.  So for
        the two orbits the multiset of indices is ``{527, 23715}``; since
        ``|Q . J_x| \le [Q : \rho(G_x)]`` for each orbit and the indices of
        distinct orbits are distinct, a set of class-set orbit sizes equal to
        ``{527, 23715}`` forces equality orbit by orbit.  That argument needs
        both orbits, so one representative alone is refused here.
        """
        plane = self._starts[positions[0]][0]
        others = ", ".join(str(self._starts[position][0]) for position in positions[1:])
        isometry = _enriques_period_lattice_isometry(self._lattice)
        if isometry is None:
            raise ValueError(
                f"the discriminant image of the stabilizer of {plane}"
                + (f" (and of {others})" if others else "")
                + f" in O({self._lattice}) is not established: the orbit of the plane's divided classes has "
                f"{sizes[positions[0]]} points, which bounds [rho(O(L)) : rho(G_x)] from above without "
                f"determining it, so the orbit count would be a lower bound. The published indices are "
                f"stated for N = U + U(2) + E8(-2) and no isometry from {self._lattice} onto it is exhibited. "
                f"Pass stabilizer_generators for the representatives, or a lattice isometric to N with the "
                f"paper's two plane orbits"
            )
        computed = {sizes[position] for position in positions}
        published = set(_ENRIQUES_PERIOD_LATTICE_PLANE_INDICES)
        if computed != published:
            raise ValueError(
                f"the discriminant image of the stabilizer of {plane}"
                + (f" (and of {others})" if others else "")
                + f" is not established: the divided-class orbits of the representatives have "
                f"{sorted(computed)} points, while the two plane orbits of N = U + U(2) + E8(-2) have "
                f"stabilizer-image indices {sorted(published)} (Dutour Sikirić--Hulek, §3.6, p. 22). "
                f"Both of those two orbits are needed for the published indices to bound each "
                f"representative's stabilizer image, so this is a lower bound, not the orbit count. "
                f"Pass stabilizer_generators for the representatives"
            )

    def _point_of_classes(self, classes):
        return _libgap().Set([self._orthogonal._engine_abelian_element(c) for c in classes])

    def _point_of(self, plane):
        return self._point_of_classes(_divided_discriminant_classes(self._lattice, plane))

    def orbits(self):
        r"""Return one :class:`IsotropicPlaneOrbit` per orbit of the subgroup."""
        from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

        action = self._setwise_action
        ambient_orbits = [
            _libgap().AsList(_libgap().Orbit(self._image, point, action))
            for _plane, _classes, point in self._starts
        ]
        self._establish_plane_stabilizer_images([len(orbit) for orbit in ambient_orbits])
        points = []
        owners = []
        for start, orbit in enumerate(ambient_orbits):
            for point in orbit:
                points.append(point)
                owners.append(start)
        markers = [str(point) for point in points]
        position = {marker: index for index, marker in enumerate(markers)}
        graphs = [
            [position[str(action(point, generator))] for point in points]
            for generator in self._subgroup_image_generators
        ]
        seen = [False] * len(points)
        orbits = []
        for start in range(len(points)):
            if seen[start]:
                continue
            seen[start] = True
            stack = [start]
            while stack:
                current = stack.pop()
                for graph in graphs:
                    following = graph[current]
                    if not seen[following]:
                        seen[following] = True
                        stack.append(following)
            orbits.append(IsotropicPlaneOrbit(self, owners[start], points[start]))
        return finite_ordered_set(tuple(orbits))

    def plane_of(self, start, point):
        r"""Return the plane at ``point`` as the image of the ``start`` representative."""
        from sage.libs.gap.libgap import libgap

        plane, _classes, start_point = self._starts[start]
        if str(point) == str(start_point):
            return plane
        element = libgap.RepresentativeAction(self._image, start_point, point, self._setwise_action)
        if element is None:
            raise ArithmeticError(
                f"the divided class point {point} is not reached from the {start}-th representative "
                f"of {self._lattice} by the discriminant image, which contradicts the orbit it was found in"
            )
        letters = self._section.letters_of(element)
        for word in (letters, tuple(reversed(letters))):
            transported = self._transported(plane, word)
            if transported is not None and str(self._point_of(transported)) == str(point):
                return transported
        raise ArithmeticError(
            f"no word in the ambient generators carries the class set of the {start}-th representative "
            f"of {self._lattice} to {point} as a plane, although the discriminant image carries the "
            f"class set there: the lift and the class set disagree"
        )

    def _transported(self, plane, word):
        r"""The image of ``plane`` under the word of ambient-generator letters, or ``None``."""
        inclusion = plane.inclusion()
        domain = inclusion.domain()
        vectors = [inclusion(domain.module_generator(label)) for label in domain.module_generating_set()]
        for label, exponent in word:
            isometry = self._ambient[label - 1]
            if exponent != 1:
                isometry = isometry.inverse()
            vectors = [isometry(vector) for vector in vectors]
        try:
            return self._lattice.primitive_isotropic_subobject(*vectors)
        except (ValueError, ArithmeticError):
            return None


def _libgap():
    from sage.libs.gap.libgap import libgap

    return libgap


def _divided_class_isotropic_plane_orbits(subgroup, representatives, stabilizer_generators=None):
    r"""Return the subgroup's orbits of primitive isotropic planes, by divided classes."""
    if representatives is None:
        raise ValueError(
            f"the divided-class plane orbits of {subgroup} need the O(L)-orbit representatives of "
            f"primitive isotropic planes as an argument: the classification below classifies the "
            f"subgroup's orbits inside each named ambient orbit, and the ambient plane orbit of an "
            f"indefinite lattice is not enumerated by the port's marking-class route without a "
            f"stabilizer computation"
        )
    representatives = tuple(representatives)
    if not representatives:
        raise ValueError(f"the divided-class plane orbits of {subgroup} need at least one ambient representative")
    return _DividedClassPlaneOrbitDecomposition(subgroup, representatives, stabilizer_generators).orbits()


class IsotropicVectorReductionImage(SageObject):
    r"""The group that ``Stab_\Gamma(v)`` induces on \(v^\perp/\mathbf Z v\), with its kernel.

    ``L`` is an even lattice, ``v`` a primitive isotropic vector, ``N = v^\perp/\mathbf Z v``
    its reduction, and ``\Gamma \le O(L)`` a subgroup cut out by a condition on
    \(A_L = L^\#/L\), i.e. ``\Gamma = \rho^{-1}(\rho(\Gamma))`` for the
    discriminant representation \(\rho = \rho_L: O(L) \to O(A_L)\).

    **What the object is.**  ``P_v = Stab_{O(L)}(v)`` is the parabolic at the line,
    and an isometry stabilizing the line preserves \(v^\perp\) and descends, so
    there is the Levi map \(\lambda: P_v \to O(N)\) (D. Dutour Sikirić and
    K. Hulek, *Moduli of polarised Enriques surfaces — computational aspects*,
    arXiv:2302.01679v2, §"The Tits building", theorem `theorem_isotropic_k_planes`,
    printed p. 22, the block form of an isometry preserving a primitive isotropic
    sublattice, with its quotient block).  Then
    \(G_v = \lambda(\Gamma \cap P_v) \le O(N)\) and
    \(K_v = \ker \lambda\) is the unipotent radical of \(P_v\).

    **Why lifting one isometry does not decide membership.**  An isometry
    \(\sigma \in O(N)\) has many lifts in \(P_v\), and two of them differ by an
    element of \(K_v\): if \(g_0\) is one lift then the lifts are exactly
    \(\{k g_0 : k \in K_v\}\).  Hence, with \(\Gamma = \rho^{-1}(\rho(\Gamma))\),

        \(\sigma \in G_v \iff \exists k \in K_v: \rho(k)\rho(g_0) \in \rho(\Gamma)
        \iff \rho(g_0) \in \rho(K_v)\rho(\Gamma)\),

    which is a computation in the finite group \(O(A_L)\) — this object's
    :meth:`contains`.  Deciding it needs the image \(\rho(K_v)\), which is why
    that image is an output (:meth:`kernel_discriminant_image`,
    :meth:`kernel_discriminant_image_is_trivial`) and not an assumption: a single
    lift decides nothing unless \(\rho(K_v)\) is trivial.

    \(K_v\) is a unipotent group and is generated by the Eichler transvections
    \(t(v,a) = E_{v,a}, a \perp v\) (V. Gritsenko, K. Hulek, G. Sankaran,
    *Abelianisation of orthogonal groups and the fundamental group of modular
    varieties*, arXiv:0810.1614, §3.1, equations (4)--(5), transcribed in
    :meth:`sage_extensions.categories.lattices.Lattices.ParentMethods.eichler_transvection`;
    for a line the kernel of the setwise quotient action is \(F^+(1)\cup F^-(1)\) and
    only \(F^+(1)\) fixes \(v\), and that fibre is the integral Eichler transvection
    kernel generated by these quotients).  :meth:`kernel_transvections` returns
    them — one per basis vector of \(v^\perp\), each checked to fix \(v\) and to
    act trivially on \(N\) — and :meth:`kernel_discriminant_image` their image
    \(\rho(K_v)\), with :meth:`kernel_discriminant_image_is_trivial` the output
    the criterion needs.  :meth:`levi_kernel_generators` asks the Levi map for its
    own kernel resolution as the cross-check of that family, and is the expensive
    route.

    **Generators.**  :meth:`reflection_generators` decides, for a supplied family
    of roots of \(L\) lying in \(v^\perp\), which of their reflections lie in
    \(G_v\); that family is what the chamber computation of #297 consumes.
    :meth:`generators` returns the images of the parabolic's own generators that
    lie in \(\Gamma\) — a subgroup of \(G_v\) — and
    :meth:`generators_are_certified_complete` says whether it is known to be all
    of \(G_v\), with :meth:`generation_obstruction` naming the missing statement
    when it is not.
    """

    def __init__(self, subgroup, representative) -> None:
        from sage_extensions.categories.group.predicate_subgroups import PredicateSubgroups

        super().__init__()
        if subgroup not in PredicateSubgroups(subgroup.supergroup()):
            raise ValueError(
                f"\nno reduction image is attached to {subgroup!r}: it is not a subgroup of "
                f"an orthogonal group whose group is known here"
            )
        lattice = subgroup.supergroup().domain()
        vector = self._coerced(lattice, representative)
        if lattice.q(vector) != lattice.base_ring().zero():
            raise ValueError(
                f"no reduction image is attached to the vector {vector!r} of {lattice}: "
                f"it has square {lattice.q(vector)}, not 0, so it spans no isotropic line"
            )
        if not vector.is_primitive():
            raise ValueError(
                f"no reduction image is attached to {vector!r}: the vector is not primitive, so "
                f"v^perp/Zv has torsion and is not the lattice whose isometries this object speaks of"
            )
        if not subgroup.contains_character_kernel():
            raise ValueError(
                f"no reduction image is attached to {subgroup!r}: it is not known to be the preimage "
                f"of its discriminant image, so membership in it is not decidable from O(A_L) and the "
                f"criterion this object decides would be about a subgroup of it"
            )
        self._subgroup = subgroup
        self._lattice = lattice
        self._vector = vector
        self._line = lattice.primitive_isotropic_subobject(vector)
        self._reduction = self._line.isotropic_reduction()

    @staticmethod
    def _coerced(lattice, element):
        r"""Return ``element`` read in ``lattice``, by its coordinates when it is an equal copy's.

        A lattice element belongs to a lattice object; two lattices with the same
        Gram matrix have the same coordinates for the same vector, so passing a
        vector of an equal copy of the ambient lattice is read coordinate-wise, and
        the equality of the two Gram matrices is what makes that an isometry and is
        asserted.  Anything else is a refusal.
        """
        source = element_parent(element)
        if source is lattice:
            return element
        if source.gram_tensor() != lattice.gram_tensor():
            raise ValueError(
                f"\ncannot read {element!r} of {source!r} as a vector of {lattice!r}: the two lattices "
                f"have different Gram matrices, so their coordinates are not the same vector"
            )
        return lattice([int(entry) for entry in element.to_vector()])

    def subgroup(self):
        r"""Return ``\Gamma``, the subgroup whose stabilizer's image this is."""
        return self._subgroup

    def lattice(self):
        r"""Return the ambient even lattice ``L``."""
        return self._lattice

    def vector(self):
        r"""Return the primitive isotropic ``v``."""
        return self._vector

    def line(self):
        r"""Return the isotropic line ``Zv`` as a primitive isotropic subobject."""
        return self._line

    def reduction(self):
        r"""Return ``N = v^\perp/\mathbf Z v``, the lattice the group acts on."""
        return self._reduction

    @cached_method
    def _levi(self):
        return self._reduction.levi_action()

    @cached_method
    def _discriminant_representation(self):
        return self._lattice.discriminant_representation()

    @cached_method
    def _subgroup_discriminant_image(self):
        return self._subgroup.discriminant_image()

    def discriminant_image(self):
        r"""Return ``\rho(\Gamma)`` in ``O(A_L)``, the subgroup that the criterion compares with."""
        return self._subgroup_discriminant_image()

    @cached_method
    def kernel_transvections(self):
        r"""Return the Eichler transvections ``t(v, a)`` over a `ZZ`-basis of ``v^\perp``.

        Each one fixes ``v`` and satisfies ``(t - 1)(v^\perp) <= Zv``, so each lies
        in ``K_v``; both facts are asserted here rather than assumed.  They are the
        family of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1, equation (4),
        and their image is a subgroup of \(\rho(K_v)\).
        """
        transvections = []
        for orthogonal in self._line.vector_perpendicular_basis((self._vector,)):
            if orthogonal.is_zero():
                continue
            transvection = self._line.eichler_transvection(orthogonal)
            assert transvection(self._vector) == self._vector, (
                f"the Eichler transvection of the line {self._line} at {orthogonal} does not fix "
                f"the isotropic vector {self._vector}, so it is not in the parabolic at all"
            )
            assert self._line.acts_trivially_on_isotropic_reduction(transvection) is True, (
                f"the Eichler transvection of the line {self._line} at {orthogonal} does not act "
                f"trivially on {self._reduction}, so it is not in the kernel of the Levi map"
            )
            transvections.append(transvection)
        return tuple(transvections)

    @cached_method
    def kernel_discriminant_image(self):
        r"""Return ``\rho(K_v)`` in ``O(A_L)``: the image of the kernel of the Levi map.

        For a primitive isotropic line ``K_v = F^+(1)``, the integral Eichler
        transvection kernel ``K_Z``: the *setwise* kernel is the union of the two
        fibres ``F^+(1)`` and ``F^-(1)``, and the second consists of the elements
        carrying ``v`` to ``-v``, which are not in the stabilizer of ``v`` at all
        (:meth:`sage_extensions.categories.isotropic_lifts.*.integral_kernel_group_generators`,
        which states that ``F^+(1)`` is ``K_Z`` and that its parameters are the
        period lattice together with the finite residue locus, generated by the
        quotients ``E(x - x_0)`` of Gritsenko--Hulek--Sankaran,
        arXiv:0810.1614, §3.1, equations (4)--(5)).  The family used here is that
        generator family on the level of the lattice: the Eichler transvections
        ``t(v, a)`` over a `ZZ`-basis of ``v^\perp`` (:meth:`kernel_transvections`,
        each checked to be in the kernel), whose image generates ``\rho(K_v)``.
        """
        rho = self._discriminant_representation()
        ambient = self._lattice.discriminant_group().orthogonal_group()
        images = tuple(rho(transvection) for transvection in self.kernel_transvections())
        return ambient.subgroup(tuple(image for image in images if image != ambient.one()))

    def kernel_discriminant_image_is_trivial(self) -> bool:
        r"""Return whether ``\rho(K_v)`` is trivial: whether one lift decides membership."""
        return self.kernel_discriminant_image().cardinality() == 1

    @cached_method
    def levi_kernel_generators(self):
        r"""Return generators of ``K_v`` from the Levi map's own kernel resolution.

        The same subgroup as :meth:`kernel_transvections` generates, through the
        other owner: the Levi map selects a generating resolution of its kernel.
        This is the expensive route and is kept as the cross-check of the
        transvections, not as the path the membership test takes.
        """
        return tuple(self._levi().kernel().group_generators())

    def lift(self, isometry):
        r"""Return a lift of ``isometry`` in ``P_v``, or ``None`` when it has none.

        The lift is the Levi map's own section: it returns an isometry of ``L``
        whose class on ``N`` is ``isometry``, or ``None`` when ``isometry`` is not
        in the image of ``P_v \to O(N)`` at all.
        """
        if isometry.parent() is not self._reduction.Aut():
            raise ValueError(
                f"cannot lift {isometry!r} to the parabolic at {self._vector!r}: it is not an "
                f"isometry of the reduction {self._reduction}, but of {isometry.parent()!r}"
            )
        return self._levi().lift(isometry)

    def reduction_image(self, isometry_of_the_ambient):
        r"""Return the class of an isometry of ``L`` in ``O(N)``.

        The isometry must stabilize the line, which is the parabolic's own
        condition; the class is read through the Levi map.
        """
        if not self._line.stabilizes(isometry_of_the_ambient):
            raise ValueError(
                f"the isometry {isometry_of_the_ambient!r} does not stabilize the line {self._line}, "
                f"so it induces no isometry of {self._reduction}"
            )
        return self._levi()(isometry_of_the_ambient)

    def _coset_meets_the_subgroup(self, image) -> bool:
        r"""Whether ``image . \rho(K_v)`` meets ``\rho(\Gamma)``."""
        subgroup_image = self._subgroup_discriminant_image()
        kernel_image = self.kernel_discriminant_image()
        return any(element * image in subgroup_image for element in kernel_image)

    def contains(self, isometry, *, lift=None) -> bool:
        r"""Return whether ``isometry`` of ``N`` lies in ``G_v``.

        The decision is the criterion of the class docstring: take a lift ``g`` of
        the isometry in ``P_v`` (:meth:`lift`, or the ``lift`` argument when the
        caller has one), and ask whether ``\rho(g)`` lies in
        ``\rho(K_v) \rho(\Gamma)`` — a computation in the finite group ``O(A_L)``.
        An isometry with no lift in ``P_v`` is not in ``G_v``.
        """
        if isometry.parent() is not self._reduction.Aut():
            raise ValueError(
                f"cannot decide membership of {isometry!r} in the image of the stabilizer at "
                f"{self._vector!r}: it is not an isometry of the reduction {self._reduction}"
            )
        if lift is None:
            lift = self.lift(isometry)
        if lift is None:
            return False
        return self._coset_meets_the_subgroup(self._discriminant_representation()(lift))

    def root_reflection(self, root):
        r"""Return the reflection of ``L`` in ``root``, which must lie in ``v^\perp``.

        The reflection in a vector of ``v^\perp`` fixes ``v``, hence induces the
        reflection in its class on ``N``: that is the lift this method uses for a
        reflection of ``N``, whose class the Levi map cannot be asked for without
        a lift anyway.
        """
        root = self._coerced(self._lattice, root)
        if self._lattice.b(root, self._vector) != self._lattice.base_ring().zero():
            raise ValueError(
                f"the vector {root!r} does not lie in the perpendicular of {self._vector!r}, so its "
                f"reflection moves that vector and induces no isometry of {self._reduction}"
            )
        reflection = self._lattice.reflection(root)
        assert reflection(self._vector) == self._vector, (
            f"the reflection of {self._lattice} in {root} does not fix the isotropic vector "
            f"{self._vector}, so it is not a lift in the parabolic at its line"
        )
        return reflection

    def contains_root_reflection(self, root) -> bool:
        r"""Return whether the reflection in ``root`` (a vector of ``v^\perp``) lies in ``G_v``.

        ``root`` is a vector of the ambient lattice, so a caller holding a root
        family written in ``L`` (Sterk's printed cusps, for instance) asks this
        directly.  The reflection of ``L`` in ``root`` is the lift of the
        reflection of ``N`` in its class, and the criterion of :meth:`contains`
        then decides.
        """
        reflection = self.root_reflection(root)
        return self.contains(self.reduction_image(reflection), lift=reflection)

    @cached_method
    def parabolic_generators(self):
        r"""Return the parabolic's own generators that lie in ``\Gamma``.

        The family is
        :meth:`sage_extensions.categories.isotropic_parabolics.PrimitiveIsotropicSubobjects.ParentMethods.parabolic_stabilizer_generators`
        -- the Eichler transvections, the half-vector transvections, the quotient
        reflections and the Levi lifts -- filtered by membership in ``\Gamma``,
        which is decided on the discriminant image, since ``\Gamma`` is the
        preimage of its own.  That family is stated for a primitive isotropic
        *plane* and refuses rank one, so at a line this method raises with the
        owner's refusal; :meth:`reflection_generators` is the line's generator
        source (#312).
        """
        rho = self._discriminant_representation()
        subgroup_image = self._subgroup_discriminant_image()
        return tuple(
            generator
            for generator in self._line.parabolic_stabilizer_generators()
            if rho(generator) in subgroup_image
        )

    @cached_method
    def generators(self):
        r"""Return the images in ``O(N)`` of :meth:`parabolic_generators`."""
        return finite_ordered_set(
            tuple(self.reduction_image(generator) for generator in self.parabolic_generators())
        )

    @cached_method
    def _reflections(self, roots):
        found = []
        for root in roots:
            reflection = self.root_reflection(root)
            if self.contains(self.reduction_image(reflection), lift=reflection):
                found.append((root, reflection))
        return tuple(found)

    def reflection_generators(self, roots):
        r"""Return the reflections in ``G_v`` among the reflections in ``roots``.

        ``roots`` is a family of vectors of the ambient lattice lying in
        ``v^\perp`` whose reflections are integral -- Sterk's printed cusp roots,
        for instance.  Each reflection of ``L`` in such a root fixes ``v`` and
        induces the reflection in its class on ``N``, so this decides, for every
        member of the family, whether that reflection of ``N`` lies in ``G_v``,
        by the criterion of :meth:`contains` (:meth:`contains_root_reflection`).
        The result is ``(root, reflection of N)`` pairs, one per member in the
        group; the reflections are what the chamber computation of #297 consumes.
        """
        return tuple(
            (root, self.reduction_image(reflection))
            for root, reflection in self._reflections(tuple(roots))
        )

    def generators_are_certified_complete(self) -> bool:
        r"""Whether :meth:`generators` is known to generate all of ``G_v``."""
        return self.generation_obstruction() is None

    def generation_obstruction(self) -> str | None:
        r"""Return what keeps :meth:`generators` from being all of ``G_v``, or ``None``.

        At a primitive isotropic *line* two statements are missing and neither is
        made here: the parabolic's constructed generator family is stated for a
        primitive isotropic plane and refuses rank one
        (``parabolic_stabilizer_generators``), and the exact generators of the
        line's parabolic are the port's line stabilizer, which at Sterk's first
        cusp of ``T_{\mathrm{En}}`` does not return within 540 s (#312).  So
        :meth:`generators` is empty at a line and :meth:`reflection_generators` is
        its generator source, while :meth:`contains` decides membership in all of
        ``G_v`` regardless of whether any generating family is known.
        """
        if int(self._line.module_rank()) == 1:
            return (
                f"the parabolic at the line {self._vector!r} has no constructed generator family: "
                f"parabolic_stabilizer_generators is stated for a primitive isotropic plane and refuses "
                f"rank one, and the port's line stabilizer generators do not return in 540 s at Sterk's "
                f"first Enriques cusp; the reflection subgroup of G_v is available through "
                f"reflection_generators, and the chamber of its reflection part is what #297 supplies"
            )
        if not self._line.is_parabolic_complete():
            return (
                f"the parabolic at {self._vector!r} does not split off as an orthogonal summand of "
                f"{self._lattice}, so its constructed generators are only a subgroup of it (#331, #297)"
            )
        return (
            f"the members of the parabolic's generating family at {self._vector!r} that lie in "
            f"{self._subgroup} generate only a subgroup of their intersection: the Reidemeister step "
            f"over [P_v : Gamma cap P_v] is not run here"
        )

    def _repr_(self) -> str:
        return (
            f"The image of the stabilizer of the isotropic vector {self._vector} in "
            f"{self._subgroup} acting on {self._reduction}"
        )


__all__ = [
    "ArithmeticCuspIncidence",
    "CuspIncidence",
    "FlagType",
    "IsotropicFlag",
    "IsotropicPlaneOrbit",
    "IsotropicVectorReductionImage",
    "OrientedIsotropicFlag",
    "RationalIsotropicFlagComplex",
]
