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

    def graded_quotient_action(self):
        r"""Return the action ``Stab(F) -> GL(gr F + I_t^perp/I_t)`` on successive quotients.

        The codomain is the general linear group of a free module with one
        coordinate block for each ``I_j/I_{j-1}``, in the adapted basis, and a
        final block for ``I_t^perp/I_t``. The morphism is block diagonal, so
        its image is the actual image in the product of the block groups.
        """
        ring = self._lattice.base_ring()
        group = self._lattice.O()
        stabilizer = group.subgroup(tuple(group.isotropic_stabilizer_generators(self, flag=True)))
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

            terms = tuple(obj.terms())
            arrows = tuple(
                left.inclusion().factor_through(right.inclusion())
                for left, right in pairwise(terms)
            ) + (terms[-1].inclusion(),)
            objects = (arrows[0].domain(), *(arrow.codomain() for arrow in arrows))
            diagram = FiniteSequenceDiagram(objects, arrows, Lattices(obj.lattice().base_ring()))
            return _marked_isotropic_category(obj.lattice(), len(terms))(diagram)


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
        dimensions = (rank,)
    if dimensions[-1] < 0:
        raise ValueError(f"the isotropic sublattice rank must be nonnegative, got {rank} in {lattice}")
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


__all__ = [
    "ArithmeticCuspIncidence",
    "CuspIncidence",
    "FlagType",
    "IsotropicFlag",
    "OrientedIsotropicFlag",
    "RationalIsotropicFlagComplex",
]
