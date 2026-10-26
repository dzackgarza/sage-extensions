r"""Owned tensor modules and finite coordinate tensor constructors.

The general constructor is ``tensor(R, ps, qs, data)``.  ``ps`` is the tuple
of dimensions of the contravariant indices and ``qs`` the tuple of dimensions
of the covariant indices.  Thus the component array has shape ``ps + qs``.

Every variance pattern is an element of its own tensor module over the owned
ring, so variance is carried by the object rather than inferred from storage.
A vector ``tensor(R, (n,), (), data)`` and a covector ``tensor(R, (), (n,),
data)`` are different objects with different parents, and a linear map
``tensor(R, (p,), (q,), data)`` from ``R^q`` to ``R^p`` is distinct from an
all-upper or all-lower two-index tensor.

``tensor.vector(...)``, ``tensor.covector(...)`` and ``tensor.matrix(...)``
accept owned rings and explicit component data.  They do not reproduce Sage's
matrix namespace: matrices as linear maps belong to the owned Mor objects.

Every route ends in one construction: ``TensorModule(R, ps, qs)`` is the
object of ``Modules(R)`` built by that owner's entry from
the rank vector, and a tensor is an element of it built by the module's
element constructor from its row-major components.
"""

from fractions import Fraction
from functools import singledispatch
from math import prod

from sage.matrix.constructor import matrix as _sage_matrix
from sage.misc.cachefunc import cache_key, cached_function, cached_method
from sage.misc.latex import latex
from sage.modules.free_module_element import vector as _sage_vector
from sage.rings.infinity import Infinity
from sage.structure.element import ModuleElement
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.modules.graded_direct_sums import (
    GradedDirectSumElement,
    _FramedDirectSumOfModules,
    _direct_sum_of_modules,
)
from sage_extensions.categories.modules.pure.modules import (
    MatrixSpaces,
    Modules,
)
from sage_extensions.categories.modules.pure.modules import (
    _engine_matrix as _engine_module_matrix,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
    SageRings,
    _engine_element,
    _engine_numeral,
    _engine_ring,
    _linear_algebra_ring,
    _linear_algebra_element,
    _own_ring,
)
from sage_extensions.categories.sets.cardinals import Cardinalities, cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import NN, Sets
from sage_extensions.owned_category import _object_of
from sage_extensions.static_types import ProductOfNaturalNumbers

_Rings = OwnedRings()
_SageRings = SageRings()
# Every tensor type is a point of this one fixed codomain.  Construct it once
# with the tensor vocabulary, rather than at the first tensor operation.
_TENSOR_TYPES = NN**2


def index_rank_family(ranks):
    r"""Return the family \(i\mapsto\) rank of slot \(i\), for \(i\in\Delta[k-1]\)."""

    entries = tuple(cardinal(rank) for rank in ranks)
    return indexed_family(
        Sets.Δ[len(entries) - 1],
        lambda index: entries[int(index)],
        name=f"Index ranks ({', '.join(str(entry) for entry in entries)})",
    )


def _owned_object_pair(first, second):
    r"""Return two mathematical objects as an object of ``Objects x Objects``."""
    from sage_extensions.categories.abstract_categories.cat import Cat
    from sage_extensions.categories.abstract_categories.objects import Objects

    return Cat().product((Objects(), Objects()))(first, second)


def _tensor_richcmp(left, right, op):
    r"""Implement only the mathematical equality relation on tensors.

    Tensor spaces carry no selected order.  The former componentwise Python
    tuple ordering was therefore a storage shadow, not a tensor operation.
    Arbitrary-operand recognition lives in :meth:`Tensor.__eq__`, the declared
    equality boundary.
    """
    match op:
        case _ if op == op_EQ:
            return Tensor.__eq__(left, right)
        case _ if op == op_NE:
            return not Tensor.__eq__(left, right)
        case _:
            return NotImplemented

_BLACKBOARD_RING_NAMES = {
    "Z": "ZZ",
    "Q": "QQ",
    "R": "RR",
    "C": "CC",
    "N": "NN",
}


def _ring_session_and_latex(ring) -> tuple[str, str]:
    r"""Session name and blackboard latex for a ring."""
    raw = str(latex(ring))
    prefix = r"\Bold{"
    if raw.startswith(prefix) and raw.endswith("}") and raw.count("{") == 1:
        letter = raw[len(prefix) : -1]
        name = _BLACKBOARD_RING_NAMES.get(letter)
        if name is not None:
            return name, rf"\mathbb{{{letter}}}"
    return str(ring), raw


def _free_module_session_and_latex(ring, rank) -> tuple[str, str]:
    r"""Session name and latex for the free module \(R^n\) or \(R^{\mathbb N}\)."""
    name, tex = _ring_session_and_latex(ring)
    if rank == Infinity:
        return f"{name}^NN", rf"{tex}^{{\mathbb{{N}}}}"
    return f"{name}^{rank}", rf"{tex}^{{{rank}}}"


def _otimes_session(factors: tuple[str, ...], unit: str) -> str:
    if not factors:
        return unit
    if len(factors) == 1:
        return factors[0]
    return " ⊗ ".join(factors)


def _otimes_latex(factors: tuple[str, ...], unit: str) -> str:
    if not factors:
        return unit
    if len(factors) == 1:
        return factors[0]
    return r" \otimes ".join(factors)


def _collapse_equal_power(factors: tuple[str, ...], *, latex_mode: bool) -> str | None:
    r"""Return a tensor power when every factor is the same; otherwise ``None``."""
    if not factors:
        return None
    first = factors[0]
    if any(factor != first for factor in factors[1:]):
        return None
    count = len(factors)
    if count == 1:
        return first
    if latex_mode:
        return rf"({first})^{{\otimes {count}}}"
    return f"({first})^{{⊗{count}}}"


def _tensor_space_session_and_latex(
    ring, upper_ranks: tuple, lower_ranks: tuple
) -> tuple[str, str]:
    r"""Name the module of type-\((p,q)\) tensors with these index ranks.

    On \(M=R^n\) this is \(M^{\otimes p}\otimes(M^*)^{\otimes q}\).  At
    infinite rank a type-\((0,q)\) tensor lives in
    \((M^{\otimes q})^*\), which is not \((M^*)^{\otimes q}\).
    """
    ring_name, ring_tex = _ring_session_and_latex(ring)
    upper_session = tuple(
        _free_module_session_and_latex(ring, rank)[0] for rank in upper_ranks
    )
    lower_session = tuple(
        _free_module_session_and_latex(ring, rank)[0] for rank in lower_ranks
    )
    upper_tex = tuple(
        _free_module_session_and_latex(ring, rank)[1] for rank in upper_ranks
    )
    lower_tex = tuple(
        _free_module_session_and_latex(ring, rank)[1] for rank in lower_ranks
    )
    dual_session = tuple(f"({name})*" for name in lower_session)
    dual_tex = tuple(rf"({name})^{{*}}" for name in lower_tex)
    infinite = Infinity in upper_ranks + lower_ranks
    if infinite:
        domain_session = _otimes_session(lower_session, ring_name)
        domain_tex = _otimes_latex(lower_tex, ring_tex)
        if not upper_ranks:
            return (
                f"({domain_session})*",
                rf"({domain_tex})^{{*}}",
            )
        if not lower_ranks:
            return (
                _otimes_session(upper_session, ring_name),
                _otimes_latex(upper_tex, ring_tex),
            )
        codomain_session = _otimes_session(upper_session, ring_name)
        codomain_tex = _otimes_latex(upper_tex, ring_tex)
        return (
            f"Mor({domain_session}, {codomain_session})",
            rf"\operatorname{{Hom}}({domain_tex}, {codomain_tex})",
        )

    def finite_factor(factors, latex_mode):
        if not factors:
            return None
        collapsed = _collapse_equal_power(factors, latex_mode=latex_mode)
        if collapsed is not None:
            return collapsed
        if latex_mode:
            return _otimes_latex(factors, ring_tex)
        return _otimes_session(factors, ring_name)

    session_factors = tuple(
        factor
        for factor in (
            finite_factor(upper_session, False),
            finite_factor(dual_session, False),
        )
        if factor is not None
    )
    tex_factors = tuple(
        factor
        for factor in (
            finite_factor(upper_tex, True),
            finite_factor(dual_tex, True),
        )
        if factor is not None
    )
    if not session_factors:
        return ring_name, ring_tex
    return (
        _otimes_session(session_factors, ring_name),
        _otimes_latex(tex_factors, ring_tex),
    )


class Tensor:
    r"""A tensor of type $(p,q)$.

    A type-$(p,q)$ tensor on a module \(M\) is an element of
    \(M^{\otimes p}\otimes(M^*)^{\otimes q}\).  When the index modules
    differ, it is an element of the corresponding mixed tensor product.
    At infinite rank a type-$(0,2)$ pairing lives in
    \((M\otimes M)^*\), not in \((M^*)^{\otimes 2}\).

    This class carries no storage.  Every tensor, of every valence, is an
    element of a :func:`TensorModule` over the owned base ring, and its
    type and index ranks are those of that module: the parent is the tensor
    space, so the element states neither again.
    """

    __slots__ = ()

    def _index_ranks(self) -> tuple:
        r"""Return the index ranks of this tensor's module, contravariant slots first.

        Private plumbing for the slot families; the public view is
        :meth:`tensor_shape`.
        """
        return self.parent()._index_ranks()

    def tensor_shape(self):
        r"""Return the family assigning each index slot the rank of its module.

        The slots are indexed by \(\Delta[k-1]\) for order \(k\), and a rank
        is a cardinal, so this is a family and not a Python tuple: two slots
        of equal rank are two slots, which a set would collapse.
        """
        return index_rank_family(self._index_ranks())

    def _upper_index_ranks(self) -> tuple:
        r"""Return the dimensions of the contravariant indices, those of this tensor's module."""
        return self.parent()._upper_index_ranks()

    def _lower_index_ranks(self) -> tuple:
        r"""Return the dimensions of the covariant indices, those of this tensor's module."""
        return self.parent()._lower_index_ranks()

    def tensor_type(self) -> ProductOfNaturalNumbers:
        r"""Return $(p,q)$: $p$ contravariant indices and $q$ covariant indices.

        A vector is type $(1,0)$.  A matrix, as a linear map, is type
        $(1,1)$.  A Gram tensor is type $(0,2)$.
        """
        return self.tensor_valence()

    def tensor_valence(self) -> ProductOfNaturalNumbers:
        r"""Return the type $(p,q)$ of this tensor's module; synonym of :meth:`tensor_type`."""
        return self.parent().tensor_valence()

    def tensor_order(self):
        r"""Return the cardinal number of tensor indices."""
        return cardinal(len(self._index_ranks()))

    def curry_bilinear(self, left_module, right_dual):
        r"""Curry a finite bilinear tensor into ``left_module -> right_dual``.

        The selected generators of ``right_dual`` are the coordinate
        covectors dual to the second tensor slot.  Thus ``b`` sends a left
        generator ``e_i`` to the covector whose ``j`` coordinate is
        ``b(e_i,e_j)``.  Taking the transpose of the bilinear coordinate
        array is confined to this tensor boundary, not its consumers.
        """
        right_rank = right_dual.module_generating_set().cardinality()
        left_rank = left_module.module_generating_set().cardinality()
        bilinear_rows = _covariant_bilinear_coordinate_rows(
            self, left_rank, right_rank
        )
        return left_module.module_category().Mor(left_module, right_dual).from_rows(
            tuple(
                tuple(bilinear_rows[i][j] for i in range(int(left_rank)))
                for j in range(int(right_rank))
            )
        )

    def gram_graph(self):
        r"""Return the weighted graph presented by this type-``(0,2)`` Gram tensor."""
        from sage_extensions.categories.forms.gram_matrices import (
            _gram_tensor_graph,
        )

        return _gram_tensor_graph(self)

    def gram_connected_component_cuts(self):
        r"""Return cuts between consecutive connected Gram blocks."""
        from sage_extensions.categories.forms.gram_matrices import (
            _tensor_connected_component_cuts,
        )

        return _tensor_connected_component_cuts(self)

    def tensor_space(self):
        r"""Return the module of which this tensor is an element.

        For type $(p,q)$ on \(R^n\) this is
        \((R^n)^{\otimes p}\otimes((R^n)^*)^{\otimes q}\), which is the parent.
        """
        return self.parent()

    def contravariant_index_modules(self):
        r"""Return the family of contravariant index modules."""
        return self.tensor_space().contravariant_index_modules()

    def covariant_index_modules(self):
        r"""Return the family of covariant index modules."""
        return self.tensor_space().covariant_index_modules()

    def index_modules(self):
        r"""Return the contravariant/covariant module families as an object of ``Objects x Objects``."""
        return self.tensor_space().index_modules()

    def contravariant_index_generating_sets(self):
        r"""Return the selected generating sets of the contravariant index modules."""
        return self.tensor_space().contravariant_index_generating_sets()

    def covariant_index_generating_sets(self):
        r"""Return the selected generating sets of the covariant index modules."""
        return self.tensor_space().covariant_index_generating_sets()

    def tensor_indices(self):
        r"""Return the two variance-indexed generating-set families as an object of ``Objects x Objects``."""
        return self.tensor_space().tensor_indices()

    def _component_array(self):
        r"""Private finite rectangular component array for tensor-owner computations."""
        shape = self._index_ranks()
        if Infinity in shape:
            raise ValueError(
                f"cannot list the components of this type-{self.tensor_valence()} tensor: "
                f"its index ranks {shape} include an infinite rank, so it has no finite "
                f"component array"
            )
        from itertools import product as cartesian_product

        entries = tuple(
            self[position]
            for position in cartesian_product(*(range(rank) for rank in shape))
        )
        return _nested(entries, shape)

    def _flat_components(self):
        r"""Private flattened finite components in tensor-index order."""
        shape = self._index_ranks()
        if Infinity in shape:
            raise ValueError(
                f"cannot list the components of this type-{self.tensor_valence()} tensor: "
                f"its index ranks {shape} include an infinite rank, so it has no finite "
                f"component list"
            )
        from itertools import product as cartesian_product

        return tuple(
            self[position]
            for position in cartesian_product(*(range(rank) for rank in shape))
        )

    def _tensor_hash(self) -> int:
        r"""Hash the data equality compares: variance, ranks, components.

        Equal tensors hash equally, so a tensor may key a cache and may be
        a constructor argument of a unique representation.  At infinite
        rank there is no component list and equality is identity, so the
        identity hash is the honest one.
        """
        if Infinity in self._index_ranks():
            return object.__hash__(self)
        return hash(
            (self.tensor_valence(), self._index_ranks(), tuple(self._flat_components()))
        )

    def _cache_key(self):
        r"""Key a finite presentation even when its scalars are unhashable.

        Sage's cache protocol recursively uses the scalar presentation
        keys. It does not give the tensor a mathematical hash, decide
        scalar equality, or identify distinct Cauchy presentations.
        Infinite tensors already use identity equality and hashing.
        """
        if Infinity in self._index_ranks():
            return self
        return cache_key((
            self.parent(), self.tensor_valence(), self._index_ranks(),
            self._flat_components(),
        ))

    def __eq__(self, other) -> bool:
        r"""Whether ``other`` is the same mathematical tensor.

        This is the arbitrary-operand equality boundary.  Tensor
        implementations may use different storage parents, so equality
        compares variance, slot ranks, coefficient ring, and components rather
        than concrete parent identity.
        """
        if not isinstance(other, Tensor):
            return False
        if self.tensor_valence() != other.tensor_valence():
            return False
        if self.tensor_shape() != other.tensor_shape():
            return False
        if _engine_ring(self.base_ring()) != _engine_ring(other.base_ring()):
            return False
        if Infinity in self._index_ranks():
            return self is other
        return all(
            left == right
            for left, right in zip(self._flat_components(), other._flat_components(), strict=True)
        )

    def __ne__(self, other) -> bool:
        return not Tensor.__eq__(self, other)

    def is_equal_tensor(self, other: "Tensor") -> bool:
        r"""Return whether the tensor ``other`` is the same tensor mathematically.

        This deliberately ignores the concrete storage parent.  Tensor spaces
        built from equal owned/engine ring facades can have distinct Sage
        parents while representing the same variance, ranks, and components.
        """
        return Tensor.__eq__(self, other)

    def change_ring(self, ring):
        r"""Change coefficients without changing tensor variance."""
        return tensor(
            ring,
            self._upper_index_ranks(),
            self._lower_index_ranks(),
            self._component_array(),
        )

    def is_symmetric(self) -> bool:
        r"""Return whether a square two-index tensor is symmetric in its slots."""
        if self.tensor_order() != 2:
            raise TypeError(
                f"is_symmetric asks whether T(x, y) = T(y, x), which needs a tensor with "
                f"exactly two indices; this is a type-{self.tensor_valence()} tensor with "
                f"{self.tensor_order()} indices"
            )
        first_rank, second_rank = self._index_ranks()
        if first_rank != second_rank:
            return False
        return all(
            self[i, j] == self[j, i]
            for i in range(first_rank)
            for j in range(second_rank)
        )

    def _partial_contract(self, other, slot=0, other_slot=0):
        r"""Contract upper ``slot`` of ``self`` with lower ``other_slot`` of ``other``."""
        if not _is_coordinate_tensor(other, self.base_ring()):
            raise TypeError(
                f"cannot contract a tensor over {self.base_ring()} with {other!r}: "
                f"contraction pairs two tensors over the same base ring {self.base_ring()}"
            )
        upper = self._upper_index_ranks()
        lower = self._lower_index_ranks()
        other_upper = other._upper_index_ranks()
        other_lower = other._lower_index_ranks()
        slot = int(slot)
        other_slot = int(other_slot)
        if slot < 0 or slot >= len(upper):
            raise IndexError(
                f"cannot contract upper slot {slot}: the left tensor has type "
                f"{self.tensor_valence()}, so its upper slots are 0..{len(upper) - 1}"
            )
        if other_slot < 0 or other_slot >= len(other_lower):
            raise IndexError(
                f"cannot contract lower slot {other_slot}: the right tensor has type "
                f"{other.tensor_valence()}, so its lower slots are 0..{len(other_lower) - 1}"
            )
        if upper[slot] != other_lower[other_slot]:
            raise ValueError(
                f"cannot contract upper slot {slot} of rank {upper[slot]} with lower slot "
                f"{other_slot} of rank {other_lower[other_slot]}: a contraction pairs a "
                f"module with its dual, so the two slots must have equal rank"
            )
        assert Infinity not in self._index_ranks() + other._index_ranks(), (
            f"cannot contract tensors with index ranks {self._index_ranks()} and "
            f"{other._index_ranks()}: contraction is computed here only when every "
            f"index module has finite rank"
        )

        from itertools import product as cartesian_product

        result_upper = upper[:slot] + upper[slot + 1 :] + other_upper
        result_lower = lower + other_lower[:other_slot] + other_lower[other_slot + 1 :]
        entries = {}
        self_positions = cartesian_product(*(range(rank) for rank in self._index_ranks()))
        other_positions = tuple(
            cartesian_product(*(range(rank) for rank in other._index_ranks()))
        )
        for left_index in self_positions:
            left_value = self[left_index]
            if not left_value:
                continue
            left_upper = left_index[: len(upper)]
            left_lower = left_index[len(upper) :]
            contracted = left_upper[slot]
            for right_index in other_positions:
                right_upper = right_index[: len(other_upper)]
                right_lower = right_index[len(other_upper) :]
                if contracted != right_lower[other_slot]:
                    continue
                right_value = other[right_index]
                if not right_value:
                    continue
                result_index = (
                    left_upper[:slot]
                    + left_upper[slot + 1 :]
                    + right_upper
                    + left_lower
                    + right_lower[:other_slot]
                    + right_lower[other_slot + 1 :]
                )
                entries[result_index] = entries.get(
                    result_index, self.base_ring().zero()
                ) + left_value * right_value

        if not result_upper and not result_lower:
            return entries.get((), self.base_ring().zero())
        shape = result_upper + result_lower
        values = tuple(
            entries.get(index, self.base_ring().zero())
            for index in cartesian_product(*(range(rank) for rank in shape))
        )
        return tensor(
            self.base_ring(),
            result_upper,
            result_lower,
            _nested(values, shape),
        )

    def contract(self, *vectors, slot=0, other_slot=0):
        r"""Contract represented tensor slots or fully evaluate a covariant tensor.

        When this tensor has an upper slot, ``contract(other, slot=i,
        other_slot=j)`` pairs that upper slot with lower slot ``j`` of
        ``other``.  The result has type ``(p-1+p', q+q'-1)``.  When this tensor
        is purely covariant, the historical evaluation spelling is retained:
        ``contract(v_1,...,v_q)`` fully evaluates it on contravariant vectors.
        """
        if self._upper_index_ranks():
            if len(vectors) != 1:
                raise TypeError(
                    f"this type-{self.tensor_valence()} tensor has an upper index, so "
                    f"contract pairs it with exactly one other tensor; got {len(vectors)} "
                    f"arguments"
                )
            return self._partial_contract(vectors[0], slot=slot, other_slot=other_slot)
        if int(slot) != 0 or int(other_slot) != 0:
            raise TypeError(
                f"this type-{self.tensor_valence()} tensor has no upper index, so contract "
                f"evaluates it on vectors and takes no slot selectors; got slot={slot}, "
                f"other_slot={other_slot}"
            )
        if len(vectors) != len(self._lower_index_ranks()):
            raise TypeError(
                f"a type-{self.tensor_valence()} tensor takes "
                f"{len(self._lower_index_ranks())} vector arguments, got {len(vectors)}"
            )
        for rank, vector in zip(self._lower_index_ranks(), vectors, strict=True):
            slot_module = TensorModule(self.base_ring(), (rank,), ())
            if vector not in slot_module:
                raise TypeError(
                    f"covariant tensor contraction takes, in a slot of rank {rank}, "
                    f"a vector of {slot_module}"
                )
        # The ubiquitous pairing G(x, y) = x^t G y is evaluated here, at the
        # tensor owner.  Reading its exact components directly avoids loading
        # a numerical array stack merely to contract a small exact tensor.
        if len(vectors) == 2:
            left, right = vectors
            left_rank, right_rank = self._lower_index_ranks()
            if Infinity in (left_rank, right_rank):
                raise ValueError(
                    f"cannot contract a type-{self.tensor_valence()} tensor with an infinite-rank index by finite component enumeration"
                )
            return sum(
                (
                    left[left_index]
                    * self[left_index, right_index]
                    * right[right_index]
                    for left_index in range(left_rank)
                    for right_index in range(right_rank)
                ),
                start=self.base_ring().zero(),
            )
        from itertools import product as cartesian_product

        return sum(
            (
                self[position]
                * prod(
                    (
                        vector[index]
                        for vector, index in zip(vectors, position, strict=True)
                    ),
                    start=self.base_ring().one(),
                )
                for position in cartesian_product(*(range(rank) for rank in self._lower_index_ranks()))
            ),
            self.base_ring().zero(),
        )

    def trace(self, slot=0, other_slot=0):
        r"""Contract one upper and one lower slot of this tensor."""
        upper = self._upper_index_ranks()
        lower = self._lower_index_ranks()
        slot = int(slot)
        other_slot = int(other_slot)
        if slot < 0 or slot >= len(upper) or other_slot < 0 or other_slot >= len(lower):
            raise IndexError(
                f"cannot trace upper slot {slot} against lower slot {other_slot}: this "
                f"tensor has type {self.tensor_valence()}, with {len(upper)} upper and "
                f"{len(lower)} lower slots"
            )
        if upper[slot] != lower[other_slot]:
            raise ValueError(
                f"cannot trace upper slot {slot} of rank {upper[slot]} against lower slot "
                f"{other_slot} of rank {lower[other_slot]}: a trace pairs a module with "
                f"its dual, so the two slots must have equal rank"
            )
        assert Infinity not in self._index_ranks(), (
            f"cannot trace a tensor with index ranks {self._index_ranks()}: the trace "
            f"is computed here only when every index module has finite rank"
        )

        from itertools import product as cartesian_product

        result_upper = upper[:slot] + upper[slot + 1 :]
        result_lower = lower[:other_slot] + lower[other_slot + 1 :]
        entries = {}
        for index in cartesian_product(*(range(rank) for rank in self._index_ranks())):
            upper_index = index[: len(upper)]
            lower_index = index[len(upper) :]
            if upper_index[slot] != lower_index[other_slot]:
                continue
            result_index = (
                upper_index[:slot]
                + upper_index[slot + 1 :]
                + lower_index[:other_slot]
                + lower_index[other_slot + 1 :]
            )
            entries[result_index] = entries.get(
                result_index, self.base_ring().zero()
            ) + self[index]

        if not result_upper and not result_lower:
            return entries.get((), self.base_ring().zero())
        shape = result_upper + result_lower
        values = tuple(
            entries.get(index, self.base_ring().zero())
            for index in cartesian_product(*(range(rank) for rank in shape))
        )
        return tensor(
            self.base_ring(),
            result_upper,
            result_lower,
            _nested(values, shape),
        )

    def tensor_product(self, other):
        r"""Return the outer tensor product, preserving upper/lower slot order."""
        if not _is_coordinate_tensor(other, self.base_ring()):
            raise TypeError(
                f"cannot form the tensor product of a tensor over {self.base_ring()} with "
                f"{other!r}: both factors must be tensors over {self.base_ring()}"
            )
        assert Infinity not in self._index_ranks() + other._index_ranks(), (
            f"cannot form the tensor product of tensors with index ranks "
            f"{self._index_ranks()} and {other._index_ranks()}: it is computed here only "
            f"when every index module has finite rank"
        )

        from itertools import product as cartesian_product

        upper = self._upper_index_ranks()
        lower = self._lower_index_ranks()
        other_upper = other._upper_index_ranks()
        other_lower = other._lower_index_ranks()
        result_upper = upper + other_upper
        result_lower = lower + other_lower
        entries = {}
        left_positions = cartesian_product(*(range(rank) for rank in self._index_ranks()))
        right_positions = tuple(
            cartesian_product(*(range(rank) for rank in other._index_ranks()))
        )
        for left_index in left_positions:
            left_upper = left_index[: len(upper)]
            left_lower = left_index[len(upper) :]
            left_value = self[left_index]
            if not left_value:
                continue
            for right_index in right_positions:
                right_value = other[right_index]
                if not right_value:
                    continue
                right_upper = right_index[: len(other_upper)]
                right_lower = right_index[len(other_upper) :]
                result_index = left_upper + right_upper + left_lower + right_lower
                entries[result_index] = entries.get(
                    result_index, self.base_ring().zero()
                ) + left_value * right_value

        shape = result_upper + result_lower
        if not shape:
            return entries.get((), self.base_ring().zero())
        values = tuple(
            entries.get(index, self.base_ring().zero())
            for index in cartesian_product(*(range(rank) for rank in shape))
        )
        return tensor(
            self.base_ring(),
            result_upper,
            result_lower,
            _nested(values, shape),
        )

    def raise_index(self, formed_module, slot=0):
        r"""Raise one lower index with the inverse Gram tensor of ``formed_module``.

        The selected lower slot must have the rank of the supplied formed
        module.  Over an integral base this requires the inverse Gram entries
        to remain integral; no automatic scalar extension is performed.
        """
        lower = self._lower_index_ranks()
        upper = self._upper_index_ranks()
        slot = int(slot)
        if slot < 0 or slot >= len(lower):
            raise IndexError(
                f"cannot raise lower slot {slot}: this tensor has type "
                f"{self.tensor_valence()}, with {len(lower)} lower slots"
            )
        if _engine_ring(formed_module.base_ring()) != _engine_ring(self.base_ring()):
            raise TypeError(
                f"cannot raise an index of a tensor over {self.base_ring()} with the form "
                f"of {formed_module}, which is over {formed_module.base_ring()}: both must "
                f"be over the same base ring"
            )
        rank = int(formed_module.module_rank())
        if lower[slot] != rank:
            raise ValueError(
                f"cannot raise lower slot {slot} of rank {lower[slot]} with the form of "
                f"{formed_module}, which has rank {rank}: the slot and the form must have "
                f"equal rank"
            )
        assert Infinity not in self._index_ranks(), (
            f"cannot raise an index of a tensor with index ranks {self._index_ranks()}: "
            f"this is computed only when every index module has finite rank"
        )

        inverse = _engine_component_matrix(formed_module.gram_tensor()).inverse()
        ring = self.base_ring()
        # The inverse is computed over the engine's fraction field; the index
        # is raised over ``ring`` exactly when every entry lies in ``ring``.
        engine = _engine_ring(ring)
        if not all(entry in engine for entry in inverse.list()):
            raise ValueError(
                f"cannot raise an index over {ring} with the form of {formed_module}: the "
                f"inverse Gram matrix has entries outside {ring}, so the form is not "
                f"unimodular over {ring}"
            )
        coefficients = {
            (raised, contracted): _owned_engine_element(ring, inverse[raised, contracted])
            for raised in range(rank)
            for contracted in range(rank)
        }

        from itertools import product as cartesian_product

        result_upper = upper + (rank,)
        result_lower = lower[:slot] + lower[slot + 1 :]
        entries = {}
        for index in cartesian_product(*(range(index_rank) for index_rank in self._index_ranks())):
            value = self[index]
            if not value:
                continue
            upper_index = index[: len(upper)]
            lower_index = index[len(upper) :]
            contracted = lower_index[slot]
            remaining_lower = lower_index[:slot] + lower_index[slot + 1 :]
            for raised in range(rank):
                coefficient = coefficients[raised, contracted]
                if not coefficient:
                    continue
                result_index = upper_index + (raised,) + remaining_lower
                entries[result_index] = entries.get(
                    result_index, ring.zero()
                ) + coefficient * value

        shape = result_upper + result_lower
        values = tuple(
            entries.get(index, ring.zero())
            for index in cartesian_product(*(range(index_rank) for index_rank in shape))
        )
        return tensor(ring, result_upper, result_lower, _nested(values, shape))

    def lower_index(self, formed_module, slot=0):
        r"""Lower one upper index with the Gram tensor of ``formed_module``."""
        upper = self._upper_index_ranks()
        lower = self._lower_index_ranks()
        slot = int(slot)
        if slot < 0 or slot >= len(upper):
            raise IndexError(
                f"cannot lower upper slot {slot}: this tensor has type "
                f"{self.tensor_valence()}, with {len(upper)} upper slots"
            )
        if _engine_ring(formed_module.base_ring()) != _engine_ring(self.base_ring()):
            raise TypeError(
                f"cannot lower an index of a tensor over {self.base_ring()} with the form "
                f"of {formed_module}, which is over {formed_module.base_ring()}: both must "
                f"be over the same base ring"
            )
        rank = int(formed_module.module_rank())
        if upper[slot] != rank:
            raise ValueError(
                f"cannot lower upper slot {slot} of rank {upper[slot]} with the form of "
                f"{formed_module}, which has rank {rank}: the slot and the form must have "
                f"equal rank"
            )
        assert Infinity not in self._index_ranks(), (
            f"cannot lower an index of a tensor with index ranks {self._index_ranks()}: "
            f"this is computed only when every index module has finite rank"
        )

        gram = formed_module.gram_tensor()
        ring = self.base_ring()
        from itertools import product as cartesian_product

        result_upper = upper[:slot] + upper[slot + 1 :]
        result_lower = lower + (rank,)
        entries = {}
        for index in cartesian_product(*(range(index_rank) for index_rank in self._index_ranks())):
            value = self[index]
            if not value:
                continue
            upper_index = index[: len(upper)]
            lower_index = index[len(upper) :]
            contracted = upper_index[slot]
            remaining_upper = upper_index[:slot] + upper_index[slot + 1 :]
            for lowered in range(rank):
                coefficient = gram[lowered, contracted]
                if not coefficient:
                    continue
                result_index = remaining_upper + lower_index + (lowered,)
                entries[result_index] = entries.get(
                    result_index, ring.zero()
                ) + coefficient * value

        shape = result_upper + result_lower
        values = tuple(
            entries.get(index, ring.zero())
            for index in cartesian_product(*(range(index_rank) for index_rank in shape))
        )
        return tensor(ring, result_upper, result_lower, _nested(values, shape))

    def dual_tensor(self):
        r"""Dualize a nondegenerate pairing or copairing.

        For a nondegenerate pairing ``g`` of type ``(0,2)``, duality through
        its correlation isomorphism produces the inverse metric, the
        contravariant tensor ``g^{-1}`` of type ``(2,0)`` on the original
        module.  Equivalently, those same inverse components define the
        covariant dual pairing on the algebraic dual; :meth:`dual_pairing`
        returns that type-``(0,2)`` presentation.  Conversely a nondegenerate
        type-``(2,0)`` tensor dualizes to type ``(0,2)``.
        """
        valence = self.tensor_valence()
        first_rank, second_rank = self._index_ranks()
        if valence in {_TENSOR_TYPES((0, 2)), _TENSOR_TYPES((2, 0))}:
            if first_rank != second_rank:
                raise ValueError(
                    f"cannot dualize this type-{valence} tensor with index ranks "
                    f"({first_rank}, {second_rank}): a pairing M x M -> R needs both "
                    f"indices of equal rank"
                )
            inverse = _engine_component_matrix(self).inverse()
            ring = self.base_ring()
            components = [
                tuple(_owned_engine_element(ring, entry) for entry in row)
                for row in inverse.rows()
            ]
            if valence == _TENSOR_TYPES((0, 2)):
                return tensor(ring, (first_rank, second_rank), (), components)
            return tensor(ring, (), (first_rank, second_rank), components)
        raise TypeError(
            f"cannot dualize a type-{valence} tensor: dual_tensor is defined for a "
            f"nondegenerate pairing (type (0, 2)) or copairing (type (2, 0))"
        )

    def dual_pairing(self):
        r"""Return the covariant pairing induced on the algebraic dual.

        If ``g`` is a nondegenerate pairing on ``M``, then ``g^{-1}`` is a
        type-``(2,0)`` tensor on ``M``.  Via
        ``(M^*)^* \cong M`` its components are the Gram components of the
        induced pairing on ``M^*``; relative to the dual framing that pairing
        is again type ``(0,2)``.
        """
        valence = self.tensor_valence()
        match valence == _TENSOR_TYPES((0, 2)):
            case False:
                raise TypeError(
                    f"cannot form the dual pairing of a type-{valence} tensor: "
                    "a pairing on M must have type (0, 2)"
                )
            case True:
                inverse = self.dual_tensor()
                return tensor(
                    self.base_ring(),
                    (),
                    inverse._upper_index_ranks(),
                    inverse._component_array(),
                )

    def pullback(self, morphism, *slot_morphisms):
        r"""Pull this covariant tensor back along owned linear morphisms.

        For ``f: V -> W`` and ``T`` of type ``(0,q)`` on ``W``, return
        ``f^*T = T \circ (f \times \cdots \times f)`` on ``V``.  Given one
        morphism ``f_k: V_k -> W`` for each covariant slot, return
        ``T \circ (f_1 \times \cdots \times f_q)`` on
        ``V_1 \times \cdots \times V_q``.  For a form ``b`` on ``L`` and
        ``i: S -> L``, the pullback along ``(i, 1_L)`` is the pairing
        ``S \times L -> R``, ``(s, x) \mapsto b(i s, x)``.

        The public datum is the morphism.  Finite coordinate matrices are
        only an implementation of this transport: each endpoint module Mor
        must itself be the finite framed-free matrix Mor.  When ``f`` is
        linear over ``R`` and ``T`` has components in an ``R``-algebra ``S``,
        the pullback is along the base change ``f \otimes_R S``, whose matrix
        is that of ``f`` read in ``S``.
        """
        if self._upper_index_ranks():
            raise TypeError(
                f"cannot pull back a type-{self.tensor_valence()} tensor along "
                f"{morphism}: pullback f^*T is defined for a covariant tensor, type (0, q)"
            )
        given = tuple(
            self._pullback_matrix(f) for f in (morphism, *slot_morphisms)
        )
        q = len(self._lower_index_ranks())
        matrices = given * q if not slot_morphisms else given
        if len(matrices) != q:
            raise ValueError(
                f"cannot pull back a tensor with {q} covariant slots along "
                f"{len(matrices)} morphisms: give one morphism, or one per slot"
            )
        target_ranks = tuple(matrix.parent().matrix_shape()[0] for matrix in matrices)
        if target_ranks != self._lower_index_ranks():
            raise ValueError(
                f"cannot pull back a tensor with covariant index ranks "
                f"{self._lower_index_ranks()} along morphisms whose codomains have ranks "
                f"{target_ranks}: each covariant index must have its morphism's codomain rank"
            )
        if q == 0:
            return self
        ring = self.base_ring()
        source_ranks = tuple(matrix.parent().matrix_shape()[1] for matrix in matrices)

        # The ubiquitous bilinear case is exactly A_1^t G A_2.  Use the
        # selected exact matrix backend only inside this boundary and cross
        # every entry back before constructing the owned tensor.
        from sage_extensions.rings.real import RR

        if q == 2 and ring is not RR:
            left, right = (
                _engine_module_matrix(matrix).change_ring(_engine_ring(ring))
                for matrix in matrices
            )
            backend_pullback = left.transpose() * _engine_component_matrix(self) * right
            entries = tuple(
                _owned_engine_element(ring, entry) for entry in backend_pullback.list()
            )
            return tensor(ring, (), source_ranks, _nested(entries, source_ranks))

        from itertools import product as cartesian_product

        source_positions = cartesian_product(*(range(rank) for rank in source_ranks))
        target_positions = tuple(
            cartesian_product(*(range(rank) for rank in self._lower_index_ranks()))
        )
        entries = []
        for source_indices in source_positions:
            value = ring.zero()
            for target_indices in target_positions:
                coefficient = self[target_indices]
                for matrix, target_index, source_index in zip(
                    matrices, target_indices, source_indices, strict=True
                ):
                    coefficient *= ring(matrix[target_index, source_index])
                value += coefficient
            entries.append(value)
        return tensor(ring, (), source_ranks, _nested(tuple(entries), source_ranks))

    def _pullback_matrix(self, morphism):
        r"""Return the framed-free module Mor element of ``morphism`` for :meth:`pullback`."""
        if _is_coordinate_tensor(morphism, self.base_ring()):
            raise TypeError(
                f"cannot pull back along the tensor {morphism!r}: pullback takes a linear "
                f"map f: V -> W between free modules of finite rank with chosen bases, "
                f"not a tensor"
            )
        matrix = morphism._framed_coordinate_morphism()
        if matrix.parent() not in MatrixSpaces(matrix.parent().base_ring()):
            raise TypeError(
                f"cannot pull back a tensor along {morphism}: its domain and codomain must be "
                f"free modules of finite rank with a chosen basis, but the module maps between "
                f"them form {matrix.parent()}"
            )
        return matrix


def _covariant_bilinear_coordinate_rows(value, left_rank, right_rank):
    r"""Read a finite type-``(0,2)`` tensor as bilinear coordinate data.

    This is the tensor owner's boundary from a tensor presentation to the
    rectangular values used by the universal bilinear classifier.  Variance
    is part of the tensor datum: a copairing of type ``(2,0)`` is not accepted
    as a form merely because its component array is rectangular.
    """
    match isinstance(value, Tensor):
        case False:
            raise TypeError(f"{value!r} is not a tensor")
        case True:
            pass
    valence = value.tensor_valence()
    match valence == _TENSOR_TYPES((0, 2)):
        case False:
            raise TypeError(
                f"a bilinear form is a covariant 2-tensor of type (0, 2), "
                f"but {value!r} has type {valence}"
            )
        case True:
            shape = tuple(cardinal(rank) for rank in value.tensor_shape())
            left_rank = cardinal(left_rank)
            right_rank = cardinal(right_rank)
            match (
                all(rank.is_finite() for rank in shape),
                left_rank.is_finite(),
                right_rank.is_finite(),
            ):
                case (True, True, True):
                    rows, columns = map(int, shape)
                    expected = (int(left_rank), int(right_rank))
                    match (rows, columns) == expected:
                        case False:
                            raise ValueError(
                                f"the type-(0, 2) tensor has shape {(rows, columns)}, but "
                                f"this pairing needs shape {expected}"
                            )
                        case True:
                            return tuple(
                                tuple(
                                    value[row, column]
                                    for column in range(columns)
                                )
                                for row in range(rows)
                            )
                case _:
                    raise TypeError(
                        "a tensor supplies bilinear coordinate data only when its "
                        "two slots and the two selected module framings are finite"
                    )



@cached_function
def _engine_component_matrix(value):
    r"""Private engine adapter (`OWN-06`): the Sage matrix of a two-index tensor.

    The owned operation -- a signature, an inverse Gram tensor, a pullback, a
    display -- is selected by the caller, and this is the one crossing of a
    two-index tensor into Sage's matrix backend: the shared generic
    linear-algebra choice retains exact owned scalars when symbolic
    serialization would lose their relations or presentation. Other
    computation parents retain their ordinary engine conversion. The
    matrix it returns is engine data; callers cross results back into owned
    tensors before exposing them.
    """
    if value.tensor_order() != 2:
        raise TypeError(
            f"cannot write a type-{value.tensor_valence()} tensor as a matrix: a matrix "
            f"has exactly two indices, this tensor has {value.tensor_order()}"
        )
    rows, columns = value._index_ranks()
    if rows == Infinity or columns == Infinity:
        raise ValueError(
            f"cannot write a tensor with index ranks ({rows}, {columns}) as a matrix: "
            f"an index of infinite rank has no finite matrix"
        )
    rows, columns = int(rows), int(columns)
    ring = value.base_ring()
    return _sage_matrix(
        _linear_algebra_ring(ring),
        rows,
        columns,
        [_linear_algebra_element(ring, value[i, j]) for i in range(rows) for j in range(columns)],
    )


# Protected engine-adapter contract (OWN-05, OWN-06, OWN-24): the
# ``_engine_*`` row-action functions below are the one place where Sage's
# row-action convention and coordinate matrices are handled.  Owner: this
# tensor package.  Permitted callers: the group-realization adapters of the
# automorphism groups that lower an element to a row action and raise one
# back (``LatticeIsometryMor``, ``ModuleAutomorphismGroup`` and the module
# engine adapter ``_flag_stabilizer_engine_data``).  Inputs are owned
# morphisms or raw engine matrices produced by these functions; outputs are
# raw engine matrices that the caller raises immediately.  Mathematical
# code never receives them.


def _engine_flag_adapted_rows(spans, engine_ring):
    r"""Private engine adapter: coordinate rows of a basis adapted to a chain of row spans over a PID.

    ``spans`` lists coordinate-row bases of ``T_1 < ... < T_k < M``.  For the
    adapted rows ``A`` of ``T_(i-1)`` and a basis ``S`` of ``T_i``, write
    ``A = C S``; the Smith form ``U C V = D`` gives the basis ``V^-1 S`` of
    ``T_i`` whose first rows span ``T_(i-1)`` exactly when every diagonal
    entry of ``D`` is a unit, i.e. ``T_(i-1)`` is saturated in ``T_i``.
    Returns the adapted rows, the block sizes and the first step that is
    not saturated (``None`` when all are).
    """
    adapted = None
    sizes = []
    for step, span in enumerate(spans):
        rows = _sage_matrix(engine_ring, span)
        if adapted is None:
            adapted = rows
            sizes.append(rows.nrows())
            continue
        coefficients = rows.solve_left(adapted)
        diagonal, _left, right = coefficients.smith_form()
        if not all(diagonal[i, i].is_unit() for i in range(adapted.nrows())):
            return None, None, step
        rebased = right.inverse() * rows
        adapted = adapted.stack(rebased.matrix_from_rows(range(adapted.nrows(), rebased.nrows())))
        sizes.append(rebased.nrows() - sum(sizes))
    return adapted.rows(), tuple(size for size in sizes if size), None


def _engine_block_general_linear_row_actions(sizes, engine_ring):
    r"""Private engine adapter: Sage's generators of each ``GL(n_i, R)``, embedded block-diagonally as row actions."""
    from sage.groups.matrix_gps.linear import GL
    from sage.matrix.constructor import block_diagonal_matrix

    actions = []
    for index, size in enumerate(sizes):
        for generator in GL(size, engine_ring).gens():
            blocks = [_sage_matrix.identity(engine_ring, other) for other in sizes]
            blocks[index] = generator.matrix()
            actions.append(block_diagonal_matrix(blocks))
    return tuple(actions)


def _engine_row_action_matrix(morphism):
    r"""Private engine adapter (`OWN-06`, `OWN-24`): a morphism as Sage's row action.

    Publicly a linear map ``f: V -> W`` between finite framed-free modules acts
    on coordinate columns: column ``j`` of its matrix holds the coordinates of
    ``f(e_j)``.  Sage's matrix groups act on coordinate rows from the right, so
    this lowering converts the convention once, by one transpose.  Row ``i`` of
    the result is the coordinate row of ``f(e_i)``; raising reads it so.
    """
    matrix = morphism._framed_coordinate_morphism()
    assert matrix.parent() in MatrixSpaces(matrix.parent().base_ring()), (
        f"{morphism} has no matrix: its domain {morphism.domain()} and codomain "
        f"{morphism.codomain()} must be free modules of finite rank with a chosen basis, "
        f"but the module maps between them form {matrix.parent()}"
    )
    return _engine_module_matrix(matrix).transpose()


def _engine_column_matrix_from_row_action(row_action):
    r"""Private engine adapter (`OWN-06`, `OWN-24`): raise an engine row action to a column matrix.

    The inverse of :func:`_engine_row_action_matrix`.  An engine that acts on
    coordinate rows (Sage's matrix groups, OSCAR's isometries and embeddings)
    returns a matrix whose row ``i`` is the coordinate row of ``f(e_i)``.  The
    returned Sage matrix has column ``i`` holding those coordinates, the public
    convention, so its caller reads generator images from its columns.
    """
    return row_action.transpose()


def _engine_general_linear_two_word(row_action):
    r"""Private engine adapter (`OWN-05`, `OWN-06`, `OWN-24`): an element of ``GL_2(ZZ)`` as a word.

    Protected caller: ``ModuleAutomorphismGroup._general_linear_two_word``
    (``modules/module_morphisms/module_morphisms.py``), and
    :func:`_engine_general_linear_two_coset_permutations` here.  Input: the
    engine row action of an automorphism of a free rank-two ``ZZ``-module on
    its selected basis.  Output: a tuple of signed letters, ``1, 2, 3`` for
    ``s_2 = [[0,-1],[1,0]]``, ``s_3 = [[0,1],[-1,1]]``, ``e = diag(1,-1)`` and
    negative for inverses, whose product is the column matrix ``C``
    (``C(gh) = C(g) C(h)``).  ``C = e A`` with ``det A = 1`` when
    ``det C = -1``; ``A`` is written in ``l, r`` by Sage's
    ``sl2z_word_problem``, with ``l = s_3^-1 s_2^-1`` and ``r = s_3 s_2``.
    """
    return _engine_general_linear_two_column_word(_engine_column_matrix_from_row_action(row_action))


def _engine_general_linear_two_column_word(column):
    r"""The word of :func:`_engine_general_linear_two_word`, read from the column matrix ``C`` itself."""
    from sage.modular.arithgroup.arithgroup_perm import sl2z_word_problem
    from sage.modular.arithgroup.congroup_sl2z import SL2Z
    from sage.rings.integer_ring import ZZ as SageZZ

    reflection = _sage_matrix.diagonal(SageZZ, [1, -1])
    letters = ((-2, -1), (2, 1))

    def special(matrix):
        return tuple(
            letter
            for which, exponent in sl2z_word_problem(SL2Z(matrix))
            for letter in (
                letters[int(which)] * int(exponent)
                if int(exponent) >= 0
                else tuple(-step for step in reversed(letters[int(which)])) * -int(exponent)
            )
        )

    match column.det():
        case 1:
            return special(column)
        case -1:
            return (3, *special(reflection * column))
        case determinant:
            raise AssertionError(f"{column} has determinant {determinant}, not +-1")


def _engine_general_linear_two_coset_permutations(generator_row_actions, index):
    r"""Private engine adapter (`OWN-05`, `OWN-06`): Todd--Coxeter for a subgroup of ``GL_2(ZZ)``.

    Protected caller: ``ModuleAutomorphismGroup._finite_index_coset_permutations``.
    ``generator_row_actions`` are the engine row actions of generators of
    ``H``; ``index`` is the caller's stated finite index.  GAP's
    ``CosetTable`` enumerates the right cosets of ``H`` in the presentation
    of ``GL_2(ZZ)`` stated by A. Ram, *Advanced Discrete Math MAST90030
    notes* (10 August 2025), Section 16, Proposition 16.1(b), p. 128
    (https://math.soimeme.org/~arunram/Teaching/2025AdvDiscreteMath/250810Modulargroup.pdf,
    opened 2026-10-16), transcribed: generators ``omega_1 = [[0,1],[-1,0]]``,
    ``omega_2 = [[0,1],[-1,1]]``, ``e = [[1,0],[0,-1]]``, relations

        omega_1^2 in Z(GL_2(ZZ)),  omega_1^4 = 1,  omega_2^3 = omega_1^2,
        e^2 = 1,  e omega_1 e^-1 = omega_1^-1,  e omega_2 e^-1 = omega_1 omega_2^-1 omega_1^-1.

    Its proof (pp. 129--135) derives SL_2(ZZ) = Z/4 *_{Z/2} Z/6 on
    ``<omega_1>, <omega_2>`` from Serre, *Trees*, 4.2(c) and Theorem 6, and
    GL_2(ZZ) = SL_2(ZZ) and its coset by ``e``.  The same SL_2(ZZ)
    presentation, ``<R, S | S^4 = (RS)^3 = 1, S^2 (RS) = (RS) S^2>`` with
    ``R = [[1,1],[0,1]]``, ``S = [[0,1],[-1,0]] = omega_1`` and
    ``RS = omega_2^2``, is stated by Blanc--Deserti, *Embeddings of SL(2,Z)
    into the Cremona group*, arXiv:1103.0114v2, Section 2.1, p. 4, citing
    Newman, *Integral Matrices*, Ch. VIII.

    The adapter's letters are ``s_2 = [[0,-1],[1,0]] = omega_1^-1``,
    ``s_3 = omega_2`` and ``e``, the generators in which
    ``_engine_general_linear_two_word`` writes elements.  Substituting
    ``omega_1 = s_2^-1``, ``omega_2 = s_3`` (an invertible change of free
    generators) turns the relations above into the relators below, one for
    one: ``s_2^4``; ``s_3^3 s_2^2``; ``[s_2^2, s_3]`` and ``[s_2^2, e]`` (the
    centrality of ``omega_1^2``; its commutator with ``omega_1`` is trivial
    in the free group); ``e^2``; ``e s_2^-1 e^-1 s_2^-1``;
    ``e s_3 e^-1 s_2^-1 s_3 s_2``.  So the finitely presented group below is
    GL_2(ZZ), with ``s_2, s_3, e`` sent to their matrices.  Enumeration
    terminates exactly when the index is finite (TauCeti's
    ``CosetTable.index_le`` bounds the index by a table's size); the index
    assertion below compares GAP's count with the caller's stated index.
    Returns, for ``s_2, s_3, e``, the right action on the coset numbers
    ``0, ..., index - 1`` (``0`` is ``H``) as tuples.
    """
    from functools import reduce

    from sage.libs.gap.libgap import libgap

    free = libgap.FreeGroup(["s2", "s3", "e"])
    letters = free.GeneratorsOfGroup()

    def word(signed_letters, generators):
        return reduce(
            lambda product, letter: product * generators[abs(letter) - 1] ** (1 if letter > 0 else -1),
            signed_letters,
            generators[0] ** 0,
        )

    s2, s3, e = letters
    relators = [
        s2 ** 4,
        s3 ** 3 * s2 ** 2,
        s2 ** 2 * s3 * s2 ** -2 * s3 ** -1,
        s2 ** 2 * e * s2 ** -2 * e ** -1,
        e ** 2,
        e * s2 ** -1 * e ** -1 * s2 ** -1,
        e * s3 * e ** -1 * s2 ** -1 * s3 * s2,
    ]
    presented = free / relators
    presented_letters = presented.GeneratorsOfGroup()
    subgroup = presented.Subgroup(
        [word(_engine_general_linear_two_word(row_action), presented_letters) for row_action in generator_row_actions]
    )
    table = presented.CosetTable(subgroup)
    assert int(libgap.Length(table[0])) == int(index), (
        f"the subgroup was stated to have index {index} in GL_2(ZZ), but Todd--Coxeter enumeration "
        f"found {libgap.Length(table[0])} cosets"
    )
    # Row 2k of GAP's coset table is the right action of the k-th generator.
    return tuple(tuple(int(point) - 1 for point in table[2 * position]) for position in range(3))


def _engine_permutation_word_action(permutations, signed_letters, point):
    r"""Private engine adapter: the right action of a word on a point, from the generators' permutations.

    Protected caller: ``ModuleAutomorphismGroup.finite_index_left_cosets``.
    """
    from functools import reduce

    inverses = tuple(
        tuple(sorted(range(len(permutation)), key=permutation.__getitem__)) for permutation in permutations
    )
    return reduce(
        lambda current, letter: (permutations if letter > 0 else inverses)[abs(letter) - 1][current],
        signed_letters,
        point,
    )


def _engine_row_family_gram(gram, row_family):
    r"""Private engine adapter (`OWN-06`, `OWN-24`): the Gram matrix of a family given by coordinate rows.

    Sage's lattice reductions (Hermite transforms, ``p_adic_normal_form``)
    return a basis change ``B`` whose row ``i`` is the coordinate row of the
    ``i``-th new vector ``b_i``.  For the bilinear form ``b`` with Gram matrix
    ``G``, the Gram matrix of the family has entry ``(i, j)`` equal to
    ``b(b_i, b_j)``.  It is the pullback of ``G`` along ``e_i |-> b_i``,
    whose column matrix is ``B^t``, so it is ``B G B^t``.  This is the one
    site that names the side of a row family.
    """
    return row_family * gram * row_family.transpose()


def _engine_symmetrized_form_matrix(form):
    r"""Private backend matrix of ``b(x,y) + b(y,x)`` for a bilinear tensor.

    Symmetrization belongs to the two tensor slots; the returned Sage matrix
    is used only as a coordinate realization for exact rational diagonalization.
    """
    gram = _engine_component_matrix(form)
    return gram + gram.transpose()


def _engine_row_basis_positions(row_family):
    r"""Indices of a maximal independent subfamily of coordinate rows.

    Sage's pivot columns of the dual (transposed) family are precisely the
    positions of independent original rows, in the original ordering.
    """
    return row_family.transpose().pivots()


def _engine_dual_row_family(row_family):
    r"""Private engine adapter (`OWN-06`, `OWN-24`): the dual of a basis given by coordinate rows.

    For an invertible ``B`` whose row ``i`` is the coordinate row of a basis
    vector ``b_i``, return the matrix whose row ``i`` is the coordinate row of
    the dual basis vector ``b_i^*``, with ``b_i^* . b_j = delta_ij`` for the
    standard pairing: ``(B^{-1})^t``.  A family that reduces the inverse form,
    ``B G^{-1} B^t = D``, has a dual family that reduces the form itself:
    ``(B^{-1})^t`` gives ``D^{-1}`` as the Gram matrix of ``G``.
    """
    return row_family.inverse().transpose()


def _engine_modular_pairing_pullback(form, row_family, modulus, *, diagonal_only=False):
    r"""Private engine adapter (``OWN-24``): a finite-family pairing contraction.

    Let ``u: ZZ^r -> A`` send the standard basis to the chosen generators
    of a finite form module, and let ``c: I -> ZZ^r`` give chosen coordinate
    representatives of a finite family. The values being realized are
    ``b(u(c(i)), u(c(j)))``, the pullback of the quotient-valued pairing
    along this family, not a new pairing on the coordinates.

    ``form`` gives normalized integer representatives in
    ``[0, modulus)`` of the generator pairings, and each row of
    ``row_family`` has nonnegative integer coordinates. For
    ``diagonal_only``, its diagonal instead records the chosen quadratic
    generator values, with off-diagonal entries the bilinear cross terms;
    its result is ``q(u(c(i)))`` in ``QQ/2ZZ``, not the diagonal of the
    bilinear pairing in ``QQ/ZZ``.

    This is the private NumPy realization of a tensor contraction; no caller
    chooses where the family transpose belongs or how to contract indices.
    The fixed-width integer backend is used only when both sums of products
    fit in signed 64 bits *before* reduction; otherwise Python integers
    preserve exact arithmetic.
    """
    import numpy

    modulus = int(modulus)
    rank = form.shape[0]
    if rank == 0:
        count = row_family.shape[0]
        return numpy.zeros(count if diagonal_only else (count, count), dtype=numpy.int64)

    largest_coordinate = int(numpy.max(row_family))
    largest_form_entry = int(numpy.max(form))
    signed_int64_max = (1 << 63) - 1
    exact_int64 = (
        modulus <= signed_int64_max
        and rank * largest_coordinate * largest_form_entry <= signed_int64_max
        and rank * largest_coordinate * (modulus - 1) <= signed_int64_max
    )
    representation = numpy.int64 if exact_int64 else object
    coordinates = numpy.asarray(row_family, dtype=representation)
    gram = numpy.asarray(form, dtype=representation)
    first_contraction = (coordinates @ gram) % modulus
    if diagonal_only:
        return numpy.sum(first_contraction * coordinates, axis=1) % modulus
    return (first_contraction @ coordinates.transpose()) % modulus


def _engine_quotient_form_family_contractions(bilinear_form, quadratic_form, row_family):
    r"""Contract pulled-back quotient-valued forms over an engine family.

    Both inputs are owned forms on the same finite free module, obtained by
    mathematical pullback along the selected Smith-generator morphism.
    Only here are generator values lowered to rational representatives.
    The quadratic coefficient form uses q(e_i) on its diagonal and
    b(e_i,e_j) off the diagonal; it takes values modulo 2, not modulo 1.
    """
    import numpy
    from sage.arith.functions import lcm

    source = bilinear_form.module()
    if quadratic_form is not None and quadratic_form.module() is not source:
        raise TypeError("the forms must have the same source module")
    basis = tuple(source.module_generator(i) for i in source.module_generating_set())
    rank = len(basis)

    def lifted(value):
        scalar = value.lift()
        return _engine_element(scalar.parent(), scalar)

    bilinear = tuple(
        tuple(lifted(bilinear_form(x, y)) for y in basis) for x in basis
    )
    diagonal = (
        tuple(lifted(quadratic_form(x)) for x in basis)
        if quadratic_form is not None else None
    )
    self_gram = (
        tuple(tuple(diagonal[i] if i == j else bilinear[i][j]
                    for j in range(rank)) for i in range(rank))
        if diagonal is not None else bilinear
    )
    denominator = lcm([1, *(int(x.denominator()) for row in (*bilinear, *self_gram)
                            for x in row)])
    self_period = 2 if diagonal is not None else 1
    b_coefficients = numpy.asarray(
        [[int(x * denominator) % denominator for x in row] for row in bilinear],
        dtype=object,
    ).reshape(rank, rank)
    q_coefficients = numpy.asarray(
        [[int(x * denominator) % (self_period * denominator) for x in row]
         for row in self_gram], dtype=object,
    ).reshape(rank, rank)
    return (
        _engine_modular_pairing_pullback(b_coefficients, row_family, denominator),
        _engine_modular_pairing_pullback(
            q_coefficients, row_family, self_period * denominator, diagonal_only=True,
        ),
    )


def _engine_row_action_from_images(source_rows, target_rows):
    r"""Private engine adapter (`OWN-06`, `OWN-24`): the row action carrying a family to its images.

    Row ``k`` of ``source_rows`` is the coordinate row of a vector ``v_k`` and
    row ``k`` of ``target_rows`` that of ``f(v_k)``.  When the ``v_k`` span,
    ``f`` is determined by these images; return its matrix ``A`` in the
    engine's row convention, ``v A = f(v)``, which is the solution of
    ``S A = T``.  Sage's ``solve_right`` raises ``ValueError`` when no linear
    ``f`` has these images.  This is the one site that names the side on which
    a family's images determine a row action.
    """
    return source_rows.solve_right(target_rows)


def _engine_coisotropic_witt_extension(partial, source_inclusion, target_inclusion):
    r"""An exact row action extending a coisotropic partial rational isometry.

    Protected caller: ``LatticeIsometryMethods.witt_extension``.  Return
    ``None`` when the ambient forms are degenerate or the specified spaces
    are not coisotropic; those hypotheses belong to this computation, not
    to the general extension locus.

    For bases S_1,S_2 of the specified spaces, choose the Euclidean
    nullspace complement C_1 of S_1 in its selected framing.  Solve the
    pairing equations for C_2, then correct C_2 by X N_2, where N_2 is the
    form-perpendicular of S_2.  Since N_2 is isotropic, the remaining
    equations are linear: B = X A + A^t X^t.  Finally project the affine
    solution along its saturated integral homogeneous module; this removes
    precisely the denominators that a homogeneous correction can remove.

    This is the exact finite computation of Lorentzian.g:115-249 and
    Fundamental.g:509-516,751-794 in Indefinite.jl at 374a5ebb.  Sage's
    rational solve and Smith form implement its linear solves, saturation
    and unimodular completion.  The Euclidean complement selects vectors;
    every isometry and orthogonality equation uses the supplied forms.
    """
    from sage.rings.integer_ring import ZZ as SageZZ
    from sage.rings.rational_field import QQ as SageQQ

    source = source_inclusion.codomain()
    target = target_inclusion.codomain()
    left_form = _engine_component_matrix(source.gram_tensor()).change_ring(SageQQ)
    right_form = _engine_component_matrix(target.gram_tensor()).change_ring(SageQQ)
    left = _engine_row_action_matrix(source_inclusion).change_ring(SageQQ)
    right = (
        _engine_row_action_matrix(partial)
        * _engine_row_action_matrix(target_inclusion)
    ).change_ring(SageQQ)
    size = left_form.nrows()
    if right_form.nrows() != size:
        raise ValueError("isometric ambient spaces must have equal dimensions")
    rank = left.nrows()
    if right.nrows() != rank or left.rank() != rank or right.rank() != rank:
        raise ValueError("a partial isometry must be given by injective inclusions")
    if left * left_form * left.transpose() != right * right_form * right.transpose():
        raise ValueError("the prescribed images do not preserve the restricted form")
    if rank == size:
        return left.solve_right(right)
    if left_form.rank() != size or right_form.rank() != size:
        return None
    left_pairing = left * left_form
    right_pairing = right * right_form
    left_normal = left_pairing.right_kernel_matrix()
    right_normal = right_pairing.right_kernel_matrix()
    if not (
        (left_normal * left_form * left_normal.transpose()).is_zero()
        and (right_normal * right_form * right_normal.transpose()).is_zero()
    ):
        return None

    complement = left.right_kernel_matrix()
    dimension = complement.nrows()
    source_basis = left.stack(complement)
    source_inverse = source_basis.inverse()
    candidate = right_pairing.solve_right(left_pairing * complement.transpose()).transpose()
    difference = complement * left_form * complement.transpose() - candidate * right_form * candidate.transpose()
    pairing = right_normal * right_form * candidate.transpose()

    # SpecialEquationSolving: X is flattened by rows, and each equation
    # (i,j) reads (X A + A^t X^t)[i,j].
    equation = _sage_matrix(SageQQ, dimension * dimension, dimension * dimension)
    for i in range(dimension):
        for j in range(dimension):
            row = i * dimension + j
            for k in range(dimension):
                equation[row, i * dimension + k] += pairing[k, j]
                equation[row, j * dimension + k] += pairing[k, i]
    solution = equation.solve_right(_sage_vector(SageQQ, difference.list()))
    correction = _sage_matrix(SageQQ, dimension, dimension, solution)
    extension = source_inverse * right.stack(candidate + correction * right_normal)

    homogeneous = equation.right_kernel_matrix()
    if homogeneous.nrows():
        zero_rows = _sage_matrix(SageQQ, rank, size)
        directions = _sage_matrix(SageQQ, [
            (source_inverse * zero_rows.stack(
                _sage_matrix(SageQQ, dimension, dimension, row) * right_normal
            )).list()
            for row in homogeneous.rows()
        ])
        # A W B = D gives a unimodular coordinate change B taking the
        # rational homogeneous space to its first rank(W) coordinate axes.
        # Their inverse images form the complete saturated integral module;
        # the remaining axes give an integral complement, as in the source's
        # IntegralSpaceSaturation/SubspaceCompletionInt construction.
        integral_directions = (directions.denominator() * directions).change_ring(SageZZ)
        diagonal, _row_change, column_change = integral_directions.smith_form()
        dimension_homogeneous = diagonal.rank()
        coordinates = _sage_vector(SageQQ, extension.list()) * column_change
        for position in range(dimension_homogeneous):
            coordinates[position] = 0
        extension = _sage_matrix(SageQQ, size, size, coordinates * column_change.inverse())

    if extension * right_form * extension.transpose() != left_form or left * extension != right:
        raise ArithmeticError("the coisotropic Witt extension failed its form or restriction equation")
    return extension


def _engine_binary_form_pullback(form, linear_map):
    r"""Private engine adapter (`OWN-06`, `OWN-24`): pull a Sage binary form back along a map.

    ``form`` is a Sage ``BinaryQF`` ``Q`` on ``ZZ^2`` and ``linear_map`` a Sage
    ``2 x 2`` matrix ``M`` acting on coordinate columns.  Return the pullback
    ``M^*Q = Q o M``.  Sage's ``BinaryQF.matrix_action_right(M)`` evaluates
    ``Q`` on the columns of ``M``, ``Q(ax+by, cx+dy)`` for
    ``M = [[a, b], [c, d]]``, which is that pullback; this is the one site that
    names Sage's side convention for binary forms.  Pullback is contravariant,
    ``(M N)^*Q = N^*(M^*Q)``, so a chain of reduction steps composes as matrices.
    """
    return form.matrix_action_right(linear_map)


def _engine_component_vector(value):
    r"""Private engine adapter (`OWN-06`): the Sage vector of a one-index tensor.

    The one crossing of a one-index tensor, of either variance, into Sage's
    vector backend; its caller is the evaluation of a pairing on two vectors.
    """
    if value.tensor_order() != 1:
        raise TypeError(
            f"cannot write a type-{value.tensor_valence()} tensor as a vector: a vector "
            f"has exactly one index, this tensor has {value.tensor_order()}"
        )
    if value._index_ranks()[0] == Infinity:
        raise ValueError(
            f"cannot write a one-index tensor of rank {value._index_ranks()[0]} as a "
            f"vector: an index of infinite rank has no finite component list"
        )
    ring = value.base_ring()
    return _sage_vector(
        _engine_ring(ring),
        [_engine_element(ring, entry) for entry in value._flat_components()],
    )


class _TensorVectorConstructor:
    r"""Construct a type-``(1,0)`` tensor from an owned ring and components."""

    def __call__(self, base_ring, components=None, *args, **kwds):
        if args or kwds:
            raise TypeError(
                f"tensor.vector(R, components) takes a ring and one family of components; "
                f"got the extra arguments {args} and keywords {sorted(kwds)}"
            )
        if base_ring not in _Rings:
            raise TypeError(
                f"tensor.vector(R, components) needs a ring R; {base_ring!r} is not a ring"
            )
        if components is None:
            raise TypeError(
                f"tensor.vector(R, components) over {base_ring} was given no components"
            )
        # Literal component data: a natural number is the rank of the zero
        # vector; a Python mapping gives the nonzero components by position;
        # anything else is the sequence of components in order.
        match components:
            case _ if components in NN:
                entries = tuple(base_ring.zero() for _ in range(int(components)))
            case dict():
                size = 0 if not components else max(int(index) for index in components) + 1
                entries = tuple(
                    components.get(index, base_ring.zero()) for index in range(size)
                )
            case _:
                entries = tuple(components)
        return tensor(base_ring, (len(entries),), (), entries)


class _TensorCovectorConstructor:
    r"""Construct a type-``(0,1)`` tensor from an owned ring and components.

    A covector is an element of the dual tensor module, so it never shares a
    parent with a type-``(1,0)`` vector even when the component families agree.

    EXAMPLES::

        sage: from sage_extensions.tensors import tensor
        sage: c = tensor.covector(ZZ, [2, -1, 4])
        sage: c.tensor_valence()
        (0, 1)
        sage: c.parent()
        (ZZ^3)*
        sage: c * tensor.vector(ZZ, [5, 6, 7])
        32
    """

    def __call__(self, base_ring, components=None, *args, **kwds):
        contravariant = _TensorVectorConstructor()(
            base_ring, components, *args, **kwds
        )
        return tensor(
            contravariant.base_ring(),
            (),
            contravariant._upper_index_ranks(),
            contravariant._flat_components(),
        )


class _TensorMatrixConstructor:
    r"""Construct finite type-``(1,1)`` coordinate tensors.

    This is component data, not a module morphism.  Actual linear maps are
    elements of ``R.matrix_space(m,n) = Hom_R(R^n,R^m)``.  Sage matrix storage
    options and named constructor namespaces are deliberately not reproduced.
    """

    def __call__(self, *args, **kwds):
        if kwds:
            raise TypeError(
                f"tensor.matrix takes a ring and components only; the keywords "
                f"{sorted(kwds)} are not tensor data"
            )
        if not args or args[0] not in _Rings:
            raise TypeError(
                f"tensor.matrix needs a ring as its first argument; got "
                f"{args[0] if args else 'no arguments'!r}"
            )
        base = args[0]
        if len(args) == 2:
            components = args[1]
            if _is_coordinate_tensor(components, base):
                if components.tensor_order() != 2:
                    raise TypeError(
                        f"tensor.matrix cannot read a type-{components.tensor_valence()} "
                        f"tensor as a matrix: a matrix has exactly two indices, this "
                        f"tensor has {components.tensor_order()}"
                    )
                # Reinterpretation: the two index ranks are read off, and the
                # result is the type-(1,1) tensor this constructor makes.  The
                # input's own variance does not survive, which is the whole
                # content of reading its components as a matrix.  The tensor
                # is over this constructor's ring: moving components to
                # another ring is scalar change, done by ``change_ring``.
                contravariant_rank, covariant_rank = components._index_ranks()
                return tensor(
                    base,
                    (contravariant_rank,),
                    (covariant_rank,),
                    components._component_array(),
                )
            shape = _component_shape(components)
            if len(shape) != 2:
                raise TypeError(
                    f"tensor.matrix(R, components) needs a rectangular array with two "
                    f"indices; the components given have shape {shape}"
                )
            rows, columns = shape
            return _coordinate_tensor(base, (rows,), (columns,), components)
        if len(args) in (3, 4):
            rows = int(args[1])
            columns = int(args[2])
            components = (
                tuple(base.zero() for _ in range(rows * columns))
                if len(args) == 3
                else args[3]
            )
            return _coordinate_tensor(base, (rows,), (columns,), components)
        raise TypeError(
            f"tensor.matrix takes (R, components) or (R, rows, columns[, components]); "
            f"got {len(args)} arguments"
        )


@singledispatch
def _component_shape(component) -> tuple[int, ...]:
    r"""A non-list/tuple is one scalar component and has no remaining indices."""
    return ()


def _sequence_shape(components: list | tuple) -> tuple[int, ...]:
    r"""Return the shape of one rectangular nested component array."""
    if not components:
        return (0,)
    shapes = tuple(_component_shape(component) for component in components)
    first = shapes[0]
    if any(shape != first for shape in shapes[1:]):
        raise ValueError(
            f"the tensor components are not a rectangular array: the entries at one "
            f"level have the differing shapes {shapes}"
        )
    return (len(components),) + first


@_component_shape.register
def _(components: list) -> tuple[int, ...]:
    return _sequence_shape(components)


@_component_shape.register
def _(components: tuple) -> tuple[int, ...]:
    return _sequence_shape(components)


def _flatten(components, shape: tuple[int, ...]) -> tuple:
    r"""Flatten a component array whose rectangular shape is already known."""
    if not shape:
        return (components,)
    return tuple(
        entry
        for block in components
        for entry in _flatten(block, shape[1:])
    )


def _nested(entries: tuple, shape: tuple[int, ...]):
    r"""Rebuild the rectangular list presentation of flat row-major entries."""
    if len(shape) == 1:
        return list(entries)
    block_size = prod(shape[1:])
    return [
        _nested(entries[i * block_size : (i + 1) * block_size], shape[1:])
        for i in range(shape[0])
    ]


class _CoordinateTensor(ModuleElement, Tensor):
    r"""A tensor stored as its row-major component array.

    The element engine of the tensor module: its datum is the flat
    sequence of components, and its type, ranks and base ring are those of
    the tensor module it is an element of.
    """

    def __init__(self, parent: Parent, entries: tuple) -> None:
        self._entries = entries
        ModuleElement.__init__(self, parent)

    def __call__(self, *args):
        r"""Feed vectors into the covariant slots, from left to right.

        For a type-$(p,q)$ tensor, supplying $k\leq q$ vectors returns a
        type-$(p,q-k)$ tensor.  Only when every slot is consumed and $p=0$
        does evaluation return a scalar.
        """
        from itertools import product as _index_tuples

        _contravariant, covariant = self.tensor_valence()
        if NN(len(args)) > covariant:
            raise TypeError(
                f"a type-{self.tensor_valence()} tensor has only "
                f"{covariant} covariant slots, got {len(args)} arguments"
            )
        if not args:
            return self
        ring = self.base_ring()
        upper = self._upper_index_ranks()
        lower = self._lower_index_ranks()
        consumed = lower[: len(args)]
        remaining = lower[len(args) :]
        for position, vector in enumerate(args):
            slot = TensorModule(ring, (consumed[position],), ())
            if vector not in slot:
                raise TypeError(
                    f"cannot evaluate this type-{self.tensor_valence()} tensor on "
                    f"{vector!r}: argument {position} must be a vector of {slot}, the "
                    f"module paired with covariant slot {position}"
                )

        def contracted(output_index):
            upper_index = output_index[: len(upper)]
            remaining_index = output_index[len(upper) :]
            total = ring.zero()
            for eaten in _index_tuples(*(range(int(rank)) for rank in consumed)):
                term = self[upper_index + eaten + remaining_index]
                for position, index in enumerate(eaten):
                    term = term * args[position][index]
                total = total + term
            return total

        result_ranks = upper + remaining
        if not result_ranks:
            return contracted(())
        values = tuple(
            contracted(index)
            for index in _index_tuples(*(range(int(rank)) for rank in result_ranks))
        )
        return tensor(ring, upper, remaining, _nested(values, result_ranks))

    def _latex_(self) -> str:
        ranks = self._index_ranks()
        match len(ranks):
            case 1:
                entries = ", ".join(
                    str(latex(self[index])) for index in range(ranks[0])
                )
                return rf"\left({entries}\right)"
            case 2:
                rows = [
                    " & ".join(
                        str(latex(self[row, column]))
                        for column in range(ranks[1])
                    )
                    for row in range(ranks[0])
                ]
                return r"\begin{pmatrix}" + r" \\ ".join(rows) + r"\end{pmatrix}"
            case _:
                return str(latex(self._component_array()))

    def _repr_(self) -> str:
        p, q = self.tensor_type()
        space = repr(self.parent())
        body = _coordinate_component_repr(self)
        return f"Type ({p}, {q}) tensor in {space}\n{body}"

    def _component_array(self):
        r"""Private rectangular component array for tensor-owner computations."""
        return _nested(self._entries, self._index_ranks())

    def _flat_components(self):
        r"""Private flattened components in index order."""
        return tuple(self._entries)

    def __getitem__(self, index):
        r"""Return the component at a position, one integer per slot.

        A position is a tuple of integers, one per slot; a single integer is
        the position of a one-index tensor, ``v[i]``.  A negative integer
        counts back from the rank of its slot.

        Python's item-access protocol delivers ``t[i, j]`` as the tuple
        ``(i, j)`` and ``v[i]`` as ``i`` itself, so the key's syntax -- a
        tuple or not -- says which was written.  Membership in the integers
        cannot say it: Sage's ``Integer`` reads a tuple as a list of digits.
        """
        match index:
            case tuple():
                positions = index
            case _:
                positions = (index,)
        if len(positions) != len(self._index_ranks()):
            raise IndexError(
                f"a tensor of shape {self._index_ranks()} takes "
                f"{self.tensor_order()} indices, got {len(positions)}"
            )
        offset = 0
        for position, dimension in zip(positions, self._index_ranks()):
            position = int(position)
            if position < 0:
                position += dimension
            if position < 0 or position >= dimension:
                raise IndexError(
                    f"index {index} is out of range for a tensor with index ranks "
                    f"{self._index_ranks()}"
                )
            offset = offset * dimension + position
        return self._entries[offset]

    def _add_(self, other):
        if other.parent() is not self.parent():
            raise TypeError(
                f"cannot add a tensor in {self.parent()} to a tensor in {other.parent()}: "
                f"tensors add only within one tensor module"
            )
        return self.parent()._element_constructor_(
            tuple(left + right for left, right in zip(self._entries, other._entries))
        )

    def _sub_(self, other):
        if other.parent() is not self.parent():
            raise TypeError(
                f"cannot subtract a tensor in {other.parent()} from a tensor in "
                f"{self.parent()}: tensors subtract only within one tensor module"
            )
        return self.parent()._element_constructor_(
            tuple(left - right for left, right in zip(self._entries, other._entries))
        )

    def _neg_(self):
        return self.parent()._element_constructor_(tuple(-entry for entry in self._entries))

    def _lmul_(self, scalar):
        return self.parent()._element_constructor_(
            tuple(entry * scalar for entry in self._entries)
        )

    def _rmul_(self, scalar):
        return self.parent()._element_constructor_(
            tuple(scalar * entry for entry in self._entries)
        )

    def __mul__(self, other):
        r"""Scale by a scalar, or contract with a tensor over the same ring.

        Multiplication contracts the left tensor's rightmost covariant index
        with the right tensor's first contravariant index; a left tensor with
        no covariant index and at least two contravariant ones instead pairs
        its last contravariant index with a covector.  Which of these applies
        is read from the two tensor modules, after placement has established
        that ``other`` is a scalar of the base ring or an element of a tensor
        module over it.
        """
        ring = self.base_ring()
        if other in ring:
            return self._lmul_(ring(other))
        if not _is_coordinate_tensor(other, ring):
            raise TypeError(
                f"cannot multiply a tensor over {ring} by {other!r}: the product is "
                f"defined with a scalar of {ring} or a tensor over {ring}; otherwise use "
                f"contract or tensor_product"
            )
        upper = self._upper_index_ranks()
        lower = self._lower_index_ranks()
        valence = self.tensor_valence()
        other_valence = other.tensor_valence()
        from itertools import product as cartesian_product

        if len(upper) >= 2 and not lower and other_valence == _TENSOR_TYPES((0, 1)):
            if upper[-1] != other._lower_index_ranks()[0]:
                raise ValueError(
                    f"cannot multiply a type-{valence} tensor by a covector of rank "
                    f"{other._lower_index_ranks()[0]}: the product pairs the last upper "
                    f"index, of rank {upper[-1]}, with the covector, so the ranks must agree"
                )
            output_upper = upper[:-1]
            contracted_rank = upper[-1]
            positions = tuple(cartesian_product(*(range(rank) for rank in output_upper)))
            entries = tuple(
                sum(
                    (self[position + (index,)] * other[index] for index in range(contracted_rank)),
                    ring.zero(),
                )
                for position in positions
            )
            return tensor(ring, output_upper, (), _nested(entries, output_upper))
        if other_valence == _TENSOR_TYPES((1, 0)):
            if not lower:
                raise TypeError(
                    f"a type-{valence} tensor has no covariant index, so it cannot be "
                    f"evaluated on the vector {other!r}"
                )
            if lower[-1] != other._upper_index_ranks()[0]:
                raise ValueError(
                    f"cannot evaluate a type-{valence} tensor on a vector of rank "
                    f"{other._upper_index_ranks()[0]}: its last covariant index has rank "
                    f"{lower[-1]}, and the two ranks must agree"
                )

            # Multiplication contracts the rightmost covariant index.  Thus a
            # bilinear form G in M* tensor M* acts on v in M as G*v in M*,
            # with components (G*v)_i = sum_j G_{ij} v_j.  No row-vector or
            # transpose convention enters the public tensor calculus.
            output_upper = upper
            output_lower = lower[:-1]
            output_shape = output_upper + output_lower
            contracted_rank = lower[-1]
            positions = tuple(
                cartesian_product(*(range(rank) for rank in output_shape))
            ) if output_shape else ((),)
            entries = tuple(
                sum(
                    (self[position + (index,)] * other[index] for index in range(contracted_rank)),
                    ring.zero(),
                )
                for position in positions
            )
            if not output_shape:
                return entries[0]
            return tensor(ring, output_upper, output_lower, _nested(entries, output_shape))
        if valence == _TENSOR_TYPES((1, 1)) and other_valence == _TENSOR_TYPES((1, 1)):
            if lower != other._upper_index_ranks():
                raise ValueError(
                    f"cannot compose type-(1, 1) tensors with index ranks "
                    f"{self._index_ranks()} and {other._index_ranks()}: the covariant "
                    f"rank {lower} of the left must equal the contravariant rank "
                    f"{other._upper_index_ranks()} of the right"
                )
            # In U tensor V* tensor V tensor W*, contract the adjacent V*, V
            # factors.  Under Hom(V,U) = U tensor V* this agrees with map
            # composition, but its owner here is tensor evaluation.
            rows = upper[0]
            inner = other._upper_index_ranks()[0]
            columns = other._lower_index_ranks()[0]
            entries = tuple(
                sum((self[i, k] * other[k, j] for k in range(inner)), ring.zero())
                for i in range(rows)
                for j in range(columns)
            )
            return tensor(ring, (rows,), (columns,), _nested(entries, (rows, columns)))
        if valence == _TENSOR_TYPES((0, 1)) and other_valence == _TENSOR_TYPES((1, 1)):
            # In V* tensor V tensor W*, evaluate the adjacent V*, V pair.
            if lower != other._upper_index_ranks():
                raise ValueError(
                    f"cannot multiply a covector of rank {lower} by a type-(1, 1) tensor "
                    f"with index ranks {other._index_ranks()}: the covector's rank must "
                    f"equal the tensor's contravariant rank {other._upper_index_ranks()}"
                )
            rows = lower[0]
            columns = other._lower_index_ranks()[0]
            entries = tuple(
                sum((self[i] * other[i, j] for i in range(rows)), ring.zero())
                for j in range(columns)
            )
            return tensor(ring, (), (columns,), entries)
        raise TypeError(
            f"multiplication contracts the left tensor's rightmost covariant "
            f"index with the right tensor's first contravariant index; "
            f"type-{valence} and type-{other_valence} do not meet that way"
        )

    def __rmul__(self, other):
        r"""Scale by a scalar of the base ring on the left.

        A left operand that is not a scalar of the base ring is left to
        Python's operator protocol, which reports the product as unsupported.
        """
        ring = self.base_ring()
        if other not in ring:
            return NotImplemented
        return self._rmul_(ring(other))

    def _richcmp_(self, other, op):
        return _tensor_richcmp(self, other, op)

    __hash__ = Tensor._tensor_hash

    def __reduce__(self):
        return (
            _restore_tensor,
            (
                self.base_ring(),
                self._upper_index_ranks(),
                self._lower_index_ranks(),
                self._component_array(),
            ),
        )


def _coordinate_component_repr(tensor_value) -> str:
    r"""Render owned tensor coefficients without delegating display to an engine."""
    return repr(tensor_value._component_array())


def _owned_coordinate_component(ring, value):
    r"""Admit one tensor component, crossing raw Sage ring data only at ingress."""
    if isinstance(value, Fraction) and value.denominator == 1:
        value = int(value)
    parent = element_parent(value)
    match parent:
        case Parent() if parent in _Rings:
            return ring(value)
        case Parent() if parent in _SageRings:
            return _owned_engine_element(ring, _engine_numeral(ring, value))
        case _:
            return ring(value)


def _normalized_rank(rank):
    r"""The rank of one tensor slot: an ``int``, or ``Infinity`` for an infinite slot."""
    return Infinity if rank == Infinity else int(cardinal(rank).finite_value())


class _CoordinateTensorModule:
    r"""Private component-array realization of an R-module of tensors.

    It retains the split rank vector for the contraction engine.  The module
    is constructed through Modules(R); its Python representation is not an
    additional category in the mathematical graph.
    """

    def __init__(self, upper_ranks, lower_ranks, **rest) -> None:
        self._upper_ranks = upper_ranks
        self._lower_ranks = lower_ranks
        super().__init__(**rest)

    def construction(self):
        r"""Return no functorial construction.

        Sage's coercion walks this when it looks for an action of a ring on
        this module; a tensor module is built from its rank vector, not from
        a construction functor applied to another parent.
        """
        return None

    def __reduce__(self):
        return (
            TensorModule,
            (self.base_ring(), self._upper_ranks, self._lower_ranks),
        )

    def _index_ranks(self) -> tuple:
        return self._upper_ranks + self._lower_ranks

    def tensor_shape(self):
        r"""Return the family assigning each index slot the rank of its module."""
        return index_rank_family(self._index_ranks())

    @cached_method
    def tensor_type(self) -> ProductOfNaturalNumbers:
        r"""Return the type $(p, q)$ as a point of $\mathbb N^2$ (`CON-15`)."""
        return _TENSOR_TYPES((len(self._upper_ranks), len(self._lower_ranks)))

    def tensor_valence(self) -> ProductOfNaturalNumbers:
        return self.tensor_type()

    def _upper_index_ranks(self) -> tuple:
        return self._upper_ranks

    def _lower_index_ranks(self) -> tuple:
        return self._lower_ranks

    def _index_modules_for(self, ranks):
        def free_of_rank(rank):
            if rank == Infinity:
                return self.base_ring().free_module(NN)
            return self.base_ring().free_module(int(rank))

        slots = Sets.Δ[len(ranks) - 1]
        return indexed_family(
            slots,
            lambda slot: free_of_rank(ranks[int(slot)]),
            name="Tensor-index modules",
        )

    def contravariant_index_modules(self):
        r"""Return the family \(M_1,\ldots,M_p\) of contravariant index modules."""
        return self._index_modules_for(self._upper_ranks)

    def covariant_index_modules(self):
        r"""Return the family \(N_1,\ldots,N_q\) of covariant index modules."""
        return self._index_modules_for(self._lower_ranks)

    def index_modules(self):
        r"""Return the two variance module families as an object of ``Objects x Objects``."""
        return _owned_object_pair(
            self.contravariant_index_modules(),
            self.covariant_index_modules(),
        )

    @staticmethod
    def _index_generating_sets(modules):
        return indexed_family(
            modules.index_set(),
            lambda slot: modules[slot].module_generating_set(),
            name="Tensor-index generating sets",
        )

    def contravariant_index_generating_sets(self):
        r"""Return the generating-set family of the contravariant index modules."""
        return self._index_generating_sets(self.contravariant_index_modules())

    def covariant_index_generating_sets(self):
        r"""Return the generating-set family of the covariant index modules."""
        return self._index_generating_sets(self.covariant_index_modules())

    def tensor_indices(self):
        r"""Return the two variance generating-set families as an object of ``Objects x Objects``."""
        return _owned_object_pair(
            self.contravariant_index_generating_sets(),
            self.covariant_index_generating_sets(),
        )

    def _element_constructor_(self, entries):
        r"""Admit a tensor of this module, or its row-major component sequence."""
        if element_parent(entries) is self:
            return entries
        shape = self._index_ranks()
        assert Infinity not in shape, (
            f"cannot build an element of {self} from components: its index ranks "
            f"{shape} include an infinite rank"
        )
        entries = tuple(entries)
        if len(entries) != prod(shape):
            raise ValueError(
                f"an element of {self} with index ranks {shape} has {prod(shape)} "
                f"components; got {len(entries)}"
            )
        ring = self.base_ring()
        return self.element_class(
            self,
            tuple(_owned_coordinate_component(ring, entry) for entry in entries),
        )

    def zero(self):
        assert Infinity not in self._index_ranks(), (
            f"cannot build the zero tensor of {self} from components: its index ranks "
            f"{self._index_ranks()} include an infinite rank"
        )
        zero = self.base_ring().zero()
        return self.element_class(
            self,
            tuple(zero for _ in range(prod(self._index_ranks()))),
        )

    def _repr_(self) -> str:
        session, _tex = _tensor_space_session_and_latex(
            self.base_ring(), self._upper_ranks, self._lower_ranks
        )
        return session

    def _latex_(self) -> str:
        _session, tex = _tensor_space_session_and_latex(
            self.base_ring(), self._upper_ranks, self._lower_ranks
        )
        return tex


def _is_coordinate_tensor(value, ring):
    r"""Recognize this private tensor engine at the component-conversion boundary.

    Declared engine adapter (``OWN-06``): this is representation dispatch for
    the private coordinate-tensor realization, not mathematical membership.
    Gram pairing rules and component tensors use the same module engine.
    This is representation dispatch, not a new mathematical category.
    """
    parent = element_parent(value)
    return isinstance(parent, _CoordinateTensorModule) and parent.base_ring() is ring


def TensorModule(base_ring, upper_ranks, lower_ranks):
    r"""Return the module of type-$(p,q)$ tensors with the given index ranks.

    If every contravariant index is a copy of \(M=R^n\) and every covariant
    index is a copy of \(M\), this is
    \(M^{\otimes p}\otimes(M^*)^{\otimes q}\).  A type-$(0,q)$ tensor
    at infinite rank is an element of \((M^{\otimes q})^*\), not of
    \((M^*)^{\otimes q}\).

    The module on this rank vector, built by Modules(base_ring) through its
    private component engine: equal rank vectors over one ring give the same
    module.

    EXAMPLES::

        sage: from sage_extensions.tensors import tensor
        sage: G = tensor(ZZ, (), (2, 2), [[0, 1], [1, 0]])
        sage: G.parent()
        ((ZZ^2)*)^{⊗2}
        sage: G.tensor_type()
        (0, 2)
        sage: latex(G.parent())
        ((\mathbb{Z}^{2})^{*})^{\otimes 2}
    """
    if base_ring not in _Rings:
        raise TypeError(
            f"cannot build a tensor module over {base_ring!r}: the base must be a ring"
        )
    return _tensor_module_on(
        base_ring,
        tuple(_normalized_rank(rank) for rank in upper_ranks),
        tuple(_normalized_rank(rank) for rank in lower_ranks),
    )


@cached_function
def _tensor_module_on(base_ring, upper_ranks, lower_ranks):
    r"""Build the tensor module on a normalized rank vector through its category's entry."""
    return _object_of(
        Modules(base_ring),
        _engine=(Modules(base_ring), _CoordinateTensorModule, _CoordinateTensor),
        base_ring=base_ring,
        upper_ranks=upper_ranks,
        lower_ranks=lower_ranks,
    )


def _mixed_tensor_valence(valence) -> ProductOfNaturalNumbers:
    r"""Normalize one bidegree ``(p,q)`` of the mixed tensor algebra."""
    return _TENSOR_TYPES(valence)


class MixedTensorAlgebraElement(GradedDirectSumElement):
    r"""A finite-support sum of homogeneous mixed tensors."""

    def valences(self):
        r"""Return the finite set of bidegrees with nonzero component."""
        return finite_ordered_set(tuple(self._components))

    def _repr_(self):
        if not self._components:
            return "0"
        return " + ".join(
            f"[{valence[0]},{valence[1]}]({component})"
            for valence, component in self._components.items()
        )


class _MixedTensorDirectSum(_FramedDirectSumOfModules):
    r"""The canonical direct sum underlying one mixed tensor algebra."""

    def __init__(self, mixed_tensor_module, **rest) -> None:
        self._mixed_tensor_module = mixed_tensor_module
        super().__init__(**rest)

    def module(self):
        return self._mixed_tensor_module

    def dual_module(self):
        r"""Return the linear dual ``M^*`` used by the covariant factor."""
        return self.module().dual_module()

    def vector_tensor_algebra(self):
        r"""Return ``T(M)``, the contravariant tensor-algebra factor."""
        return self.module().tensor_algebra()

    def covector_tensor_algebra(self):
        r"""Return ``T(M^*)``, the covariant tensor-algebra factor."""
        return self.dual_module().tensor_algebra()

    def homogeneous_piece(self, valence):
        r"""Return the tensor module of bidegree ``valence``."""
        return self.graded_piece(valence)

    def include(self, tensor_element):
        r"""Include one live homogeneous tensor in its bidegree."""
        if not _is_coordinate_tensor(tensor_element, self.base_ring()):
            raise TypeError(
                f"cannot include {tensor_element!r} in {self}: it is not a tensor over "
                f"{self.base_ring()}"
            )
        valence = _mixed_tensor_valence(tensor_element.tensor_valence())
        expected = self.homogeneous_piece(valence)
        if tensor_element.parent() is not expected:
            raise ValueError(
                f"cannot include a tensor of {tensor_element.parent()} in {self}: the "
                f"bidegree-{valence} piece is {expected}, so every index must have the "
                f"rank of {self.module()}"
            )
        return self.from_component(valence, tensor_element)

    def _element_constructor_(self, value):
        r"""Admit an element: one of this algebra, a homogeneous tensor, a scalar, or components by bidegree.

        Components by bidegree are literal data, a Python mapping from
        bidegree to homogeneous tensor.
        """
        ring = self.base_ring()
        match value:
            case _ if element_parent(value) is self:
                return value
            case _ if _is_coordinate_tensor(value, ring):
                return self.include(value)
            case _ if value in ring:
                scalar_tensor = self.homogeneous_piece((0, 0))((ring(value),))
                return self.from_component((0, 0), scalar_tensor)
            case dict():
                return self.from_components(value)
            case _ if element_parent(value) in Modules(ring):
                return super()._element_constructor_(value)
            case _:
                raise TypeError(
                    f"{value!r} is not an element of {self}: an element is a tensor over "
                    f"{ring}, a scalar of {ring}, or a mapping from bidegrees to tensors"
                )

    def _module_with_structure(self, categories, construction_data):
        return super()._module_with_structure(
            categories,
            {"mixed_tensor_module": self.module(), **construction_data},
        )

    def _direct_sum_realization(self):
        return _MixedTensorDirectSum, MixedTensorAlgebraElement

    def _repr_(self) -> str:
        return f"Mixed tensor algebra T({self.module()}) tensor T({self.module()}^*)"


def _mixed_tensor_algebra(module):
    r"""Return ``T(M) tensor T(M^*)`` through the graded-module and algebra owners."""
    from sage_extensions.categories.algebras.algebras import _algebra_on_module
    from sage_extensions.categories.algebras.graded_algebras import (
        GradedAlgebras,
        _graded_multiplication_from_components,
    )

    rank = module.module_rank()
    assert rank.is_finite(), (
        f"cannot build the mixed tensor algebra T(M) tensor T(M^*) of {module}: it "
        f"is built here only for a module of finite rank, and {module} has rank {rank}"
    )
    ring = _own_ring(module.base_ring())
    size = int(rank)
    bigrades = _TENSOR_TYPES
    pieces = indexed_family(
        bigrades,
        lambda valence: TensorModule(
            ring,
            (size,) * int(valence[0]),
            (size,) * int(valence[1]),
        ),
        name="Mixed tensor homogeneous pieces",
    )
    graded = _direct_sum_of_modules(
        ring,
        bigrades,
        pieces,
        construction_data={"mixed_tensor_module": module},
        _realization=(_MixedTensorDirectSum, MixedTensorAlgebraElement),
        componentwise_framing=True,
    )

    def component_product(left_degree, left, right_degree, right):
        target = graded.graded_piece(
            graded.combine_degrees(left_degree, right_degree)
        )
        product = left.tensor_product(right)
        match product.parent() is target:
            case True:
                pass
            case False:
                raise ValueError(
                    f"the product of tensors of bidegrees {left_degree} and "
                    f"{right_degree} landed in {product.parent()}, not in the "
                    f"bidegree piece {target} of the mixed tensor algebra of {module}"
                )
        return product

    multiplication = _graded_multiplication_from_components(
        graded,
        component_product,
    )
    degree_zero = graded.graded_piece((0, 0))
    unit = graded.from_component((0, 0), degree_zero((ring.one(),)))
    return _algebra_on_module(
        graded,
        multiplication,
        placement=(GradedAlgebras(ring, bigrades),),
        unit=unit,
        law_decisions={"associativity": True, "unit": True, "grading": True},
    )


def _is_rank(value) -> bool:
    r"""Whether ``value`` names the rank of a finite tensor slot.

    A rank is a natural number, or a finite cardinal -- the rank a module
    reports is a cardinal.  Decided by placement in ``NN`` and in
    ``Cardinalities()``.
    """
    if value in NN:
        return True
    return value in Cardinalities() and value.is_finite()


def _rank_tuple(ranks) -> tuple[int, ...]:
    r"""Normalize one side of the tensor rank vector.

    A single rank is the one-index shorthand used by ``matrix(R, p, q, data)``;
    a family of ranks is the general tensor syntax.
    """
    if _is_rank(ranks):
        return (int(ranks),)
    dimensions = tuple(ranks)
    if not all(_is_rank(rank) for rank in dimensions):
        raise ValueError(
            f"the tensor index ranks {dimensions} are not all natural numbers or "
            f"finite cardinals"
        )
    return tuple(int(rank) for rank in dimensions)


def _coordinate_tensor(
    base_ring: Parent,
    upper_ranks: tuple[int, ...],
    lower_ranks: tuple[int, ...],
    components,
) -> Tensor:
    r"""Construct a coordinate tensor that is not a Sage vector or matrix."""
    shape = upper_ranks + lower_ranks
    nested_shape = _component_shape(components)
    if nested_shape:
        if nested_shape == shape:
            entries = _flatten(components, shape)
        elif nested_shape == (prod(shape),):
            entries = tuple(components)
        else:
            raise ValueError(
                f"a tensor over {base_ring} with index ranks {shape} needs components "
                f"of shape {shape} or a flat list of {prod(shape)}; got shape "
                f"{nested_shape}"
            )
    else:
        entries = tuple(components)
    return TensorModule(base_ring, upper_ranks, lower_ranks)(entries)


class _TensorConstructor:
    r"""General tensor constructor with variance encoded in the rank vectors.

    ``tensor.vector(R, data)``, ``tensor.covector(R, data)``, and
    ``tensor.matrix(R, data)`` are small typed conveniences over the main
    ``tensor(R, ps, qs, data)`` call.  They accept owned rings and mathematical
    component data only; Sage constructor/storage compatibility is not public
    API.

    The main call is ``tensor(R, ps, qs, data)``.  ``ps`` lists upper-index
    dimensions and ``qs`` lower-index dimensions.  Hence vectors and covectors
    are different constructor calls even though both have one index.
    """

    vector = _TensorVectorConstructor()
    covector = _TensorCovectorConstructor()
    matrix = _TensorMatrixConstructor()

    def from_matrix(self, matrix):
        r"""Interpret a finite matrix Mor element as a type-``(1,1)`` tensor."""

        parent = matrix.parent()
        ring = parent.base_ring()
        if parent not in MatrixSpaces(ring):
            raise TypeError(
                f"tensor.from_matrix needs a matrix over {ring}; {matrix!r} lies in "
                f"{parent}, which is not a space of matrices"
            )
        return self(
            ring,
            (parent.nrows(),),
            (parent.ncols(),),
            tuple(
                matrix[row_label, column_label]
                for row_label in parent.row_index_set()
                for column_label in parent.column_index_set()
            ),
        )

    def from_morphism(self, morphism):
        r"""Interpret a finite framed-free module morphism as a type-``(1,1)`` tensor.

        The ordinary module Mor of the endpoints must itself be a matrix Mor.
        """
        matrix = morphism._framed_coordinate_morphism()
        return self.from_matrix(matrix)

    def __call__(
        self,
        base_ring: Parent,
        upper_ranks,
        lower_ranks,
        components=None,
        **kwds,
    ) -> Tensor:
        r"""Construct a tensor of type \((\lvert\mathrm{ps}\rvert,\lvert\mathrm{qs}\rvert)\).

        EXAMPLES::

            sage: from sage_extensions.tensors import tensor
            sage: G = tensor(ZZ, (), (2, 2), [[0, 1], [1, 0]])
            sage: G.tensor_type()
            (0, 2)
            sage: G.parent()
            ((ZZ^2)*)^{⊗2}
            sage: tensor(ZZ, (), (3,), [1, 2, 3]).parent()
            (ZZ^3)*
            sage: tensor(ZZ, (2, 3), (), range(6)).parent()
            ZZ^2 ⊗ ZZ^3
        """
        if base_ring not in _Rings:
            raise TypeError(
                f"cannot build a tensor over {base_ring!r}: the base must be a ring"
            )
        ps = _rank_tuple(upper_ranks)
        qs = _rank_tuple(lower_ranks)

        if kwds:
            names = ", ".join(sorted(kwds))
            raise TypeError(
                f"tensor(R, ps, qs, components) takes no keywords; {names} is a Sage "
                f"matrix storage option, not tensor data"
            )
        if components is None:
            zero = base_ring.zero()
            components = tuple(zero for _ in range(prod(ps + qs)))
        return _coordinate_tensor(base_ring, ps, qs, components)


tensor = _TensorConstructor()


def _restore_tensor(
    base_ring: Parent,
    upper_ranks: tuple[int, ...],
    lower_ranks: tuple[int, ...],
    components,
) -> Tensor:
    return tensor(base_ring, upper_ranks, lower_ranks, components)
