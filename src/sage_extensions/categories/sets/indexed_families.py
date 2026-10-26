"""Owned indexed families of mathematical values."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from itertools import islice
from typing import TYPE_CHECKING, Any

from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.objects import Objects

from sage_extensions.lexicon.set_theory import SetObject
from sage_extensions.owned_category import _object_of

if TYPE_CHECKING:
    from sage_extensions.categories.sets.cardinals import Cardinal
    from sage_extensions.logic import Predicate


class IndexedFamily[IndexT, ValueT]:
    r"""A family ``(x_i)_{i in I}`` retaining its indexing set.

    A family is not the set of its values: different indices may have equal
    values, so it is not injective and has no ranking map of its own.  Its
    index set may have one, and positional access goes through that.
    Consumers iterate values lazily or address them through ``value(index)``.
    """

    def __init__(
        self,
        index_set: Parent,
        value: Callable[[IndexT], ValueT] | Parent,
        *,
        value_category=None,
        name: str | None = None,
        **rest,
    ) -> None:
        self._constant_value = value if isinstance(value, Parent) else None
        if isinstance(value, Parent):
            selected = value
            value = lambda _index: selected
        if not callable(value):
            raise TypeError(
                f"an indexed family over {index_set} needs a map from indices to values, but {value!r} is "
                "not callable"
            )
        self._index_set = index_set
        self._value_function = value
        self._value_cache: dict[int, list[tuple[IndexT, ValueT]]] = {}
        self._rank_value_cache: dict[int, ValueT] = {}
        self._unhashable_value_cache: list[tuple[IndexT, ValueT]] = []
        self._cached_hashable_values: list[tuple[IndexT, ValueT]] = []
        self._name = name
        self._diagram = None
        self._value_category = value_category
        super().__init__(**rest)

    def index_set(self) -> SetObject:
        return self._index_set

    def constant_value(self):
        r"""The defining value of a constant family, or ``None`` otherwise."""
        return self._constant_value

    def selected_diagram(self):
        return self._diagram

    def cardinality(self) -> Cardinal:
        from sage_extensions.categories.sets.cardinals import cardinal

        return cardinal(self.index_set().cardinality())

    def value(self, index: IndexT) -> ValueT:
        r"""Return the chosen value at this label, including unhashable labels.

        Unverified specimen: a family chooses its value once, not each time
        a Python list is used to address the same point of its index set::

            sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
            sage: labels = finite_ordered_set(([0], [1]))
            sage: family = indexed_family(labels, lambda label: finite_ordered_set((label[0],)))
            sage: family.value([0]) is family.value([0])
            True
            sage: labels = finite_ordered_set((([0],),))
            sage: family = indexed_family(labels, lambda label: finite_ordered_set((label[0][0],)))
            sage: family.value(([0],)) is family.value(([0],))
            True
        """
        return self._value_at_normalized_index(self.index_set()(index))

    def _value_at_normalized_index(self, normalized: IndexT) -> ValueT:
        r"""Return the cached value at an index already supplied by ``index_set()``.

        Iteration over an indexed family obtains its labels from the index set
        itself.  Reapplying the index-set constructor to those labels is not a
        mathematical operation and can be expensive for represented index
        sets, so the internal iteration path enters the value cache directly.
        Public ``value(index)`` still performs the canonical normalization.

        This is the Python memoization boundary. A tuple may implement the
        hash protocol while containing an unhashable label. Only that hash
        computation is caught; errors from the mathematical value constructor
        propagate without selecting another cache or constructing twice.
        A hash selects a bucket, not an equality decision: reuse a value only
        for an identical or decided-equal label. An undecided comparison keeps
        the labels separate without asserting that they are unequal.
        """
        from sage_extensions.categories.sets.set_categories import EnumeratedSets, Sets

        indices = self.index_set()
        if Sets().is_provably_finite(indices) and indices in EnumeratedSets():
            # The selected enumeration is a bijection: equal labels have
            # precisely the same ordinal rank. Use that mathematical datum
            # rather than a hash or an undecidable equality comparison.
            rank = int(indices.ranking_map()(normalized))
            if rank not in self._rank_value_cache:
                self._rank_value_cache[rank] = self._value_function(normalized)
            return self._rank_value_cache[rank]
        try:
            index_hash = hash(normalized)
        except (TypeError, ValueError):
            # Hashability is representation data, not a hypothesis on an
            # indexing set. Only unhashable labels actually requested are
            # retained on this exact fallback path.
            bucket = self._unhashable_value_cache
            candidates = (*bucket, *self._cached_hashable_values)
        else:
            bucket = self._value_cache.setdefault(index_hash, [])
            # Hashing is only a storage optimization. Presented mathematical
            # labels may have different hashes even when their equality is
            # decided true, so the cache's equality contract must not be
            # restricted to the matching Python hash bucket.
            candidates = (*self._cached_hashable_values, *self._unhashable_value_cache)
        for known, value in candidates:
            if normalized is known:
                equal = True
            else:
                try:
                    equal = normalized == known
                except (TypeError, ValueError):
                    # Some mathematical parents signal an undecided equality
                    # by raising when their comparison cannot be decided.
                    # That is not proof of inequality and must not abort value
                    # selection; retain this presentation as a separate cache
                    # entry below.
                    continue
            if equal is True:
                return value
            # Undecidable equality is not a reason to reuse a previous
            # value, nor evidence that the two labels are distinct.  Keep
            # both presentations in the memoization cache until an exact
            # identity or decided equality justifies reuse.
        value = self._value_function(normalized)
        bucket.append((normalized, value))
        if bucket is not self._unhashable_value_cache:
            self._cached_hashable_values.append((normalized, value))
        return value

    __call__ = value

    def __getitem__(self, index: IndexT) -> ValueT:
        r"""The value at a label, otherwise at a position in the index set's enumeration."""
        match self.index_set().is_parent_of(index):
            case True:
                return self.value(index)
            case False:
                from sage_extensions.categories.sets.set_categories import EnumeratedSets

                if self.index_set() not in EnumeratedSets():
                    raise ValueError(
                        f"{index!r} is not an index of {self}, and its index set "
                        "has no selected enumeration for positional lookup"
                    )
                return self.value(self.index_set().ranking_map().inverse()(index))
            case _:
                raise ValueError(
                    f"cannot select the value of {self} at {index!r}: "
                    "membership in its index set is undecided, so this datum "
                    "cannot be interpreted as either a label or a rank"
                )

    def items(self) -> Iterator[tuple[IndexT, ValueT]]:
        return (
            (index, self._value_at_normalized_index(index))
            for index in self.index_set()
        )

    def keys(self) -> SetObject:
        r"""Return the mathematical index set of this family."""
        return self.index_set()

    def values(self) -> Iterator[ValueT]:
        return iter(self)

    def get(self, index: IndexT, default=None):
        r"""Return a value only for decided index membership.

        An undecided membership proposition cannot select the default: that
        would assert absence of an index that may actually belong to the set.
        """
        match self.index_set().is_parent_of(index):
            case True:
                return self.value(index)
            case False:
                return default
            case _:
                raise ValueError(
                    f"cannot select a value or default for {index!r}: "
                    f"membership in {self.index_set()} is undecided"
                )

    def __iter__(self) -> Iterator[ValueT]:
        return (
            self._value_at_normalized_index(index)
            for index in self.index_set()
        )

    def __contains__(self, candidate: object) -> bool | Predicate:
        r"""Return the image-membership proposition for a represented family.

        The family retains its indexing data and is not identified with its
        image set. For a constant family with a nonempty index set, membership
        is equality with its selected value. For a finite family, occurrence
        among the selected values is the finite existential. An
        undecided equality is not nonmembership; one decided match establishes
        membership even when other comparisons remain undecided.
        """
        # The image of a constant family on a provably nonempty index set is
        # a singleton, independently of the cardinality of that index set.
        # On the empty set its image is empty. Neither case enumerates I.
        constant = self.constant_value()
        if constant is not None:
            size = self.cardinality()
            if size == 0:
                return False
            if size.is_finite() is False or (size.is_finite() is True and size.finite_value() > 0):
                return True if candidate is constant else constant == candidate
        from sage_extensions.logic import AtomicProposition, conjunction, negation
        from sage_extensions.categories.sets.set_categories import EnumeratedSets

        # Finiteness does not select an enumeration, and an infinite image
        # remains a set with a definite mathematical membership proposition
        # even when the given representation cannot decide that proposition.
        if self.cardinality().is_finite() is not True or self.index_set() not in EnumeratedSets():
            return AtomicProposition("is_member", candidate, self)

        return negation(conjunction(
            negation(True if (value := self._value_at_normalized_index(index)) is candidate else value == candidate)
            for index in self.index_set()
        ))

    def __len__(self) -> int:
        r"""Return the Python length when the mathematical index set is finite."""
        size = self.cardinality()
        if not size.is_finite():
            raise TypeError(
                f"the family {self} has infinite index set of cardinality {size}, so it has no length"
            )
        return int(size.finite_value())

    def map[MappedValueT](
        self,
        function: Callable[[ValueT], MappedValueT],
        *,
        name: str | None = None,
    ) -> IndexedFamily[IndexT, MappedValueT]:
        if not callable(function):
            raise TypeError(f"cannot map {function!r} over the family {self}: it is not callable")
        from sage_extensions.categories.functors.core import Functor

        diagram = self.selected_diagram()
        if isinstance(function, Functor) and diagram is not None:
            # A functor acts on the entire selected diagram, not merely on
            # its object callback. This retains morphism transport and the
            # codomain witness for nonconstant infinite factor families.
            # When the diagram lands in a stronger category, its canonical
            # inclusion is part of the composite; dropping the diagram or
            # rejecting a legitimate restriction would lose its arrow data.
            if diagram.codomain() is not function.domain() and diagram.codomain().is_subcategory(function.domain()):
                diagram = diagram.then(diagram.codomain().inclusion_into(function.domain()))
            return indexed_family(self.index_set(), diagram.then(function), name=name)
        constant = self.constant_value()
        if constant is not None:
            mapped = function(constant)
            if isinstance(mapped, Parent):
                # Mapping an actually constant family produces a constant
                # family. Preserve this defining datum even for an infinite
                # index set: replacing it by a callback would erase the
                # constant-family evidence used by categorical products.
                return indexed_family(self.index_set(), mapped, name=name)
            # The map is already evaluated on the unique value of this
            # family. Retain that same result even when it is not a parent;
            # an opaque per-index callback would rerun the computation and
            # could assign different objects to identical input values.
            return indexed_family(self.index_set(), lambda _index: mapped, name=name)
        return indexed_family(
            self.index_set(),
            lambda index: function(self.value(index)),
            name=name,
        )

    def __eq__(self, other: Any) -> bool | Predicate:
        r"""Return extensional equality, decided on a finite index set.

        Otherwise the answer is the proposition that the two families are
        equal.
        """
        from sage_extensions.logic import AtomicProposition, conjunction

        if self is other:
            return True
        if not isinstance(other, IndexedFamily):
            return False

        # Families on the identical retained index object have the same
        # domain without asking an equality algorithm for that set. This
        # matters when its representation has undecidable extensional
        # equality, but its chosen finite enumeration is available.
        same_indices = (
            True if self.index_set() is other.index_set()
            else self.index_set() == other.index_set()
        )
        if same_indices is False:
            return False
        from sage_extensions.categories.sets.set_categories import EnumeratedSets

        if (
            same_indices is not True
            or self.cardinality().is_finite() is not True
            or self.index_set() not in EnumeratedSets()
        ):
            return AtomicProposition("equal", self, other)
        return conjunction(self.value(index) == other.value(index) for index in self.index_set())

    def __ne__(self, other) -> bool | Predicate:
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self):
        r"""Hash selected finite extensional data; otherwise retain identity.

        Finiteness alone supplies no enumeration of the index set. The
        extensional-equality owner also requires a selected enumeration;
        hashing must not attempt to iterate an unenumerated finite index.
        """
        from sage_extensions.categories.sets.set_categories import EnumeratedSets

        if self.cardinality().is_finite() is not True or self.index_set() not in EnumeratedSets():
            return object.__hash__(self)
        # Neither indices nor values are required to be hashable.  In
        # particular, distinct representations of equal points may differ in
        # hashability, so branching on the ability to hash a value would
        # violate the implication f == g => hash(f) == hash(g).  The index
        # set is a necessary equality invariant; collisions between different
        # value assignments are permitted by the hash contract.
        return hash(self.index_set())

    def _repr_(self):
        from sage_extensions.categories.sets.set_categories import (
            EnumeratedSets,
            FiniteSets,
        )

        index_set = self.index_set()
        label = self._name or "Indexed family"
        if index_set in FiniteSets() and index_set in EnumeratedSets():
            size = int(index_set.cardinality().finite_value())
            shown = tuple(index_set) if size <= 12 else tuple(islice(index_set, 6))
            entries = ", ".join(
                f"{index} ↦ {self.value(index)}" for index in shown
            )
            suffix = "" if size <= 12 else ", ..."
            data = f"[{entries}{suffix}]"
            prefix = f"{label}: " if self._name else ""
            count = "" if size <= 12 else f" ({size} entries)"
            return f"{prefix}{data}{count}"

        return f"{label} over {index_set}"


def indexed_family[IndexT, ValueT](
    index_set: Parent,
    value: Callable[[IndexT], ValueT] | Parent,
    *,
    value_category=None,
    name: str | None = None,
) -> IndexedFamily[IndexT, ValueT]:
    r"""Return the family ``index |-> value(index)`` as an owned mathematical object.

    A family is not the set of its values: repeated values at distinct indices
    remain distinct family slots.  Until a consumer supplies a more specific
    codomain/category (for example a discrete diagram in ``[I,C]``), the family
    therefore lives at the existing root ``Objects()`` rather than being
    misdeclared as a set.
    """
    from sage_extensions.categories.abstract_categories.functors import DiscreteCategory, _DiscreteDiagram
    from sage_extensions.categories.functors.core import Functor

    selected_functor = value if isinstance(value, Functor) else None
    if selected_functor is not None:
        from sage_extensions.categories.sets.set_categories import EnumeratedSets, Sets
        from sage_extensions.categories.abstract_categories.products import RestrictedDiagram

        provenance = selected_functor
        while isinstance(provenance, RestrictedDiagram):
            provenance = provenance.original_diagram()
        if isinstance(provenance, _DiscreteDiagram) and not Sets().is_provably_finite(
            provenance.domain().object_set()
        ):
            raise TypeError(
                "a diagram descended from an unchecked infinite object callback "
                "does not establish that its values belong to its claimed codomain"
            )
        index_category = DiscreteCategory(index_set)
        if selected_functor.domain() is not index_category:
            raise ValueError("the selected family functor has the wrong discrete index category")
        if value_category is not None and value_category is not selected_functor.codomain():
            raise ValueError("the requested category differs from the selected functor codomain")
        value_category = selected_functor.codomain()
        value = lambda index: selected_functor(index_category.object(index))

    family = _object_of(
        Objects(),
        _engine=(Objects(), IndexedFamily, None),
        index_set=index_set,
        value=value,
        value_category=value_category,
        name=name,
    )
    if value_category is not None:
        from sage_extensions.categories.abstract_categories.cat import Cat
        from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
        from sage_extensions.categories.sets.set_categories import EnumeratedSets, Sets

        constant = family.constant_value()
        if constant is not None and constant not in value_category:
            raise ValueError(
                f"the constant family has value {constant}, outside its declared category {value_category}"
            )
        if not Sets().is_provably_finite(index_set) and family.constant_value() is None and selected_functor is None:
            raise TypeError(
                "an infinite nonconstant family cannot establish its value category by declaring one: "
                "supply a mathematically justified category-valued diagram"
            )
        if Sets().is_provably_finite(index_set) and index_set in EnumeratedSets():
            for index in index_set:
                if family(index) not in value_category:
                    raise ValueError(
                        f"the selected family has value {family(index)} at {index}, outside {value_category}"
                    )

        if (
            family.constant_value() is None
            and selected_functor is None
            and index_set not in EnumeratedSets()
        ):
            raise TypeError(
                "a nonconstant family without selected index enumeration cannot certify its value category"
            )

        diagram_parent = Cat().Mor(DiscreteCategory(index_set), value_category)
        family._diagram = (
            selected_functor
            or (diagram_parent.constant_functor(constant) if constant is not None
                else diagram_parent.discrete_diagram(family))
        )
    return family


finite_indexed_family = indexed_family


def finite_indexed_family_from_values(
    index_set,
    values,
    *,
    name: str | None = None,
) -> IndexedFamily:
    r"""Read finite literal data as an indexed family, preserving its labels.

    ``values`` may already be an indexed family, a mapping keyed by labels, or
    an ordinary finite iterable.  When ``index_set`` is omitted, those three
    cases use the family's own labels, the mapping keys, or the ordinal of the
    iterable positions respectively.  Literal-container interpretation belongs
    here, at the indexed-family owner; mathematical consumers only state the
    index set they require.
    """
    from sage_extensions.categories.sets.finite_ordered_sets import (
        finite_ordered_set,
    )

    match values:
        case IndexedFamily():
            from sage_extensions.categories.sets.set_categories import EnumeratedSets

            supplied_cardinality = values.cardinality()
            if supplied_cardinality.is_finite() is not True:
                raise TypeError(
                    f"cannot read {values} as a finite family: its index set has cardinality {supplied_cardinality}"
                )
            match index_set:
                case None:
                    if values.index_set() not in EnumeratedSets():
                        raise TypeError(
                            "cannot select finite ordered labels from an indexed family "
                            "whose index set has no enumeration"
                        )
                    # Preserve the actual domain, not a different ordered
                    # presentation of the same points. A copied enumeration
                    # is not an identity map between the two set objects.
                    labels = values.index_set()
                case _:
                    # A family is a function on its exact index set. Equal
                    # cardinalities do not provide a reindexing map; a
                    # different set requires an explicit transport of labels.
                    same_labels = (
                        True if index_set is values.index_set()
                        else index_set == values.index_set()
                    )
                    if same_labels is not True:
                        raise ValueError(
                            f"cannot reinterpret the family on {values.index_set()} "
                            f"as a family on {index_set} without an index map"
                        )
                    labels = index_set
            family = indexed_family(labels, values.value, name=name)
            supplied_size = int(supplied_cardinality.finite_value())
        case Mapping():
            match index_set:
                case None:
                    labels = finite_ordered_set(tuple(values))
                case _:
                    from sage_extensions.categories.sets.set_categories import EnumeratedSets, Sets

                    if not Sets().is_provably_finite(index_set) or index_set not in EnumeratedSets():
                        raise TypeError(
                            f"mapping-valued finite family requires finite enumerated labels, not {index_set}"
                        )
                    if len(values) != int(index_set.cardinality().finite_value()) or any(
                        label not in values for label in index_set
                    ):
                        raise ValueError(
                            "the mapping keys must be precisely the selected index labels; "
                            "equal cardinalities alone do not define a family on that index set"
                        )
                    labels = index_set
            family = indexed_family(labels, values.__getitem__, name=name)
            supplied_size = len(values)
        case _:
            if index_set is not None:
                from sage_extensions.categories.sets.set_categories import EnumeratedSets, Sets

                if not Sets().is_provably_finite(index_set) or index_set not in EnumeratedSets():
                    raise TypeError(
                        f"positional finite-family data require a finite enumerated index set, not {index_set}"
                    )
            entries = tuple(values)
            match index_set:
                case None:
                    labels = finite_ordered_set(range(len(entries)))
                case _:
                    labels = index_set
            family = indexed_family(
                labels,
                lambda label: entries[int(labels.ranking_map()(label))],
                name=name,
            )
            supplied_size = len(entries)

    match family.cardinality().is_finite():
        case True:
            pass
        case _:
            raise TypeError(
                f"cannot read {values!r} as a finite family: the index set {labels} is not finite"
            )
    match int(family.cardinality().finite_value()) == supplied_size:
        case True:
            pass
        case False:
            raise ValueError(
                f"cannot read {values!r} as a family indexed by {labels}: it has {supplied_size} entries, but "
                f"{labels} has {family.cardinality()} elements"
            )
    return family


__all__ = [
    "IndexedFamily",
    "finite_indexed_family",
    "finite_indexed_family_from_values",
    "indexed_family",
]
