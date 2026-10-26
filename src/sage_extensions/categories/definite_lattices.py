r"""Exact algorithms for finite definite integral lattices."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product
from typing import TYPE_CHECKING

from sage.libs.pari import pari
from sage.matrix.constructor import matrix as engine_matrix
from sage.modules.free_module_element import vector as engine_vector
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import parent as element_parent

from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values
from sage_extensions.categories.modules.pure.modules import (
    MatrixSpaces,
    ModuleSubobjects,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
)
from sage_extensions.categories.schemes.polytopes import ConvexPolytopes
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.set_categories import finite_ordinal_set
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.rings.real import RR, _owned_real_from_engine_expression
from sage_extensions.tensors.tensor import _engine_component_matrix, tensor

if TYPE_CHECKING:
    from sage.structure.element import RingElement
    from sage_extensions.categories.lattices import Lattices


def _definite_sign(lattice):
    if not lattice.module_rank().is_finite():
        raise TypeError(
            f"cannot run a definite-lattice algorithm on {lattice}: it needs a lattice of "
            f"finite rank, and {lattice} has rank {lattice.module_rank()}"
        )
    _signature = lattice.signature_pair()
    positive, negative = _signature.first(), _signature.second()
    rank = lattice.module_rank()
    ring = lattice.base_ring()
    if positive == rank and negative == 0:
        return ring.one()
    if negative == rank and positive == 0:
        return -ring.one()
    raise ValueError(
        f"cannot run a definite-lattice algorithm on {lattice}: it must be positive or "
        f"negative definite, but its signature is ({positive}, {negative}) in rank {rank}"
    )


def _positive_gram(lattice):
    r"""Return the sign and positive Gram tensor used by definite engines."""
    sign = _definite_sign(lattice)
    return sign, sign * lattice.gram_tensor()


def _element_from_coordinates(lattice, coordinates):
    ring = lattice.base_ring()

    def owned(coefficient):
        if element_parent(coefficient) is ring:
            return coefficient
        return _owned_engine_element(ring, coefficient)

    return lattice(
        {
            label: owned(coefficient)
            for label, coefficient in zip(
                lattice.module_generating_set(), coordinates, strict=True
            )
            if coefficient
        }
    )


def _shell(lattice, square, coordinate_rows):
    r"""Return the finite ordered set of the vectors of ``lattice`` with these coordinates.

    The engine enumerates each vector of a shell once, so the rows are
    distinct and need no identification.  A vector is raised into the
    lattice when it is first asked for, and membership is the lookup of its
    coordinates.
    """
    index_set = finite_ordinal_set(len(coordinate_rows))
    positions = {
        tuple(int(coordinate) for coordinate in row): position
        for position, row in enumerate(coordinate_rows)
    }

    @cache
    def element_at(position):
        return _element_from_coordinates(lattice, coordinate_rows[int(position)])

    def index_of(element):
        if element_parent(element) is not lattice:
            return None
        position = positions.get(tuple(int(coordinate) for coordinate in element))
        if position is None:
            return None
        return index_set(position)

    return FiniteOrderedSets().from_indexed(
        index_set,
        element_at,
        index_of=index_of,
        contains=lambda element: index_of(element) is not None,
        name=f"vectors of square {square} in {lattice}",
    )


@dataclass(frozen=True)
class LatticeReduction:
    original: object
    reduced: object
    isometry: object
    change_of_basis_matrix: object


def _lll_reduction(lattice):
    _sign, positive_gram = _positive_gram(lattice)
    engine_gram = _engine_component_matrix(positive_gram)
    transformation = engine_gram.LLL_gram()
    ring = lattice.base_ring()
    rank = int(lattice.module_rank())
    basis_map = ring.matrix_space(rank, rank).from_rows(
        tuple(
            tuple(
                _owned_engine_element(ring, transformation[row, column])
                for column in range(rank)
            )
            for row in range(rank)
        )
    )
    return _reduction_from_transformation(lattice, basis_map)


def _reduction_from_backend_rows(lattice, backend_rows):

    ring = lattice.base_ring()
    rank = int(lattice.module_rank())
    # Definite-lattice engines return basis vectors as rows.  The live linear
    # map acts on coordinate columns, hence the transpose here.
    basis_map = ring.matrix_space(rank, rank).from_rows(
        tuple(
            tuple(
                _owned_engine_element(ring, backend_rows[column, row])
                for column in range(rank)
            )
            for row in range(rank)
        )
    )
    return _reduction_from_transformation(lattice, basis_map)


def _reduction_from_transformation(lattice, basis_map):

    if basis_map.parent() not in MatrixSpaces(lattice.base_ring()):
        raise TypeError(
            f"{basis_map} cannot change the basis of {lattice}: a change of basis must be "
            f"a matrix over {lattice.base_ring()}, but it lies in {basis_map.parent()}"
        )
    original_generators = tuple(lattice.module_generators())
    images = tuple(
        sum(
            (
                lattice.scalar_multiple(
                    basis_map[row, column], original_generators[row]
                )
                for row in range(len(original_generators))
                if basis_map[row, column]
            ),
            lattice.zero(),
        )
        for column in range(len(original_generators))
    )
    reduced_gram = lattice.gram_tensor().pullback(basis_map)
    if lattice in ModuleSubobjects(lattice.base_ring()):
        from sage_extensions.categories.lattices import (
            _lattice_subobject_spanning,
        )

        ambient = lattice.ambient_lattice()
        old_inclusion = lattice.inclusion()
        embedded_reduced_basis = finite_ordered_set(
            tuple(old_inclusion(image) for image in images)
        )
        reduced = _lattice_subobject_spanning(
            ambient,
            embedded_reduced_basis,
        )
        if reduced.gram_tensor() != reduced_gram:
            raise ArithmeticError(
                f"the reduced basis of the sublattice {lattice} of {ambient} was computed "
                f"wrongly: its Gram matrix {reduced.gram_tensor()} is not the pullback "
                f"{reduced_gram} of the form along the change of basis"
            )
    else:
        reduced = lattice.lattice_category()(reduced_gram)
    isometry = reduced.Isom(lattice)(images)
    return LatticeReduction(lattice, reduced, isometry, basis_map)


def _bkz_reduction(lattice, block_size=20):
    r"""Return a BKZ-reframed copy with its exact integral isometry witness."""
    from fpylll import BKZ, GSO, LLL, IntegerMatrix

    _sign, positive_gram = _positive_gram(lattice)
    rank = positive_gram.tensor_shape()[0]
    if rank <= 1:

        return _reduction_from_transformation(
            lattice, lattice.base_ring().matrix_space(rank, rank).identity_matrix()
        )
    block_size = min(max(2, int(block_size)), rank)
    backend_gram = IntegerMatrix.from_matrix(_engine_component_matrix(positive_gram))
    backend_transformation = IntegerMatrix.identity(rank)
    gso = GSO.Mat(
        backend_gram,
        U=backend_transformation,
        gram=True,
        update=True,
    )
    lll = LLL.Reduction(gso)
    lll()
    BKZ.Reduction(gso, lll, BKZ.Param(block_size=block_size))()
    from sage.matrix.constructor import matrix as sage_matrix

    backend_rows = sage_matrix(
        SageZZ,
        rank,
        rank,
        [
            backend_transformation[row, column]
            for row in range(rank)
            for column in range(rank)
        ],
    )
    return _reduction_from_backend_rows(lattice, backend_rows)


def _hkz_reduction(lattice):
    return lattice.bkz_reduction(block_size=int(lattice.module_rank()))


def _minimum(lattice):
    assert _engine_ring(lattice.base_ring()) is SageZZ, (
        f"the minimum of {lattice} is computed here only for integral lattices "
        f"over ZZ, but {lattice} is over {lattice.base_ring()}"
    )
    sign, positive_gram = _positive_gram(lattice)
    if positive_gram.tensor_shape()[0] == 0:
        raise ValueError("the zero lattice has no nonzero vector and no minimum")
    from sage_extensions.categories.lattice_engines import _oscar_lattices

    minimum_value = _owned_engine_element(
        lattice.base_ring(),
        _oscar_lattices.definite_minimum(positive_gram),
    )
    return sign * minimum_value


def _square_shell(positive_gram, target, reflective):
    r"""All vectors of the positive definite integral square shell.

    The inverse-Gram Cauchy--Schwarz bound gives a complete coordinate box.
    Exhaust it directly when it has at most 10,000 candidates, avoiding a
    Julia startup for small shells. Larger boxes use the maintained Hecke
    enumeration below.

    Hecke's inclusive ``short_vectors(L, target, target)`` enumerates one
    vector per sign pair, using rational pseudo-Cholesky enumeration after
    Gram LLL reduction, and transports coordinates to the original basis.
    Restore both signs here. For a reflective vector, ``target`` divides
    every entry of ``2 G v``. Zero and negative squares are handled by the
    caller before this nonzero shell computation.
    """
    form = _engine_component_matrix(positive_gram).change_ring(SageZZ)
    rank = form.nrows()
    inverse = form.change_ring(SageQQ).inverse()
    engine_target = SageZZ(_engine_element(target.parent(), target))
    squared_bound = SageQQ(engine_target) * max(inverse.diagonal())
    bound = int(squared_bound.floor().isqrt())
    if (2 * bound + 1) ** rank <= 10000:
        shell = []
        for coordinates in product(range(-bound, bound + 1), repeat=rank):
            vector = engine_vector(SageZZ, coordinates)
            if vector * form * vector != engine_target:
                continue
            if reflective and any(entry % engine_target for entry in 2 * form * vector):
                continue
            shell.append(vector)
        return tuple(shell)

    from sage_extensions.categories.lattice_engines import _oscar_lattices

    representatives = _oscar_lattices.square_shell(positive_gram, target)
    shell = []
    for row in representatives.rows():
        vector = engine_vector(SageZZ, row)
        if reflective and any(entry % target for entry in 2 * form * vector):
            continue
        shell.extend((vector, -vector))
    return tuple(shell)


def _square_coordinate_bound(
    lattice: Lattices.ParentMethods, square: RingElement
) -> RingElement:
    r"""Evaluate the inverse-Gram Cauchy--Schwarz bound using exact rationals."""
    ring = lattice.base_ring()
    if lattice.module_rank() == 0:
        return ring.zero()
    sign, positive_gram = _positive_gram(lattice)
    target = sign * square
    if target <= ring.zero():
        return ring.zero()
    inverse = _engine_component_matrix(positive_gram).change_ring(SageQQ).inverse()
    squared_bound = SageQQ(_engine_element(ring, target)) * max(inverse.diagonal())
    bound = squared_bound.floor().isqrt()
    return _owned_engine_element(ring, bound)


def _vectors_of_square(lattice, square):
    r"""The finite shell ``{v in L : b(v, v) = square}`` of a definite lattice over ``ZZ``.

    The enumeration is of integral coordinate vectors; over ``QQ`` that is
    only the shell of the integral span of the chosen basis, not the rational
    fibre.  Its one caller, ``Lattices.ParentMethods.vectors_of_square``,
    asserts that hypothesis.
    """
    sign, positive_gram = _positive_gram(lattice)
    square = lattice.base_ring()(square)
    target = sign * square
    if target < 0:
        return finite_ordered_set(())
    if target == 0:
        rank = _engine_component_matrix(positive_gram).nrows()
        return _shell(lattice, square, (engine_vector(SageZZ, [0] * rank),))
    return _shell(lattice, square, _square_shell(positive_gram, target, False))


def _roots(lattice):
    sign = _definite_sign(lattice)
    return lattice.vectors_of_square(2 * sign)


def _roots_of_square(lattice, square):
    r"""Return the vectors ``v`` with ``b(v,v) = square`` whose reflection is integral."""
    square = lattice.base_ring()(square)
    if lattice.module_rank() == 0:
        return finite_ordered_set(())
    sign, positive_gram = _positive_gram(lattice)
    target = int(sign * square)
    if target <= 0:
        return finite_ordered_set(())
    return _shell(lattice, square, _square_shell(positive_gram, target, True))


def _root_sublattice(lattice):
    r"""Return the formed subobject generated by all square-two roots."""
    from sage.combinat.root_system.cartan_type import CartanType

    from sage_extensions.categories._lattice import _root_system_type_name

    ordered, component_types = _norm_two_simple_system(lattice)
    if not component_types:
        return lattice.subobject_on(())
    recognized = component_types[0] if len(component_types) == 1 else CartanType(component_types)

    if lattice.is_negative_definite():
        return lattice._root_subobject_on(ordered, _root_system_type_name(recognized))
    return lattice.subobject_on(ordered)


_NORM_TWO_LETTER_ORDER = {"E": 0, "D": 1, "A": 2}


def _norm_two_root_types(lattice):
    r"""Return the label of the type of the square-two root system of a definite lattice.

    Each irreducible component is spelled by its letter and rank, and the
    components are joined by ``+``, ``E`` before ``D`` before ``A`` and
    decreasing rank within one letter, as ``E8+E8+A1`` and ``E7+D10``.  The
    empty root system is the empty sum ``""``.
    """
    _ordered, component_types = _norm_two_simple_system(lattice)
    components = sorted(
        (_NORM_TWO_LETTER_ORDER[component.type()], -int(component.rank()), f"{component.type()}{int(component.rank())}")
        for component in component_types
    )
    return "+".join(label for _letter, _rank, label in components)


def _norm_two_simple_system(lattice):
    r"""Return a simple system of the square-two roots and the ADE type of each component.

    The simple roots are returned component by component, each component in
    the order of the index set of its recognized type.  A component of the
    Coxeter graph of the simple roots is recognized by graph isomorphism
    with the Dynkin diagram of ``A_n``, ``D_n`` or ``E_n``.  The engine
    Cartan types stay inside this module's two consumers.
    """
    from sage.combinat.root_system.cartan_type import CartanType
    from sage.graphs.graph import Graph

    root_vectors = tuple(lattice.roots())
    if not root_vectors:
        return (), []
    simple = _simple_roots(lattice, root_vectors)
    graph = Graph(multiedges=False, loops=False)
    graph.add_vertices(range(len(simple)))
    graph.add_edges((left, right) for left in range(len(simple)) for right in range(left + 1, len(simple)) if simple[left].b(simple[right]) != 0)
    ordered = []
    component_types = []
    for component in graph.connected_components(sort=True):
        size = len(component)
        candidates = [CartanType(["A", size])]
        if size >= 4:
            candidates.append(CartanType(["D", size]))
        if size in (6, 7, 8):
            candidates.append(CartanType(["E", size]))
        component_graph = graph.subgraph(component)
        for candidate_type in candidates:
            standard = Graph(
                candidate_type.dynkin_diagram().to_undirected(),
                multiedges=False,
            )
            isomorphic, certificate = component_graph.is_isomorphic(standard, certificate=True)
            if isomorphic:
                break
        else:
            raise RuntimeError(
                f"a connected component of the root system of {lattice}, with "
                f"{size} simple roots, was not recognized as type A, D or E; every "
                f"finite simply-laced root system is of ADE type, so the simple roots "
                f"were computed wrongly"
            )
        by_label = {certificate[vertex]: vertex for vertex in component}
        ordered.extend(simple[by_label[label]] for label in candidate_type.index_set())
        component_types.append(candidate_type)
    return tuple(ordered), component_types


def _simple_roots(lattice, roots):
    r"""Return the simple roots of the positive system of ``roots`` in the coordinate order.

    The positive roots are those whose first nonzero coordinate in the
    framing of ``lattice`` is positive, and a positive root is simple exactly
    when it is not the sum of two positive roots (Humphreys, *Introduction to
    Lie Algebras and Representation Theory*, §10.1).
    """
    zero = (SageZZ.zero(),) * int(lattice.module_rank())
    positive = tuple(
        (root, coordinates)
        for root in roots
        if (coordinates := _coordinate_tuple(lattice, root)) > zero
    )
    positive_coordinates = {coordinates for _root, coordinates in positive}
    return tuple(
        candidate
        for candidate, candidate_coordinates in positive
        if not any(
            tuple(left - right for left, right in zip(candidate_coordinates, other_coordinates, strict=True)) in positive_coordinates
            for other_coordinates in positive_coordinates
            if other_coordinates != candidate_coordinates
        )
    )


def _reflective_root_system_components(lattice):
    r"""Return the irreducible components of the reflective root system of a definite lattice.

    The primitive reflective roots of a definite lattice form a finite reduced
    crystallographic root system.  Its simple roots span one connected rooted
    Coxeter diagram per irreducible component, since a root system is
    irreducible exactly when its Coxeter graph is connected (Humphreys,
    *Introduction to Lie Algebras and Representation Theory*, §10.4 and
    §11.3).
    """
    from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams

    from sage_extensions.categories.lattices import DefiniteLattices
    simple = _simple_roots(lattice, tuple(DefiniteLattices(lattice.base_ring())(lattice).reflective_roots()))
    match simple:
        case ():
            return finite_ordered_set(())
    return CoxeterDiagrams().from_roots(finite_indexed_family_from_values(None, simple)).connected_components()


def _vectors_of_square_and_divisibility(lattice, square, divisibility):
    divisibility = lattice.base_ring()(divisibility)
    fibre = lattice.vectors_of_square(square)
    if fibre.is_finite() is not True:
        return fibre.condition_set(lambda vector: vector.div() == divisibility)
    return finite_ordered_set(tuple(
        vector
        for vector in fibre
        if vector.div() == divisibility
    ))


def _shortest_vectors(lattice):
    target = lattice.minimum()
    return lattice.vectors_of_square(target)


def _target_coordinates(lattice, target):
    if element_parent(target) is lattice:

        coordinates = target.to_vector()
        target = [
            coordinates(label)
            for label in lattice.module_generating_set()
        ]
    rationals = lattice.base_ring().fraction_field()
    point = tensor.vector(rationals, target)
    if point.tensor_shape()[0] != int(lattice.module_rank()):
        raise ValueError(
            f"{target} is not a point of {lattice} tensor QQ: it must have "
            f"{lattice.module_rank()} coordinates, one per basis vector, but has "
            f"{point.tensor_shape()[0]}"
        )
    return point


class _ExactCVPEngine:
    r"""Cached exact closest-vector backend for one definite lattice."""

    def __init__(self, lattice) -> None:
        self.lattice = lattice
        self.rank = int(lattice.module_rank())
        self.sign, positive_gram = _positive_gram(lattice)
        self.ring = lattice.base_ring()
        self.rationals = self.ring.fraction_field()
        self.engine_sign = SageQQ(_engine_element(self.ring, self.sign))
        self.engine_gram = _engine_component_matrix(positive_gram)
        self.engine_gram_q = self.engine_gram.change_ring(SageQQ)
        self.pari_gram = self.engine_gram.__pari__()

    @classmethod
    def _from_positive_engine_gram(cls, ring, engine_gram):
        r"""Prepare the coordinate CVP backend directly from a positive Gram matrix.

        This lowering constructor is for algorithms that already own an exact
        definite Gram and use only the coordinate-level CVP methods.  It avoids
        constructing a categorical lattice solely to hand the same Gram back
        to PARI.
        """
        if engine_gram.nrows() != engine_gram.ncols():
            raise ValueError("an exact CVP Gram must be square")
        result = cls.__new__(cls)
        result.lattice = None
        result.rank = int(engine_gram.nrows())
        result.sign = ring.one()
        result.ring = ring
        result.rationals = ring.fraction_field()
        result.engine_sign = SageQQ.one()
        result.engine_gram = engine_gram
        result.engine_gram_q = engine_gram.change_ring(SageQQ)
        result.pari_gram = engine_gram.__pari__()
        return result

    def _engine_scalar(self, value):
        parent = element_parent(value)
        if parent is SageQQ:
            return value
        if parent is self.rationals:
            return SageQQ(_engine_element(self.rationals, value))
        if parent is self.ring:
            return SageQQ(_engine_element(self.ring, value))
        owned = self.rationals(value)
        return SageQQ(_engine_element(self.rationals, owned))

    def _engine_target_coordinates(self, target):
        if self.lattice is not None and (
            element_parent(target) is self.lattice
            or element_parent(target) is self.lattice.vector_space()
        ):
            coordinates = target.to_vector()
            return tuple(
                self._engine_scalar(coordinates(label))
                for label in self.lattice.module_generating_set()
            )
        coordinates = tuple(target)
        if len(coordinates) != self.rank:
            ambient = self.lattice if self.lattice is not None else f"rank-{self.rank} definite Gram"
            raise ValueError(
                f"{target} is not a point of {ambient} tensor QQ: it must have "
                f"{self.rank} coordinates, one per basis vector, but has "
                f"{len(coordinates)}"
            )
        return tuple(self._engine_scalar(coordinate) for coordinate in coordinates)

    def _center(self, target):
        point = self._engine_target_coordinates(target)
        translation = tuple(coordinate.round() for coordinate in point)
        centered = engine_vector(
            SageQQ,
            tuple(
                coordinate - SageQQ(translate)
                for coordinate, translate in zip(point, translation, strict=True)
            ),
        )
        return point, translation, centered

    def _filtered_candidates(self, centered, positive_bound):
        _count, _largest, raw_coordinates = self.pari_gram.qfcvp(
            centered.__pari__().Col(),
            positive_bound + SageQQ(1) / 2,
        )
        for column in engine_matrix(SageQQ, raw_coordinates).columns():
            displacement = column - centered
            positive_square = (
                displacement * self.engine_gram_q * displacement
            )
            if positive_square <= positive_bound:
                yield column, positive_square

    def has_close_vector(self, target, square_bound) -> bool:
        _point, _translation, centered = self._center(target)
        positive_bound = self.engine_sign * self._engine_scalar(square_bound)
        if positive_bound < 0:
            return False
        return any(
            True
            for _column, _square in self._filtered_candidates(
                centered, positive_bound
            )
        )

    def closest_vector(self, target):
        _point, translation, centered = self._center(target)
        zero = engine_vector(SageQQ, [0] * len(translation))
        displacement = zero - centered
        best_distance = displacement * self.engine_gram_q * displacement
        best_coordinates = tuple(translation)
        for column, positive_square in self._filtered_candidates(
            centered,
            best_distance,
        ):
            coordinates = tuple(
                self.ring(int(entry) + int(translate))
                for entry, translate in zip(column, translation, strict=True)
            )
            if positive_square < best_distance or (
                positive_square == best_distance
                and tuple(int(entry) for entry in coordinates)
                < tuple(int(entry) for entry in best_coordinates)
            ):
                best_distance = positive_square
                best_coordinates = coordinates
        return _element_from_coordinates(self.lattice, best_coordinates)

    def close_vector_coordinates(self, target, square_bound):
        r"""Return exact engine-coordinate rows and signed squared distances.

        This is the private lowering primitive beneath :meth:`close_vectors`.
        It deliberately stays on Sage integer/rational carriers so algorithms
        that immediately reconstruct their own semantic codomain do not first
        allocate every intermediate vector as an element of this lattice.
        """
        _point, translation, centered = self._center(target)
        positive_bound = self.engine_sign * self._engine_scalar(square_bound)
        if positive_bound < 0:
            raise ValueError(
                f"no vectors of {self.lattice} can satisfy the bound {square_bound} on "
                f"q(x - target): the bound must have the sign of the form, which is "
                f"{'positive' if self.sign > 0 else 'negative'} definite"
            )
        candidates = {}
        for column, positive_square in self._filtered_candidates(
            centered, positive_bound
        ):
            coordinates = tuple(
                SageZZ(int(entry) + int(translate))
                for entry, translate in zip(column, translation, strict=True)
            )
            candidates[coordinates] = self.engine_sign * positive_square
        return tuple(candidates.items())

    def close_vectors(self, target, square_bound):
        candidates = {}
        for engine_coordinates, engine_square in self.close_vector_coordinates(
            target, square_bound
        ):
            coordinates = tuple(self.ring(int(entry)) for entry in engine_coordinates)
            vector = _element_from_coordinates(self.lattice, coordinates)
            signed_square = _owned_engine_element(
                self.rationals,
                engine_square,
            )
            candidates[_coordinate_tuple(self.lattice, vector)] = (
                vector,
                signed_square,
            )
        vectors = finite_ordered_set(
            tuple(vector for vector, _square in candidates.values())
        )
        by_coordinates = {
            coordinates: square
            for coordinates, (_vector, square) in candidates.items()
        }
        return finite_indexed_family(
            vectors,
            lambda vector: by_coordinates[
                _coordinate_tuple(self.lattice, vector)
            ],
            name="Close lattice vectors",
        )


def _exact_cvp_engine(lattice):
    return _ExactCVPEngine(lattice)


def _closest_vector(lattice, target):
    r"""Return the exact closest lattice vector to a rational target."""
    return lattice._exact_cvp_engine().closest_vector(target)


def _close_vectors(lattice, target, square_bound):
    r"""Return the lattice vectors within the stated quadratic bound of ``target``.

    The target is a point of ``L tensor QQ`` in the selected lattice frame.
    For a positive-definite lattice this returns the ``x in L`` with
    ``q(x-target) <= square_bound``; for a negative-definite lattice the same
    statement uses the lattice's own negative form, so ``square_bound`` is
    negative and ``q(x-target) >= square_bound``.  The values of the returned
    indexed family are the exact signed squares ``q(x-target)`` in the
    fraction field of the base ring.

    PARI's ``qfcvp`` supplies the finite candidate set for the positive metric
    ``sign*q``.  Because its radius interface passes through a floating bound,
    every candidate is filtered again against the exact rational quadratic
    form before it crosses back into the owned lattice.
    """
    return lattice._exact_cvp_engine().close_vectors(target, square_bound)


def _babai(lattice, target):
    r"""Return Babai's LLL nearest-plane approximation."""
    point = _target_coordinates(lattice, target)
    rank = int(lattice.module_rank())
    if rank == 0:
        return lattice.zero()
    _sign, gram = _positive_gram(lattice)
    from sage.modules.free_module_element import vector as sage_vector

    rationals = point.base_ring()
    # Sage's LLL_gram returns U with U^T G U reduced (matrix2.pyx, LLL_gram):
    # column j of U is the j-th reduced basis vector, so U is the map from
    # reduced coordinates to the lattice frame.
    basis_map = _engine_component_matrix(gram).LLL_gram().change_ring(SageQQ)
    point_backend = sage_vector(
        SageQQ,
        [_engine_element(rationals, entry) for entry in point],
    )
    reduced_coordinates = basis_map.inverse() * point_backend
    rounded = sage_vector(SageQQ, [entry.round() for entry in reduced_coordinates])
    original = basis_map * rounded
    return _element_from_coordinates(lattice, tuple(original))


def _voronoi_region(lattice, bound=None):
    r"""Compute the exact rational Voronoi region, not just a bounded truncation.

    First include the inequalities for every signed basis vector; their
    independent covectors bound a polytope P.  Let R^2 be the maximum of q
    on its vertices (convexity bounds q everywhere on P by this number).
    For q(v) > 4 R^2 and x in P, Cauchy--Schwarz gives
    b(x,v) <= sqrt(q(x)q(v)) < q(v)/2.  Hence all omitted inequalities are
    automatic on P once all lattice vectors through 4 R^2 are included.

    Both enumerations are exact PARI qfminim calls.  ``bound`` is a lower
    bound on the initial enumeration, never a request to return an outer
    approximation as the Voronoi cell.  Sage's rational polyhedron engine
    supplies the exact vertex maximum and irredundant facet inequalities.
    """
    from sage.geometry.polyhedron.constructor import Polyhedron

    _sign, gram = _positive_gram(lattice)
    rank = gram.tensor_shape()[0]
    rationals = lattice.base_ring().fraction_field()
    if rank == 0:
        return Polyhedron(vertices=[[]], base_ring=SageQQ)
    gram_q = gram.change_ring(rationals)
    engine_gram = _engine_component_matrix(gram)

    def region_from_bound(radius):
        backend_radius = SageZZ(int(radius))
        _count, _largest, raw_coordinates = engine_gram.__pari__().qfminim(
            backend_radius, None
        )
        coordinates = raw_coordinates
        inequalities = []
        for column_index in range(coordinates.ncols()):
            column = tensor.vector(
                rationals,
                [
                    _owned_engine_element(rationals,
                        SageQQ(coordinates[row_index, column_index])
                    )
                    for row_index in range(rank)
                ],
            )
            for signed in (column, -column):
                covector = gram_q * signed
                square = covector * signed
                owned_entries = [
                    square / rationals(2),
                    *(-covector[index] for index in range(int(covector.tensor_shape()[0]))),
                ]
                inequalities.append(
                    [_engine_element(rationals, entry) for entry in owned_entries]
                )
        return Polyhedron(ieqs=inequalities, base_ring=SageQQ)

    initial_bound = max(
        SageQQ(_engine_element(rationals, gram_q[index, index])).ceil()
        for index in range(rank)
    ) + 1
    if bound is not None:
        initial_bound = max(initial_bound, SageQQ(bound).ceil())
    outer = region_from_bound(initial_bound)
    assert outer.is_compact(), (
        f"the first approximation to the Voronoi cell of {lattice}, cut out by the "
        f"vectors of square at most {initial_bound}, is not bounded; it must be, since "
        f"it contains the inequalities of a basis and its negative"
    )
    gram_engine_q = engine_gram.change_ring(SageQQ)
    radius_squared = max(
        engine_vector(SageQQ, vertex) * gram_engine_q * engine_vector(SageQQ, vertex)
        for vertex in outer.vertices_list()
    )
    complete_bound = max(initial_bound, (4 * radius_squared).ceil() + 1)
    return outer if complete_bound == initial_bound else region_from_bound(complete_bound)


def _voronoi_cell(lattice, bound=None):
    r"""Return the Voronoi cell of ``lattice``: a convex polytope in ``L tensor QQ``.

    The cell is built by ``ConvexPolytopes(lattice)`` on the vertices of the region,
    with ``lattice`` as its ambient coordinate lattice.  Its facets and their
    relevant vectors are :func:`_voronoi_facets`.
    """
    region = _voronoi_region(lattice, bound=bound)
    return ConvexPolytopes(lattice)(region.vertices_list())


def _relevant_vector_of_inequality(lattice, inequality):
    r"""Recover the relevant vector without assuming a normalized inequality.

    A native inequality c + a.x >= 0 can be a positive multiple lambda of
    q(v)/2 - b(x,v) >= 0.  Thus d=-G^-1 a=lambda v and
    v=(2c/q(d))d.  This is invariant under the engine's rescaling of its
    inequalities, which is especially visible for an even lattice such as A2.
    """
    _sign, gram = _positive_gram(lattice)
    rank = gram.tensor_shape()[0]
    ring = lattice.base_ring()
    rationals = ring.fraction_field()
    dual_gram = gram.change_ring(rationals).dual_tensor()
    coefficients = tuple(
        _owned_engine_element(rationals, SageQQ(entry)) for entry in inequality.A()
    )
    covector = tensor(rationals, (), (rank,), coefficients)
    direction = -(dual_gram * covector)
    gram_q = gram.change_ring(rationals)
    square = (gram_q * direction) * direction
    constant = _owned_engine_element(rationals, SageQQ(inequality.b()))
    scalar = rationals(2) * constant / square
    vector_coordinates = tuple(scalar * coordinate for coordinate in direction)
    assert all(coordinate in ring for coordinate in vector_coordinates), (
        f"the facet inequality {inequality} of the Voronoi cell of {lattice} gives the "
        f"coordinates {vector_coordinates}, which are not all in {ring}; a facet of the "
        f"Voronoi cell comes from a vector of the lattice"
    )
    return _element_from_coordinates(lattice, tuple(ring(coordinate) for coordinate in vector_coordinates))


def _voronoi_relevant_vectors(lattice):
    r"""Return the Voronoi-relevant vectors: the vectors whose inequalities are facets of the cell."""
    relevant = []
    for inequality in _voronoi_region(lattice).inequalities():
        candidate = _relevant_vector_of_inequality(lattice, inequality)
        if candidate is not None and candidate != lattice.zero() and candidate not in relevant:
            relevant.append(candidate)
    return finite_ordered_set(tuple(relevant))


def _voronoi_facets(lattice):
    r"""Return the facets of the Voronoi cell, indexed by their relevant vectors.

    The facet at the relevant vector ``v`` is the convex polytope on which
    ``b(x,v) = q(v)/2``; ``v`` and ``-v`` index opposite facets, and the
    stabilizer of the facet at ``v`` in ``O(L)`` is the point stabilizer of
    ``v``.
    """
    facets = {}
    for face in _voronoi_region(lattice).facets():
        inequalities = tuple(
            inequality
            for inequality in face.ambient_Hrepresentation()
            if inequality.is_inequality()
        )
        if len(inequalities) != 1:
            raise ArithmeticError(
                f"the facet {face} of the Voronoi cell of {lattice} lies on "
                f"{len(inequalities)} of the defining inequalities; a facet lies on "
                f"exactly one"
            )
        relevant_vector = _relevant_vector_of_inequality(lattice, inequalities[0])
        if relevant_vector is None or relevant_vector == lattice.zero():
            raise ArithmeticError(
                f"the facet {face} of the Voronoi cell of {lattice} gives the relevant "
                f"vector {relevant_vector}; a facet comes from a nonzero lattice vector"
            )
        facets[relevant_vector] = ConvexPolytopes(lattice)(
            face.as_polyhedron().vertices_list()
        )
    return finite_indexed_family(
        finite_ordered_set(tuple(facets)),
        lambda vector: facets[vector],
        name=f"Voronoi facets of {lattice}",
    )


def _successive_minima(lattice):
    r"""Return the family of exact successive lengths, as owned real numbers."""
    from sage.matrix.constructor import matrix as sage_matrix

    _sign, gram = _positive_gram(lattice)

    rank = gram.tensor_shape()[0]
    if rank == 0:
        return finite_family((), name="Successive minima")
    engine_gram = _engine_component_matrix(gram)
    ring = lattice.base_ring()
    # The columns of Sage's LLL_gram transformation are a reduced basis; the
    # largest of their squares bounds every successive minimum.
    reduced_basis = tuple(
        tensor.vector(ring, [_owned_engine_element(ring, entry) for entry in column])
        for column in engine_gram.LLL_gram().columns()
    )
    bound = max(_engine_element(ring, gram.contract(vector, vector)) for vector in reduced_basis)
    # PARI's qfminim returns the short vectors as the columns of its third entry.
    _count, _largest, coordinate_array = engine_gram.__pari__().qfminim(bound, None)
    coordinates = tuple(
        tensor.vector(
            ring,
            [
                _owned_engine_element(ring,
                    SageZZ(coordinate_array[row, column])
                )
                for row in range(rank)
            ],
        )
        for column in range(coordinate_array.ncols())
    )
    candidates = sorted(
        tuple(coordinates) + tuple(-column for column in coordinates),
        key=lambda column: (
            int(gram.contract(column, column)),
            tuple(int(entry) for entry in column),
        ),
    )
    independent = []
    for column in candidates:
        trial = independent + [column]
        backend_rows = sage_matrix(
            SageZZ,
            len(trial),
            rank,
            [
                _engine_element(ring, coefficient)
                for row in trial
                for coefficient in row
            ],
        )
        if backend_rows.rank() > len(independent):
            independent.append(column)
            if len(independent) == rank:
                break
    if len(independent) != rank:
        raise RuntimeError(
            f"the successive minima of {lattice} were computed wrongly: the vectors of "
            f"square at most {bound} span a space of dimension {len(independent)}, not "
            f"{rank}, but they contain an LLL-reduced basis"
        )

    return finite_family(
        tuple(
            RR(_engine_element(ring, gram.contract(column, column))).sqrt()
            for column in independent
        ),
        name="Successive minima",
    )


def _gaussian_heuristic(lattice, *, exact_form=False):
    r"""Return the Gaussian-heuristic shortest-vector radius of ``lattice``.

    The radius ``r`` is defined by ``vol(B_n(r)) = covol(lattice)``.  For a
    Gram matrix ``G`` this is

    ``r = (sqrt(abs(det(G))) / V_n)^(1/n)``,

    where ``V_n = pi^(n/2) / Gamma(n/2 + 1)`` is the volume of the Euclidean
    unit ball.  ``exact_form=True`` keeps this symbolic expression; otherwise
    the result is returned in the owned real field.
    """
    from sage.functions.gamma import gamma
    from sage.symbolic.constants import pi
    from sage.symbolic.ring import SR

    _definite_sign(lattice)
    rank = int(lattice.module_rank())
    if rank == 0:
        raise ValueError(
            f"{lattice} has no Gaussian-heuristic radius: it has rank 0, and the "
            f"radius is defined only for positive rank"
        )
    ring = lattice.base_ring()
    covolume = SR(_engine_element(ring, abs(lattice.determinant()))).sqrt()
    dimension = SageQQ(rank)
    unit_ball_volume = pi ** (dimension / 2) / gamma(dimension / 2 + 1)
    expression = (covolume / unit_ball_volume) ** (SageQQ.one() / rank)
    if exact_form:
        return expression
    return _owned_real_from_engine_expression(expression)


def _hadamard_ratio(lattice):
    from sage.misc.misc_c import prod
    from sage.symbolic.ring import SR

    _sign, gram = _positive_gram(lattice)
    rank = int(gram.tensor_shape()[0])
    if rank == 0:
        raise ValueError(
            f"{lattice} has no Hadamard ratio: it has rank 0, and the ratio is defined "
            f"only for positive rank"
        )
    ring = lattice.base_ring()
    product_of_norms = prod(
        SR(_engine_element(ring, gram[index, index])).sqrt()
        for index in range(rank)
    )
    determinant = abs(lattice.determinant())
    expression = (
        SR(_engine_element(ring, determinant)).sqrt() / product_of_norms
    ) ** (SageQQ.one() / rank)
    return RR(expression)


def _contact_polytope(lattice):
    from sage.geometry.polyhedron.constructor import Polyhedron

    rationals = lattice.base_ring().fraction_field()
    vertices = [
        [
            _engine_element(rationals, rationals(coordinate))
            for coordinate in _coordinate_tuple(lattice, vector)
        ]
        for vector in lattice.shortest_vectors()
    ]
    return ConvexPolytopes(lattice)(vertices)


def _coordinate_tuple(lattice, element):

    coordinates = lattice(element).to_vector()
    return tuple(coordinates(label) for label in lattice.module_generating_set())


def _covering_radius(lattice):

    _sign, gram = _positive_gram(lattice)
    rationals = lattice.base_ring().fraction_field()
    gram_q = gram.change_ring(rationals)
    squared = max(
        gram_q.contract(
            tensor.vector(
                rationals,
                [
                    _owned_engine_element(rationals, SageQQ(coordinate))
                    for coordinate in vertex
                ],
            ),
            tensor.vector(
                rationals,
                [
                    _owned_engine_element(rationals, SageQQ(coordinate))
                    for coordinate in vertex
                ],
            ),
        )
        for vertex in _voronoi_region(lattice).vertices_list()
    )
    return RR(_engine_element(rationals, squared)).sqrt()


def _center_density(lattice):

    _sign, gram = _positive_gram(lattice)
    rank = int(gram.tensor_shape()[0])
    if rank == 0:
        raise ValueError(
            f"{lattice} has no center density: it has rank 0, and the sphere packing "
            f"density is defined only for positive rank"
        )
    determinant_length = RR(
        _engine_element(lattice.base_ring(), abs(lattice.determinant()))
    ).sqrt()
    return lattice.packing_radius() ** rank / determinant_length


def _packing_density(lattice):
    from sage.functions.gamma import gamma
    from sage.symbolic.constants import pi

    rank = int(lattice.module_rank())
    factor = pi ** (SageQQ(rank) / 2) / gamma(1 + SageQQ(rank) / 2)
    return _owned_real_from_engine_expression(factor) * lattice.center_density()


def _theta_series(lattice, precision=20, variable="q"):
    from sage.quadratic_forms.quadratic_form import QuadraticForm

    _sign, positive_gram = _positive_gram(lattice)
    quadratic_form = QuadraticForm(
        SageZZ,
        2 * _engine_component_matrix(positive_gram),
    )
    backend_series = quadratic_form.theta_series(
        int(precision), var_str=variable
    )
    series_ring = lattice.base_ring().power_series_ring(variable)
    engine = _engine_ring(series_ring)
    return _owned_engine_element(series_ring, engine(backend_series))


def _hermite_invariant(lattice):

    sign, _positive_gram_tensor = _positive_gram(lattice)
    rank = int(lattice.module_rank())
    ring = lattice.base_ring()
    metric_minimum = _engine_element(ring, sign * lattice.minimum())
    determinant = _engine_element(ring, abs(lattice.determinant()))
    from sage.symbolic.ring import SR

    value = SR(metric_minimum) / SR(determinant) ** (SageQQ.one() / rank)
    return _owned_real_from_engine_expression(value)


def _packing_radius(lattice):

    sign = _definite_sign(lattice)
    metric_minimum = sign * lattice.minimum()
    return RR(_engine_element(lattice.base_ring(), metric_minimum)).sqrt() / 2


def _kissing_number(lattice):
    return lattice.base_ring()(len(lattice.shortest_vectors()))


__all__ = [
    "LatticeReduction",
]


def _first_unrepresented_value(lattice, classes, max_value, predicate):
    r"""Answer ``False`` at the least value a lattice of ``classes`` represents and ``lattice`` does not.

    ``classes`` holds more than the class of ``lattice``; the callers answer
    ``True`` for a genus or spinor genus of one class.

    The value \(n\) is represented by a definite lattice exactly when the
    coefficient of \(q^{|n|}\) in its theta series is nonzero.  The search
    reads the theta series to a precision that doubles from 64.  Without
    ``max_value`` it does not stop while no such value appears; a search
    that reaches ``max_value`` answers the proposition ``predicate``.
    """
    from sage_extensions.logic import AtomicProposition

    precision = 64
    while True:
        searched = precision if max_value is None else min(precision, int(max_value))
        own = lattice.theta_series(precision=searched + 1)
        others = tuple(other.theta_series(precision=searched + 1) for other in classes)
        found = next(
            (value for value in range(1, searched + 1) if own[value] == 0 and any(series[value] != 0 for series in others)),
            None,
        )
        match found, max_value is not None and searched >= int(max_value):
            case None, True:
                return AtomicProposition(predicate, lattice)
            case None, False:
                precision *= 2
            case _:
                return False
