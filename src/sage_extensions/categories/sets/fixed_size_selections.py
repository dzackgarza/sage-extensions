"""Fixed-size subsets and multisets of enumerated sets."""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Iterable, Mapping
from heapq import merge
from itertools import groupby
from operator import index
from typing import SupportsIndex, TypeVar

from sage.arith.misc import binomial
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import Element
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalIsomorphism,
)
from sage_extensions.categories.sets.cardinals import Cardinalities, cardinal
from sage_extensions.categories.sets.finite_ordered_sets import FiniteOrderedSets
from sage_extensions.categories.sets.indexed_families import IndexedFamily, indexed_family
from sage_extensions.categories.sets.set_categories import (
    EnumeratedSets,
    FiniteSets,
    Sets,
)

PointT = TypeVar("PointT")


def _selection_integer(value: SupportsIndex) -> int:
    r"""Read integer index data through Python's exact integer-index protocol.

    This native ingress accepts Python, preparsed Sage and owned integers.
    Unlike Sage's integer constructor it also admits the owned natural-number
    element, whose native integer operation is ``__index__``.  The equality
    guard refuses a foreign implementation that truncates in ``__index__``.
    """
    result = index(value)
    if value != result:
        raise TypeError(f"a selection index must be an integer, but {value!r} is not")
    return result


def _largest_combinadic_entry(rank: int, size: int) -> int:
    # The largest a with binomial(a, size) <= rank. The usual finite-n
    # combination engine uses an ambient bound; here the source can be NN,
    # so discover one by doubling and locate a by integer bisection rather
    # than performing rank many increments when size is one.
    lower = size - 1
    upper = size
    while binomial(upper, size) <= rank:
        lower = upper
        upper *= 2
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if binomial(middle, size) <= rank:
            lower = middle
        else:
            upper = middle
    return lower


def _strict_positions_from_combinadic(rank: int, size: int):
    if size == 0:
        return iter(())
    # Recover the same colex combinadic digits iteratively. Recursive
    # recovery otherwise reaches Python's recursion limit for legitimate
    # high-degree finite selections, even at rank zero.
    largest_first = []
    remainder = rank
    for degree in range(size, 0, -1):
        largest = _largest_combinadic_entry(remainder, degree)
        largest_first.append(largest)
        remainder -= int(binomial(largest, degree))
    return iter(reversed(largest_first))


class FixedSizeSelectionElement(Element):
    r"""One selection, identified with its combinatorial rank."""

    def __init__(self, parent: FixedSizeSelections, combinatorial_rank: int) -> None:
        Element.__init__(self, parent)
        self._combinatorial_rank = combinatorial_rank

    def combinatorial_rank(self) -> int:
        return self._combinatorial_rank

    def degree(self) -> int:
        return self.parent().selection_size()

    def allows_repetition(self) -> bool:
        return self.parent().allows_repetition()

    @cached_method
    def _source_positions(self):
        r"""Selected source ranks, decoded once from the combinadic datum."""
        strict = tuple(_strict_positions_from_combinadic(
            self.combinatorial_rank(), self.degree()
        ))
        if not self.allows_repetition():
            return strict
        return tuple(position - offset for offset, position in enumerate(strict))

    def word(self) -> IndexedFamily:
        r"""The selection as the family of its points in increasing order."""
        indices = Sets.Δ[self.degree() - 1]
        positions = tuple(self._source_positions())
        point_at_rank = self.parent().source().ranking_map().inverse()

        def value(index):
            requested = int(index)
            return point_at_rank(positions[requested])

        return indexed_family(indices, value, name="Selection word")

    def __iter__(self):
        return iter(self.word())

    def multiplicity(self, label: PointT) -> int:
        source_position = int(self.parent().source().ranking_map()(label))
        return sum(
            1 for position in self._source_positions() if position == source_position
        )

    def support(self) -> FiniteOrderedSets.ObjectType:
        r"""The set of points occurring in the selection, in increasing order."""

        def distinct_positions():
            previous = None
            first = True
            for position in self._source_positions():
                if first or position != previous:
                    yield position
                first = False
                previous = position

        positions = tuple(distinct_positions())
        indices = Sets.Δ[len(positions) - 1]
        point_at_rank = self.parent().source().ranking_map().inverse()

        def source_label(index):
            requested = int(index)
            return point_at_rank(positions[requested])

        return FiniteOrderedSets().from_indexed(
            indices,
            source_label,
            name="Selection support",
        )

    def add_label(self, label: PointT) -> FixedSizeSelectionElement:
        target = self.parent().with_size(self.degree() + 1)
        position = int(self.parent().source().ranking_map()(label))
        positions = tuple(self._source_positions())
        if not self.allows_repetition() and position in positions:
            raise ValueError(
                f"cannot add {label} to the subset {self}: it already contains {label}"
            )
        return target.from_source_rank_positions(
            merge(positions, (position,))
        )

    def merged_with(self, other: FixedSizeSelectionElement) -> FixedSizeSelectionElement:
        r"""The union of two selections over one source, as a selection of the summed size."""
        assert element_parent(other) is self.parent().with_size(other.degree()), (
            f"cannot merge the selection {self} of {self.parent()} with {other} of {element_parent(other)}: "
            "they must come from one source set with one repetition rule"
        )
        target = self.parent().with_size(self.degree() + other.degree())
        left_positions = tuple(self._source_positions())
        right_positions = tuple(other._source_positions())
        if not self.allows_repetition():
            common = set(left_positions).intersection(right_positions)
            if common:
                raise ValueError(f"cannot merge the subsets {self} and {other}: they share source positions {common}")
        return target.from_source_rank_positions(
            merge(left_positions, right_positions)
        )

    def wedge_with(
        self, other: FixedSizeSelectionElement
    ) -> tuple[FixedSizeSelectionElement, int] | None:
        assert element_parent(other) is self.parent().with_size(other.degree()), (
            f"cannot form the wedge of {self} and {other}: they must be subsets of one enumerated set, but "
            f"{other} lies in {element_parent(other)}"
        )
        if self.allows_repetition() or other.allows_repetition():
            raise TypeError(
                f"the wedge of {self} and {other} is defined here for subsets, not multisets"
            )
        left_positions = tuple(self._source_positions())
        right_positions = tuple(other._source_positions())
        if set(left_positions).intersection(right_positions):
            return None
        # Both retained position tuples are increasing. The standard-library
        # binary-search primitive counts preceding right ranks without
        # forming the quadratic Cartesian family of comparisons.
        inversions = sum(bisect_left(right_positions, position) for position in left_positions)
        # Disjointness is established above. Reuse the selected positions
        # instead of unranking both selections again in merged_with.
        merged = self.parent().with_size(self.degree() + other.degree()).from_source_rank_positions(
            merge(left_positions, right_positions)
        )
        return merged, (-1 if inversions % 2 else 1)

    def __eq__(self, other) -> bool:
        return (
            element_parent(other) is self.parent()
            and other.combinatorial_rank() == self.combinatorial_rank()
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((id(self.parent()), self.combinatorial_rank()))

    def _repr_(self) -> str:
        if self.degree() == 0:
            return "1"
        if not self.allows_repetition():
            return "{" + ", ".join(map(repr, self)) + "}"
        terms = []
        point_at_rank = self.parent().source().ranking_map().inverse()
        for position, occurrences in groupby(self._source_positions()):
            label = point_at_rank(position)
            multiplicity = sum(1 for _ in occurrences)
            terms.append(
                repr(label)
                if multiplicity == 1
                else f"{label!r}^{multiplicity}"
            )
        return " ".join(terms)


class FixedSizeSelections(EnumeratedSets().ObjectType):
    r"""The set of \(k\)-element selections from an enumerated set \(S\).

    An engine realizing objects of ``EnumeratedSets()``.  Without repetition
    these are the \(k\)-element subsets of \(S\); with repetition they are the
    \(k\)-element multisets on \(S\).  The datum is \((S, k)\) and whether
    repetition is allowed.  A selection is identified with its rank in the
    combinatorial number system, which enumerates the set and orders it; the
    set is finite exactly when \(S\) is finite or \(k = 0\), and countably
    infinite otherwise.  These refinements are inherited from the source's
    placement, without requiring a cardinality computation to construct the
    selections.  ``S.fixed_size_selections(k, repetition=r)`` is the
    construction route.
    """

    Element = FixedSizeSelectionElement

    def __init__(
        self,
        source: EnumeratedSets.ObjectType,
        selection_size: SupportsIndex,
        *,
        repetition: bool,
    ) -> None:
        size = _selection_integer(selection_size)
        assert size >= 0, f"the selection size k must be a natural number, but k = {selection_size}"
        assert source in EnumeratedSets(), (
            f"selections of fixed size need an enumerated source set, but {source} is not enumerated"
        )
        self._source = source
        self._selection_size = size
        self._repetition = repetition
        match source:
            case _ if size == 0 or source in FiniteSets():
                size_placement = (FiniteSets(),)
            case _ if source in Sets().Countable().Infinite():
                size_placement = (Sets().Countable().Infinite(),)
            case _:
                size_placement = ()
        super().__init__(
            category=Cat().meet([EnumeratedSets(), *size_placement]),
            facade=False,
        )

    def source(self) -> EnumeratedSets.ObjectType:
        return self._source

    def selection_size(self) -> int:
        return self._selection_size

    def allows_repetition(self) -> bool:
        return self._repetition

    def with_size(self, selection_size: int) -> FixedSizeSelections:
        return self.source().fixed_size_selections(
            selection_size,
            repetition=self.allows_repetition(),
        )

    def _cardinality_decision(self) -> Cardinalities.ObjectType:
        r"""The number of \(k\)-selections from \(S\).

        For finite \(S\) with \(|S| = n\): \(\binom{n}{k}\) subsets and
        \(\binom{n+k-1}{k}\) multisets.  For \(k = 0\) the empty selection is
        the only one.  For infinite \(S\) and \(k \ge 1\) the selections number
        \(|S|\).  The chosen enumeration of an infinite \(S\) identifies it
        with \(\mathbb N\): the disjoint blocks
        \(\{kn,\ldots,kn+k-1\}\) inject \(\mathbb N\) into its
        \(k\)-subsets, which inject into \(\mathbb N^k\); the same lower
        bound works for multisets.  Both bounds are countable.
        """
        size = self.selection_size()
        if size == 0:
            return cardinal(1)
        source_size = cardinal(self.source().cardinality())
        match source_size:
            case _ if source_size.is_finite() and self.allows_repetition():
                return cardinal(binomial(source_size.finite_value() + size - 1, size))
            case _ if source_size.is_finite():
                return cardinal(binomial(source_size.finite_value(), size))
            case _:
                return source_size

    @cached_method
    def ranking_map(self) -> CategoricalIsomorphism:
        r"""The combinadic enumeration: a selection *is* its combinatorial rank."""

        def selection_at(position):
            position = _selection_integer(position)
            size = self.cardinality()
            if position < 0 or (size.is_finite() and position >= int(size)):
                raise IndexError(
                    f"position {position} is out of range for {self}, which has {size} elements"
                )
            # For a finite source the cardinality bound is precisely the
            # combinadic range in which every selected position lies in
            # the source.
            return self.element_class(self, position)

        return self._ranking_isomorphism(
            lambda selection: self(selection).combinatorial_rank(), selection_at
        )

    def __contains__(self, candidate) -> bool:
        r"""A selection of this set is an element constructed in it."""
        return element_parent(candidate) is self

    def _element_constructor_(self, datum):
        if datum in self:
            return datum
        raise TypeError(
            f"{datum!r} is not an element of {self}; build one from its rank, from its source positions, "
            "or from its multiplicities"
        )

    def from_source_rank_positions(
        self,
        positions: Iterable[SupportsIndex],
    ) -> FixedSizeSelectionElement:
        degree = self.selection_size()
        rank = 0
        count_positions = 0
        previous = None
        first = True
        for offset, source_position in enumerate(positions):
            source_position = _selection_integer(source_position)
            if source_position < 0:
                raise ValueError(
                    f"the source position {source_position} is negative, but source positions are natural numbers"
                )
            if not first:
                if self.allows_repetition():
                    if source_position < previous:
                        raise ValueError(
                            f"the source positions of a multiset must be nondecreasing, but {source_position} follows "
                            f"{previous}"
                        )
                elif source_position <= previous:
                    raise ValueError(
                        f"the source positions of a subset must be strictly increasing, but {source_position} follows "
                        f"{previous}"
                    )
            strict_position = (
                source_position + offset
                if self.allows_repetition()
                else source_position
            )
            rank += int(binomial(strict_position, offset + 1))
            count_positions += 1
            previous = source_position
            first = False
        if count_positions != degree:
            raise ValueError(
                f"an element of {self} needs exactly {degree} source positions, but {count_positions} were given"
            )
        return self[rank]

    def from_labels(self, labels: Iterable[PointT]) -> FixedSizeSelectionElement:
        positions = sorted(int(self.source().ranking_map()(label)) for label in labels)
        return self.from_source_rank_positions(positions)

    def from_multiplicities(
        self,
        multiplicities: Mapping[PointT, SupportsIndex],
    ) -> FixedSizeSelectionElement:
        if any(_selection_integer(value) < 0 for value in multiplicities.values()):
            raise ValueError(
                f"multiplicities must be natural numbers, but {dict(multiplicities)} has a negative value"
            )
        total = sum(_selection_integer(value) for value in multiplicities.values())
        if total != self.selection_size():
            raise ValueError(
                f"an element of {self} needs multiplicities summing to {self.selection_size()}, but they sum "
                f"to {total}"
            )
        if not self.allows_repetition() and any(
            _selection_integer(value) not in (0, 1) for value in multiplicities.values()
        ):
            raise ValueError(
                f"an element of {self} is a subset, so its multiplicities are 0 or 1, but they are "
                f"{dict(multiplicities)}"
            )
        positions = sorted(
            int(self.source().ranking_map()(label))
            for label, multiplicity in multiplicities.items()
            for _ in range(_selection_integer(multiplicity))
        )
        return self.from_source_rank_positions(positions)

    def singleton_power(self, label: PointT) -> FixedSizeSelectionElement:
        if self.selection_size() == 0:
            raise ValueError(
                f"{self} has selection size 0, so it has no element of the form {{{label}}}"
            )
        return self.from_multiplicities({label: self.selection_size()})

    def _repr_(self) -> str:
        noun = "Multisets" if self.allows_repetition() else "Subsets"
        return f"{noun} of {self.source()} of size {self.selection_size()}"


@cached_function(key=lambda source, selection_size, repetition: (id(source), _selection_integer(selection_size), bool(repetition)))
def _fixed_size_selections(
    source: EnumeratedSets.ObjectType,
    selection_size: int,
    *,
    repetition: bool,
) -> FixedSizeSelections:
    return FixedSizeSelections(source, selection_size, repetition=bool(repetition))


__all__ = [
    "FixedSizeSelectionElement",
    "FixedSizeSelections",
]
