"""Owned ordered enumerated sets, with the finite ones as a refinement."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import chain, islice
from typing import TYPE_CHECKING, TypeVar

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.misc.prandom import randrange
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalIsomorphism,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.set_categories import (
    EnumeratedSets,
    FiniteSets,
    Sets,
    finite_ordinal_set,
)
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of, owned_category_join

if TYPE_CHECKING:
    from sage_extensions.logic import Predicate

IndexT = TypeVar("IndexT")
PointT = TypeVar("PointT")


class OrderedEnumeratedSets(OwnedCategory):
    r"""Sets presented by a chosen enumeration from an index set.

    The defining datum is the enumeration: an index set \(I\), the bijection
    ``element_at`` from \(I\) onto the set, its inverse ``index_of``, which
    answers ``None`` for a candidate that is not a point, and optionally a
    membership decision ``contains``.  The total order is the one the
    enumeration transports from \(I\), which ``EnumeratedSets`` answers.
    """

    def an_object(self) -> ObjectOfCategory:
        r"""The ordinal on three points."""
        return finite_ordered_set((0, 1, 2))

    def super_categories(self):
        return [EnumeratedSets()]

    def __call__(self, index_set, element_at, **datum):
        r"""Construct from an enumeration even when ``index_set`` is itself in this category.

        Sage's generic category call returns its first argument whenever that
        argument is already an object of the category.  The index set of an
        enumeration may be one, and the enumeration is further data, so the
        call always constructs.
        """
        return self._call_(index_set, element_at, **datum)

    def _call_(
        self,
        index_set: Parent,
        element_at: Callable[[IndexT], PointT],
        *,
        index_of: Callable[[PointT], IndexT | None],
        contains: Callable[[PointT], bool] | None = None,
        name: str | None = None,
    ) -> Sets().ObjectType:
        r"""Construct an ordered enumerated set from its chosen enumeration."""
        assert index_set in EnumeratedSets(), (
            f"an ordered set is indexed by an enumerated set, but {index_set} is not enumerated"
        )
        match index_set:
            case _ if Sets().is_provably_finite(index_set):
                return FiniteOrderedSets().from_indexed(
                    index_set, element_at, index_of=index_of, contains=contains, name=name
                )
            case _ if index_set in Sets().Infinite():
                placement = owned_category_join((self, Sets().Infinite()))
            case _:
                placement = self
        return _object_of(
            placement,
            index_set=index_set,
            element_at=element_at,
            index_of=index_of,
            contains=contains,
            name=name,
        )

    class ParentMethods:
        def __init__(
            self,
            index_set: Parent,
            element_at: Callable[[IndexT], PointT],
            *,
            index_of: Callable[[PointT], IndexT | None],
            contains: Callable[[PointT], bool] | None = None,
            name: str | None = None,
            **rest,
        ) -> None:
            assert callable(element_at), (
                f"an ordered set needs a map from its index set {index_set} to its points, but "
                f"{element_at!r} is not callable"
            )
            assert callable(index_of), (
                f"an ordered set needs the map from points back to positions in {index_set}, but "
                f"{index_of!r} is not callable; without it the data is a family, not a set with an order"
            )
            self._index_set = index_set
            self._element_at_function = element_at
            self._index_of_function = index_of
            self._contains_function = contains
            self._name = name
            super().__init__(facade=True, **rest)

        def index_set(self) -> Sets().ObjectType:
            return self._index_set

        def enumeration(self) -> Callable[[IndexT], PointT]:
            r"""The chosen bijection from the index set onto this set."""
            return self._element_at_function

        def enumeration_inverse(self) -> Callable[[PointT], IndexT | None]:
            r"""The chosen inverse on this set, with ``None`` allowed off it."""
            return self._index_of_function

        def __iter__(self):
            r"""Iterate through the chosen enumeration.

            This category already stores the bijection ``I -> X`` as its
            defining datum.  Iteration therefore evaluates that map on the
            represented index set directly; the categorical ranking
            isomorphism is needed when the isomorphism itself is requested,
            not to read the enumeration it represents.

            The standard finite ordinal is the one self-indexed construction:
            its index set is literally itself and its selected enumeration is
            the identity on ``0, ..., n-1``.  Read those positions from its
            finite cardinality rather than recursively asking it to iterate.
            """
            element_at = self.enumeration()
            index_set = self.index_set()
            if index_set is self:
                size = cardinal(self.cardinality())
                assert size.is_finite(), (
                    f"the self-indexed ordered enumeration {self} needs a finite cardinality "
                    "or its defining category must state its own base enumeration"
                )
                indices = range(int(size.finite_value()))
            else:
                indices = index_set
            return (element_at(index) for index in indices)

        @cached_method
        def ranking_map(self) -> CategoricalIsomorphism:
            r"""The chosen enumeration of this set, as one isomorphism.

            The presentation gives a bijection from the index set, and the
            index set already knows its own ordinal, so this composes the two
            rather than counting the set a second time.
            """
            index_ranking = self.index_set().ranking_map()

            def point_at(position):
                return self._element_at_function(index_ranking.inverse()(int(position)))

            def position_of(element):
                # Admission verifies the inverse's domain and its forward
                # equation; a raw supplied inverse need not do either.
                admitted = self._element_constructor_(element)
                index = self._index_of_function(admitted)
                if index is None:
                    raise ValueError(f"{element!r} is not in {self}")
                return int(index_ranking(index))

            return self._ranking_isomorphism(position_of, point_at)

        def __contains__(self, element):
            if self._contains_function is not None:
                decision = self._contains_function(element)
                if decision is True or decision is False:
                    return decision
                from sage_extensions.logic import Predicate

                if isinstance(decision, Predicate):
                    return decision
                raise TypeError("finite-set membership must be a truth value or proposition")
            index = self._index_of_function(element)
            if index is None:
                return False
            admitted = self.index_set().is_parent_of(index)
            if admitted is not True:
                return admitted
            value = self._element_at_function(self.index_set()(index))
            return True if value is element else value == element

        # Keep an unresolved membership proposition in the owned set API.
        # Python's `in` protocol would otherwise demand a Boolean result.
        is_parent_of = __contains__

        def __call__(self, element):
            return self._element_constructor_(element)

        def _element_constructor_(self, element):
            r"""Return the member of this set that ``element`` names.

            This is the element constructor, the one boundary that admits
            foreign data, so it reads the presentation directly.  It cannot
            ask the ranking map: applying an arrow coerces its argument into
            the domain, and the domain is this parent.
            """
            decision = self.is_parent_of(element)
            if decision is False:
                raise ValueError(f"{element!r} is not in {self}")
            if decision is not True:
                raise ValueError(f"membership of {element!r} in {self} is undecided")
            index = self._index_of_function(element)
            if index is None:
                raise ValueError(f"{element!r} is not in {self}")
            admissible_index = self.index_set().is_parent_of(index)
            if admissible_index is not True:
                raise ValueError(f"the proposed index {index!r} of {element!r} is not established in {self.index_set()}")
            image = self._element_at_function(self.index_set()(index))
            equal = True if image is element else image == element
            if equal is not True:
                raise ValueError(f"the proposed index of {element!r} does not establish the forward equation")
            return image

        def _an_element_(self):
            r"""Return the first point of a nonempty enumeration."""
            for point in self:
                return point
            raise ValueError(f"{self} is empty, so it has no element")

        def _repr_(self) -> str:
            size = cardinal(self.cardinality())
            prefix = f"{self._name} = " if self._name else ""
            if size.is_finite():
                count = int(size.finite_value())
                shown = tuple(self) if count <= 12 else tuple(islice(self, 6))
                suffix = "" if count <= 12 else ", ..."
                data = "{" + ", ".join(repr(element) for element in shown) + suffix + "}"
                return f"{prefix}{data}" if count <= 12 else f"{prefix}{data} ({count} elements)"
            shown = tuple(islice(self, 6))
            data = "{" + ", ".join(repr(element) for element in shown) + ", ...}"
            return f"{prefix}{data} (cardinality {size})"


class FiniteOrderedSets(OwnedCategory):
    r"""Ordered enumerated sets over a finite index set, without sequence-valued storage.

    The datum is that of :class:`OrderedEnumeratedSets`; this category adds
    finiteness and the operations it permits.  Every other route -- a finite
    set, finitely many points, an indexed presentation -- computes that datum
    and enters through it.
    """

    def an_object(self) -> ObjectOfCategory:
        r"""The three-point ordered set."""
        return finite_ordered_set((0, 1, 2))

    def super_categories(self):
        # The owned finiteness, not Sage's: Sage's
        # ``FiniteEnumeratedSets`` supplies a ``cardinality`` returning an
        # integer, and a cardinality here is a cardinal.
        return [OrderedEnumeratedSets(), FiniteSets()]

    def _call_(self, elements: Parent | Iterable[PointT]) -> ObjectOfCategory:
        r"""Construct the finite ordered set from an enumerated set or ordered points.

        The category call returns ``elements`` itself when it already is one.
        A finite set must state its own enumeration; finitely many literal
        points are taken in order, with equal points identified.
        """
        match elements:
            case _ if elements in Sets():
                return self._on_finite_set(elements)
            case _:
                return self._on_points(elements)

    def _on_finite_set(self, source: Parent) -> ObjectOfCategory:
        r"""The finite ordered set on the points of the finite set ``source``."""
        size = cardinal(source.cardinality())
        assert size.is_finite(), (
            f"a finite ordered set needs a finite set of points, but {source} has cardinality {size}"
        )
        index_set = finite_ordinal_set(size.finite_value())
        match source:
            case _ if source in EnumeratedSets():
                # The source states its own enumeration, so both directions
                # come from that one isomorphism.
                ranking = source.ranking_map()
                return _object_of(
                    self,
                    index_set=index_set,
                    element_at=lambda position: ranking.inverse()(int(position)),
                    index_of=lambda element: ranking(element) if source.is_parent_of(element) is True else None,
                    contains=source.is_parent_of,
                )
            case _:
                # Cardinality is not an enumeration.  An arbitrary finite
                # set cannot be indexed merely because its size is known;
                # the caller must supply an actual order of its points.
                raise TypeError(
                    f"the finite set {source} has no selected enumeration; "
                    "supply its ordered points explicitly"
                )

    def _on_points(self, points: Iterable[PointT]) -> ObjectOfCategory:
        r"""The finite ordered set on finitely many points, repeated points identified.

        Literal ingress: the points are read once, in order.
        """
        # Dictionary insertion preserves the first occurrence and delegates
        # hashable-point identification to the maintained hash-table engine.
        # A genuinely unhashable point still requires the equality fallback;
        # do not impose hashability on the mathematical points of a finite set.
        supplied = tuple(points)
        try:
            distinct = tuple(dict.fromkeys(supplied))
        except (TypeError, ValueError):
            distinct_list = []
            for point in supplied:
                comparisons = tuple(
                    True if point is present else point == present
                    for present in distinct_list
                )
                if any(equal is True for equal in comparisons):
                    continue
                if any(equal is not False for equal in comparisons):
                    raise ValueError(
                        "cannot form a finite set of distinct points: equality of supplied "
                        "unhashable elements is undecided"
                    )
                distinct_list.append(point)
            distinct = tuple(distinct_list)
        return self.from_indexed(
            finite_ordinal_set(len(distinct)),
            lambda position: distinct[int(position)],
        )

    def from_indexed(
        self,
        index_set: Parent,
        element_at: Callable[[IndexT], PointT],
        *,
        index_of: Callable[[PointT], IndexT | None] | None = None,
        contains: Callable[[PointT], bool] | None = None,
        name: str | None = None,
    ) -> ObjectOfCategory:
        r"""Construct the finite ordered set enumerated by ``element_at`` on ``index_set``.

        When the points are hashable, the default inverse and membership maps
        use hash lookup. Owned mathematical objects are not required to be
        hashable, so the fallback uses equality in the selected enumeration.
        """
        assert cardinal(index_set.cardinality()).is_finite(), (
            f"a finite ordered set needs a finite index set, but {index_set} is not finite"
        )
        assert index_set in EnumeratedSets(), (
            f"a finite ordered set needs an enumerated index set, but {index_set} is not enumerated"
        )
        if index_of is None:
            indices = tuple(index_set)
            points = tuple(element_at(index) for index in indices)
            # The finite presentation has already selected its points. Keep
            # these exact objects as the forward enumeration instead of
            # re-running an arbitrary defining callback during membership,
            # ranking, and iteration. The index ranking supplies positions.
            index_ranking = index_set.ranking_map()
            element_at = lambda index: points[int(index_ranking(index))]
            # The declared enumeration must be injective. A dictionary
            # silently drops duplicate hashable points otherwise, and its
            # inverse would no longer be inverse to the chosen enumeration.
            try:
                lookup = dict(zip(points, indices, strict=True))
            except (TypeError, ValueError):
                for offset, present in enumerate(points):
                    for earlier in points[:offset]:
                        equal = True if present is earlier else present == earlier
                        if equal is True:
                            raise ValueError("an enumeration must select distinct points at distinct indices")
                        if equal is not False:
                            raise ValueError("distinctness of the enumerated points is undecided")
                def index_of(point):
                    for index, present in zip(indices, points, strict=True):
                        equal = True if point is present else point == present
                        if equal is True:
                            return index
                    return None

                # The inverse is a partial *decision* procedure. A missing
                # decided match does not refute membership when an equality
                # is unresolved. Retain the finite existential separately.
                if contains is None:
                    def contains(point):
                        from sage_extensions.logic import conjunction, negation

                        return negation(conjunction(
                            negation(True if point is present else point == present)
                            for present in points
                        ))
            else:
                if len(lookup) != len(points):
                    raise ValueError("an enumeration must select distinct points at distinct indices")
                def index_of(point):
                    try:
                        return lookup.get(point)
                    except (TypeError, ValueError):
                        # A query can have undecidable symbolic equality even
                        # when the selected points formed a valid hash table.
                        for index, present in zip(indices, points, strict=True):
                            if point is present or (point == present) is True:
                                return index
                        return None
                if contains is None:
                    def contains(point):
                        from sage_extensions.logic import conjunction, negation

                        try:
                            position = lookup.get(point)
                        except (TypeError, ValueError):
                            return negation(conjunction(
                                negation(True if point is present else point == present)
                                for present in points
                            ))
                        return position is not None
        if contains is None:
            # Membership is the domain of the selected enumeration inverse,
            # not a second independent set reconstructed from its values.
            # The inverse already uses a hash table when points are hashable,
            # and retains the necessary equality fallback otherwise. A
            # supplied inverse can be extended arbitrarily off the image;
            # only the forward equation certifies such a candidate.
            def contains(point):
                from sage_extensions.logic import AtomicProposition

                position = index_of(point)
                if position is None:
                    return False
                admitted = index_set.is_parent_of(position)
                if admitted is False:
                    return False
                if admitted is not True:
                    return AtomicProposition("is_member", point, index_set)
                image = element_at(index_set(position))
                return True if image is point else image == point
        return _object_of(
            self,
            index_set=index_set,
            element_at=element_at,
            index_of=index_of,
            contains=contains,
            name=name,
        )

    class ParentMethods:
        def random_element(self):
            r"""Sample uniformly from this nonempty finite enumerated set.

            Each point has probability 1/|X|: draw a uniform integer rank
            with Sage's pseudorandom generator and apply the inverse of
            the retained ranking map. The support is exactly this finite
            set. For a predicate subset first construct its finite
            enumeration; this method does not sample from an unbounded
            ambient set until a predicate happens to hold.

            EXAMPLES::

                sage: S = finite_ordered_set((ZZ(2), ZZ(5), ZZ(9)))
                sage: assert S.random_element() in S
                sage: assert finite_ordered_set((ZZ(7),)).random_element() == ZZ(7)
                sage: finite_ordered_set(()).random_element()
                Traceback (most recent call last):
                ...
                ValueError: cannot sample uniformly from the empty set
            """
            size = int(self.cardinality().finite_value())
            if size == 0:
                raise ValueError("cannot sample uniformly from the empty set")
            ranking = self.ranking_map()
            return ranking.inverse()(ranking.codomain()(randrange(size)))

        def filtered(self, predicate, *, name=None):
            r"""Return the ordered subset of this set cut out by ``predicate``."""
            subset = _filtered_ordered_set(self, predicate, name=name)
            assert subset is not None, (
                f"cannot enumerate the subset of {self} cut out by {predicate}: some memberships "
                "are undecided; condition_set retains this finite subset without an enumeration"
            )
            return subset

        def union(self, other):
            r"""The finite set of the points of this set and of the finite set ``other``.

            Ordered as this set, followed by the points of ``other`` not
            already present, in the order of ``other``.
            """
            assert other in Sets() and Sets().is_provably_finite(other) and other in EnumeratedSets(), (
                f"the ordered union with {self} requires a finite enumerated second set, but {other} "
                "does not supply a selected finite enumeration"
            )
            return FiniteOrderedSets()(chain(self, other))

        def intersection(self, other):
            r"""The points of this set that lie in ``other``, in this set's order."""
            from sage_extensions.categories.sets.set_categories import Sets

            if other not in Sets():
                raise TypeError(f"intersection requires a set, not {other!r}")
            return Sets().condition_set(self, lambda point: other.is_parent_of(point))

        def difference(self, other):
            r"""The points of this set that do not lie in ``other``, in this set's order."""
            from sage_extensions.logic import negation
            from sage_extensions.categories.sets.set_categories import Sets

            if other not in Sets():
                raise TypeError(f"difference requires a set, not {other!r}")
            predicate = lambda point: negation(other.is_parent_of(point))
            return Sets().condition_set(self, predicate)

        def __or__(self, other):
            return self.union(other)

        def __and__(self, other):
            return self.intersection(other)

        def __sub__(self, other):
            return self.difference(other)

        def __eq__(self, other) -> bool | Predicate:
            r"""Equal to a finite set with the same points; two finite ordered sets also agree in order."""
            from sage_extensions.logic import Predicate, conjunction

            def point_equality(left, right):
                equal = True if left is right else left == right
                match equal:
                    case True | False | Predicate():
                        return equal
                    case _:
                        raise AssertionError(
                            f"cannot compare the finite ordered sets {self} and {other}: their points "
                            f"{left!r} and {right!r} answer equality with {equal!r}, which is neither "
                            "True, False nor a proposition, so one of them is not a point that decides "
                            "its own equality"
                        )

            match other:
                case _ if other is self:
                    return True
                case _ if other in FiniteOrderedSets():
                    if self.cardinality() != other.cardinality():
                        return False
                    return conjunction(
                        point_equality(left, right)
                        for left, right in zip(self, other, strict=True)
                    )
                case _:
                    return False

        def __ne__(self, other) -> bool | Predicate:
            from sage_extensions.logic import negation

            return negation(self == other)

        def __hash__(self) -> int:
            # Do not hash members: group/lattice elements may normalize expensively.
            return hash(int(self.cardinality()))

        def _repr_(self) -> str:
            return "{" + ", ".join(repr(element) for element in self) + "}"


def _filtered_ordered_set(
    universe: Parent,
    predicate: Callable[[PointT], bool | Predicate],
    *,
    name: str | None = None,
) -> FiniteOrderedSets().ObjectType | None:
    r"""Compute the ordered subset \(\{x\in S : P(x)\}\), or decline an undecided enumeration.

    Protected construction contract (``OWN-05``), owned by
    ``FiniteOrderedSets`` and called only by its ``filtered`` operation and
    ``Sets.condition_set``.  The input is an owned finite enumerated set
    with an immutable predicate on its points.  When every value is decided,
    the result is the owned finite ordered subset, with the original
    universe, predicate and canonical inclusion retained.  ``None`` means
    only that this optional enumeration computation is unavailable; it
    makes no claim about the subset or its cardinality.

    ``Sets.condition_set`` needs this optional construction choice because
    the public ``filtered`` operation requires a represented enumeration.
    A successful computation selects the \(k\)-th satisfying point of
    \(S\), indexed by the ordinal counting those points. Its finite selected
    enumeration is materialized once, not recomputed on every rank query;
    a declined computation constructs no order.
    """
    from sage_extensions.logic import Predicate

    assert Sets().is_provably_finite(universe) and universe in EnumeratedSets(), (
        f"the subset of {universe} cut out by a condition is an ordered set only when {universe} is "
        "finite and enumerated"
    )

    selected = []
    for point in universe:
        match predicate(point):
            case True:
                selected.append(point)
            case False:
                pass
            case Predicate():
                return None
            case value:
                raise TypeError(
                    f"a subset predicate on {universe} must return True, False or a proposition, "
                    f"but returned {value!r} at {point!r}"
                )

    points = tuple(selected)
    positions = tuple(range(len(points)))
    try:
        inverse_lookup = dict(zip(points, positions, strict=True))
    except (TypeError, ValueError):
        def position_of(value):
            for i, point in enumerate(points):
                same = True if point is value else point == value
                if same is True:
                    return i
            return None
    else:
        if len(inverse_lookup) != len(points):
            raise ValueError("a filtered enumeration cannot contain duplicate points")
        def position_of(value):
            try:
                return inverse_lookup.get(value)
            except (TypeError, ValueError):
                for i, point in enumerate(points):
                    if value is point or (value == point) is True:
                        return i
                return None

    def element_at(index):
        return points[int(index)]

    def index_of(element):
        return position_of(element)

    def contains(element):
        # The selected tuple supplies an enumeration, not the definition of
        # the subset. Membership remains P(x) for x in the given universe.
        from sage_extensions.logic import AtomicProposition, Predicate

        admission = universe.is_parent_of(element)
        if admission is False:
            return False
        if admission is not True:
            return AtomicProposition("is_member", element, universe)
        decision = predicate(universe(element))
        if decision is True or decision is False or isinstance(decision, Predicate):
            return decision
        raise TypeError(
            f"a subset predicate on {universe} must return True, False or a proposition, "
            f"but returned {decision!r} at {element!r}"
        )

    return _object_of(
        FiniteOrderedSets(),
        _engine=(FiniteOrderedSets(), _FilteredOrderedSetEngine, None),
        universe=universe,
        predicate=predicate,
        index_set=finite_ordinal_set(len(points)),
        element_at=element_at,
        index_of=index_of,
        contains=contains,
        name=name,
    )


class _FilteredOrderedSetEngine:
    r"""Private computation class (``OWN-06``) of the ordered subset \(\{x\in S : P(x)\}\).

    The datum this class keeps is \((S, P)\); the inclusion into \(S\) is
    the subobject the set is.
    """

    def __init__(self, universe: Parent, predicate: Callable[[PointT], bool], **rest) -> None:
        self._universe = universe
        self._predicate = predicate
        super().__init__(**rest)

    def universe(self) -> Sets().ObjectType:
        r"""The set \(S\) this subset is cut out of."""
        return self._universe

    def predicate(self) -> Callable[[PointT], bool]:
        r"""The predicate \(P\) cutting this subset out of \(S\)."""
        return self._predicate

    @cached_method
    def inclusion(self):
        r"""The inclusion \(\{x\in S : P(x)\}\hookrightarrow S\)."""
        return Sets().Mono(self, self.universe())._from_subset_inclusion()

    def __iter__(self):
        return (self.enumeration()(index) for index in self.index_set())

    def _repr_(self):
        return self._name or f"Ordered subset of {self.universe()}"


def _enumerated_image_set(
    source: Sets().ObjectType,
    map_: Callable[[IndexT], PointT],
    inverse: Callable[[PointT], IndexT | None],
) -> OrderedEnumeratedSets().ObjectType:
    r"""An injective image, constructed by the ordered enumerated sets owner.

    No category of images is introduced.  The source, map and inverse are
    exactly the index set and the two directions of the enumeration.  In the
    infinite case the supplied inverse is a decision extension: it returns
    ``None`` on candidates for which no preimage is represented.  Membership
    also checks the forward equation, so a total extension of an inverse
    cannot admit values outside the image.

    Unexecuted separating specimen: for a finite source with an inverse
    returning the correct preimage or ``None``, querying an absent value
    invokes that inverse and never compares the candidate with every image
    value. A total inverse extension selecting a source point for an absent
    value is rejected by the forward equation. Both conditions apply equally
    to finite and infinite index sets.
    """
    match source:
        case _ if Sets().is_provably_finite(source):
            placement = FiniteOrderedSets()
        case _:
            # The image of an infinite set under an injection is infinite.
            placement = (
                owned_category_join((OrderedEnumeratedSets(), Sets().Infinite()))
                if source in Sets().Infinite()
                else OrderedEnumeratedSets()
            )


    def contains(value):
        # A supplied inverse determines image membership for finite as well
        # as infinite sources. Scanning the finite source would discard that
        # map and incorrectly turn membership into an enumeration algorithm.
        preimage = inverse(value)
        if preimage is None:
            return False
        admitted = source.is_parent_of(preimage)
        if admitted is not True:
            return admitted
        image = map_(source(preimage))
        return True if image is value else image == value

    return _object_of(
        placement,
        _engine=(placement, _EnumeratedImageSetEngine, None),
        index_set=source,
        element_at=map_,
        index_of=inverse,
        contains=contains,
    )


class _EnumeratedImageSetEngine:
    r"""Private computation class (``OWN-06``) of an injective image enumerated by its source."""

    def source_set(self) -> Sets().ObjectType:
        r"""The source of the injective map presenting this image."""
        return self.index_set()

    def image_map(self) -> Callable[[IndexT], PointT]:
        r"""The map presenting this image, which is its enumeration."""
        return self.enumeration()

    def inverse_on_image(self) -> Callable[[PointT], IndexT | None]:
        r"""The selected inverse of the image map."""
        return self.enumeration_inverse()

    def is_injective_image(self) -> bool:
        r"""The supplied inverse satisfies ``g(f(a)) = a`` on the source."""
        return True


def finite_ordered_set[PointT](
    elements: Parent | Iterable[PointT],
) -> FiniteOrderedSets().ObjectType:
    r"""The finite ordered set a finite set or finitely many points present."""
    return FiniteOrderedSets()(elements)
