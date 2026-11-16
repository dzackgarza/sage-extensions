"""Owned ordered enumerated sets, with the finite ones as a refinement."""

from __future__ import annotations

import weakref
from collections.abc import Callable, Iterable
from itertools import chain, islice
from typing import TYPE_CHECKING, TypeVar

from sage.categories.category import Category
from sage.misc.cachefunc import cached_function, cached_method
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


class _PointsAreEqual:
    r"""The default equivalence of an ordered set: two points are equivalent when they are equal.

    An ordered set retains its equivalence on the parent, and a parent must survive
    a pickle round trip, so the default is a module-level object rather than a
    closure.  It carries no state.
    """

    def __call__(self, left, right):
        return left == right

    def __repr__(self) -> str:
        return "point equality"


_DEFAULT_EQUIVALENCE = _PointsAreEqual()


class _PointSequence:
    r"""The points of a finite ordered set, in order, and the hash of that tuple.

    A finite ordered set *is* its point sequence (the rule of
    :class:`FiniteOrderedSets`): equality compares those points position by
    position and the hash is the hash of the tuple.  So the tuple is one datum
    of the set, and one object per point sequence is kept alive by the sets that
    hold it (``_interned_point_sequence``).  Two equal sets then hold the *same*
    object, so deciding that they are equal -- which the store of finite
    products and coproducts does for every factor of every family it places
    (``set_categories._finite_family_key``, `SET-05`) -- reads no point, at any
    size.

    ``digest`` is that tuple's hash, decided when the sequence is made, so a
    reader of it never walks the points.  It is ``None`` when a point refuses a
    hash: the set is then unhashable, exactly as ``hash(tuple(self))`` is, and
    its sequence is not interned, because the registry is keyed by the digest.
    """

    __slots__ = ("points", "digest", "__weakref__")

    def __init__(self, points: tuple[PointT, ...], digest: int | None) -> None:
        self.points = points
        self.digest = digest

    def __reduce__(self):
        # A sequence is the one object its points name, so it is rebuilt through
        # the registry rather than copied: two sets that held one sequence still
        # hold one sequence after a round trip.
        return (_interned_point_sequence, (self.points,))


# A sequence is held by the sets that hold it, not by this registry: an entry is
# a weak reference, and one that has died is dropped the next time its bucket is
# visited.
_POINT_SEQUENCES: dict[int, list[weakref.ref]] = {}


def _point_equality(left: PointT, right: PointT) -> bool | Predicate:
    r"""Whether two points of a finite ordered set are equal.

    ``True``, ``False``, or the proposition the points answer: the equality of
    some points of this library is itself a statement, and a comparison that
    reported one of the two answers would decide it.
    """
    from sage_extensions.logic import Predicate

    equal = True if left is right else left == right
    match equal:
        case True | False | Predicate():
            return equal
        case _:
            raise AssertionError(
                f"cannot compare the points {left!r} and {right!r} of a finite ordered set: "
                f"they answer equality with {equal!r}, which is neither True, False nor a "
                "proposition, so one of them is not a point that decides its own equality"
            )


def _point_sequence_equality(left: tuple[PointT, ...], right: tuple[PointT, ...]) -> bool | Predicate:
    r"""Whether two point sequences agree, position by position."""
    if len(left) != len(right):
        return False
    for one, other in zip(left, right):
        equal = _point_equality(one, other)
        if equal is not True:
            return equal
    return True


def _interned_point_sequence(points: tuple[PointT, ...]) -> _PointSequence:
    r"""The one point sequence this tuple of points is.

    Two finite ordered sets built separately from equal points reach this with
    equal tuples, and the second is answered with the first one's sequence: that
    one object is what their equality is decided by, and no reader walks the
    points of either again.  A bucket is keyed by the tuple's hash, which equal
    sequences share; a bucket holding a second sequence is a collision, and it is
    resolved by comparing the points, so two sequences are one object exactly
    when they are equal.

    A sequence containing a point that refuses a hash has no digest to be looked
    up by and is not interned: nothing is decided for it, and its set is
    unhashable, as the tuple's hash is.
    """
    try:
        digest = hash(points)
    except TypeError:
        return _PointSequence(points, None)
    bucket = _POINT_SEQUENCES.get(digest)
    if bucket is not None:
        live = []
        for reference in bucket:
            sequence = reference()
            if sequence is None:
                continue
            live.append(reference)
            if _point_sequence_equality(sequence.points, points) is True:
                _POINT_SEQUENCES[digest] = live
                return sequence
        bucket[:] = live
    sequence = _PointSequence(points, digest)
    _POINT_SEQUENCES.setdefault(digest, []).append(weakref.ref(sequence))
    return sequence


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
        equivalent: Callable[[PointT, PointT], bool] | None = None,
        name: str | None = None,
        description: Callable[[], str] | None = None,
    ) -> Sets().ObjectType:
        r"""Construct an ordered enumerated set from its chosen enumeration."""
        assert index_set in EnumeratedSets(), (
            f"an ordered set is indexed by an enumerated set, but {index_set} is not enumerated"
        )
        match index_set:
            case _ if Sets().is_provably_finite(index_set):
                return FiniteOrderedSets().from_indexed(
                    index_set, element_at, index_of=index_of, contains=contains,
                    equivalent=equivalent, name=name, description=description
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
            description=description,
        )

    class ParentMethods:
        def __init__(
            self,
            index_set: Parent,
            element_at: Callable[[IndexT], PointT],
            *,
            index_of: Callable[[PointT], IndexT | None],
            contains: Callable[[PointT], bool] | None = None,
            equivalent: Callable[[PointT, PointT], bool] | None = None,
            name: str | None = None,
            description: Callable[[], str] | None = None,
            point_sequence: _PointSequence | None = None,
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
            if name is not None and description is not None:
                raise ValueError(
                    f"the set of {index_set} is given both the name {name!r} and a description "
                    f"function: a set is named or described, and one of the two would be lost"
                )
            self._index_set = index_set
            self._element_at_function = element_at
            self._index_of_function = index_of
            self._contains_function = contains
            self._equivalent_function = equivalent or _DEFAULT_EQUIVALENCE
            self._name = name
            self._description_function = description
            self._point_sequence = point_sequence
            super().__init__(facade=True, **rest)

        def index_set(self) -> Sets().ObjectType:
            return self._index_set

        def enumeration(self) -> Callable[[IndexT], PointT]:
            r"""The chosen bijection from the index set onto this set."""
            return self._element_at_function

        def enumeration_inverse(self) -> Callable[[PointT], IndexT | None]:
            r"""The chosen inverse on this set, with ``None`` allowed off it."""
            return self._index_of_function

        def point_sequence(self) -> _PointSequence:
            r"""The points of this set, in order, with their hash, as one object.

            A construction that read a finite ordered set's points hands them to
            the set here, and the set's hash is the hash of that tuple.  A
            presentation that builds its points on demand -- an image under a
            map, the ordering of a finite set by its ranking, a subobject on
            given positions -- reads none of them, and this reads them once, on
            the first ask, and keeps them: a second reader asks nothing.

            Two equal sets answer with one object (``_interned_point_sequence``),
            which is what makes their equality an identity test rather than a
            walk of their points.
            """
            decided = self._point_sequence
            if decided is None:
                decided = self._point_sequence = _interned_point_sequence(tuple(self))
            return decided

        def __iter__(self):
            r"""Iterate through the chosen enumeration.

            This category already stores the bijection ``I -> X`` as its
            defining datum.  Iteration therefore evaluates that map on the
            represented index set directly; the categorical ranking
            isomorphism is needed when the isomorphism itself is requested,
            not to read the enumeration it represents.

            A set that holds its points -- every set whose construction read
            them, and every set whose first hash did -- reads them back and
            runs no map at all.

            The standard finite ordinal is the one self-indexed construction:
            its index set is literally itself and its selected enumeration is
            the identity on ``0, ..., n-1``.  Read those positions from its
            finite cardinality rather than recursively asking it to iterate.
            """
            element_at = self.enumeration()
            index_set = self.index_set()
            decided = self._point_sequence
            if decided is not None:
                return iter(decided.points)
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
            equal = True if image is element else self._equivalent_function(image, element)
            if equal is not True:
                raise ValueError(f"the proposed index of {element!r} does not establish the forward equation")
            return image

        def _an_element_(self):
            r"""Return the first point of a nonempty enumeration."""
            for point in self:
                return point
            raise ValueError(f"{self} is empty, so it has no element")

        @cached_method
        def description(self):
            r"""What this set was named or described with, rendered on the first read and kept.

            A set is given a name, or a description of the source it was carved out
            of, and a construction that states both is refused: one of the two would
            be lost.  Rendering the description is the reader's act: the set asks it
            here, and not at construction, so building the set computes no display.
            Neither answer changes while the set exists, so a second reader asks
            nothing.
            """
            described = self._description_function
            if described is not None:
                return described()
            return self._name

        def _repr_(self) -> str:
            size = cardinal(self.cardinality())
            described = self.description()
            prefix = f"{described} = " if described else ""
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

    The points of a finite ordered set are values: each one hashes, and its
    hash agrees with its equality.  A set is fixed by its points, and what is
    keyed by a set or by its points -- the inverse of its enumeration, which is
    a hash table of the points; an interned label set -- is correct only while
    the points cannot change and their hashes agree with their equality.  A
    point that refuses a hash is mutable, as a Python list
    or a mutable Sage vector is, and then the value is its tuple or the vector
    after ``set_immutable()``; or its owner computes no hash for it, and a
    constant hash agrees with every equality.  The constructions that build the
    hash table of the points refuse such a point, with the table's
    ``TypeError``.

    A finite ordered set is its point sequence, so the tuple of its points is
    the datum its equality compares and its hash reads, and a set that has read
    its points holds both: the tuple, and its hash.  One object stands for one
    point sequence (``_interned_point_sequence``), so two equal sets hold the
    same tuple and are equal by an identity test.  The product and coproduct of
    a family are interned under their index set and their factors' hashes
    (``set_categories._finite_family_key``), so placing a family reads a value
    each factor holds and confirms its equality without reading a point of it,
    at any size.  No caller supplies that value: a datum other than the
    points cannot key a set, because two sets of one point sequence would then
    be unequal while remaining equal to every set of those points, and one
    family would have two constructions (`SET-05`).

    Which constructions read their points, and which leave it to the first
    reader, is the cost of the set and not of its mathematics.
    ``from_indexed`` and the filtered subset read them and hand them over; a
    presentation whose points are built on demand -- an image under a map, the
    ordering of a finite set by its ranking, a subobject on given positions --
    reads none, and the first ask for its hash or its sequence reads them once
    and keeps them.  A finite ordered set that has not read its points cannot
    answer with their hash, because the hash of a set is a function of its
    points and nothing weaker; what a key costs is the second read, and a set
    that has read its points is never read twice.
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
            case _ if elements in self:
                # Preserve the literal selected index set. Rewrapping an
                # existing finite ordered set through its underlying Set
                # presentation replaces its chosen labels by a new ordinal
                # indexing and breaks constructors that retain this framing.
                return elements
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
        # The points hash (the rule of this category), so dictionary insertion
        # identifies repeated points and keeps the first occurrence.
        distinct = tuple(dict.fromkeys(points))
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
        equivalent: Callable[[PointT, PointT], bool] | None = None,
        name: str | None = None,
        description: Callable[[], str] | None = None,
    ) -> ObjectOfCategory:
        r"""Construct the finite ordered set enumerated by ``element_at`` on ``index_set``.

        The default inverse is a hash table of the points, which hash by the
        rule of :class:`FiniteOrderedSets`, and membership is that inverse's
        domain.

        The construction reads the points here, whichever inverse it was given:
        they are the set's own enumeration, its hash is the hash of that tuple,
        and the tuple is interned, so a second set of the same points is the same
        point sequence and the two compare by identity.  A supplied inverse is
        kept as the set's inverse, and the objects this construction selected are
        its iteration from then on, so no reader runs the defining map again.
        """
        assert cardinal(index_set.cardinality()).is_finite(), (
            f"a finite ordered set needs a finite index set, but {index_set} is not finite"
        )
        assert index_set in EnumeratedSets(), (
            f"a finite ordered set needs an enumerated index set, but {index_set} is not enumerated"
        )
        indices = tuple(index_set)
        points = tuple(element_at(index) for index in indices)
        point_sequence = _interned_point_sequence(points)
        if index_of is None:
            # These retained objects already satisfy the chosen enumeration.
            # Their admission does not need equality with other points.
            identity_indices = {id(point): index for point, index in zip(points, indices, strict=True)}
            # The finite presentation has already selected its points. Keep
            # these exact objects as the forward enumeration instead of
            # re-running an arbitrary defining callback during membership,
            # ranking, and iteration. The index ranking supplies positions.
            index_ranking = index_set.ranking_map()
            element_at = lambda index: points[int(index_ranking(index))]
            # The declared enumeration must be injective: the table identifies
            # equal points, so a repeated point leaves it smaller than the
            # enumeration, and its inverse would not be inverse to it.
            lookup = dict(zip(points, indices, strict=True))
            if len(lookup) != len(points):
                raise ValueError("an enumeration must select distinct points at distinct indices")
            # A candidate is looked up in the table, so one that refuses a hash,
            # or whose equality with a point of its hash is undecided, raises
            # the table's TypeError, as ``[0] in {}`` does.
            def index_of(point):
                retained = identity_indices.get(id(point))
                if retained is not None:
                    return retained
                return lookup.get(point)
            if contains is None:
                def contains(point):
                    return id(point) in identity_indices or point in lookup
        if contains is None:
            # Membership is the domain of the selected enumeration inverse,
            # not a second independent set reconstructed from its values. A
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
            equivalent=equivalent,
            name=name,
            description=description,
            point_sequence=point_sequence,
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

        def filtered(self, predicate, *, name=None, description=None):
            r"""Return the ordered subset of this set cut out by ``predicate``."""
            subset = _filtered_ordered_set(
                self, predicate, name=name, description=description
            )
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
            r"""Equal to a finite set with the same points; two finite ordered sets also agree in order.

            Equality is extensional and reads nothing but the points: a finite
            ordered set is its point sequence, so two sets are equal exactly when
            their points agree, position by position.  Nothing else about how
            either set was constructed takes part, which is what makes ``==`` an
            equivalence relation here -- two sets equal to a third are equal to
            each other -- and what lets the hash, which is the hash of those
            points, agree with it (``SET-05``).

            Two sets that hold their points hold one tuple when their sequences
            are equal (``_interned_point_sequence``), so equal sets are decided
            here by one identity test however many points they have.  A set that
            holds no tuple yet, or a pair whose points answer with a proposition,
            is compared point by point.
            """
            from sage_extensions.logic import conjunction

            match other:
                case _ if other is self:
                    return True
                case _ if other in FiniteOrderedSets():
                    if self.cardinality() != other.cardinality():
                        return False
                    held = self._point_sequence
                    if held is not None and held is other._point_sequence:
                        return True
                    return conjunction(
                        _point_equality(left, right)
                        for left, right in zip(self, other, strict=True)
                    )
                case _:
                    return False

        def __ne__(self, other) -> bool | Predicate:
            from sage_extensions.logic import negation

            return negation(self == other)

        def __hash__(self) -> int:
            r"""Return the hash of the point sequence this set holds, which :meth:`__eq__` compares.

            The points of a finite ordered set are values, so the set is fixed by
            them and this hash does not change: it is the hash of the tuple of the
            points, decided with that tuple (``_interned_point_sequence``) when
            the construction read them, or when the first reader asked.  Reading
            it therefore reads no point, which is what the store of finite
            products and coproducts does for every factor of every family it
            places (`SET-05`); ``STY-55``'s repeated derivation is the
            question this answers once.

            The points hash and their hashes agree with their equality (the rule
            of :class:`FiniteOrderedSets`), so equal sets hash equally, and a set
            carrying a point that refuses a hash refuses one too: the tuple's own
            hash raises, and no sequence is kept for it.
            """
            decided = self.point_sequence()
            if decided.digest is None:
                # The sequence was made without a digest because a point refused
                # a hash; asking again raises the TypeError that point raises.
                return hash(decided.points)
            return decided.digest

        def _repr_(self) -> str:
            return "{" + ", ".join(repr(element) for element in self) + "}"


def _filtered_ordered_set(
    universe: Parent,
    predicate: Callable[[PointT], bool | Predicate],
    *,
    name: str | None = None,
    description: Callable[[], str] | None = None,
) -> FiniteOrderedSets().ObjectType | None:
    r"""Compute the ordered subset \(\{x\in S : P(x)\}\), or decline an undecided enumeration.

    Protected construction contract (``OWN-05``), owned by
    ``FiniteOrderedSets`` and called only by its ``filtered`` operation and
    ``Sets.condition_set``.  The input is an owned finite enumerated set
    with an immutable predicate on its points.  When every value is decided,
    the result is the owned finite ordered subset, with the original
    universe, predicate and canonical inclusion retained.  A description given
    as a function is rendered when a reader asks for the subset's description
    and not when the subset is built.  ``None`` means
    only that this optional enumeration computation is unavailable; it
    makes no claim about the subset or its cardinality.

    ``Sets.condition_set`` needs this optional construction choice because
    the public ``filtered`` operation requires a represented enumeration.
    A successful computation selects the \(k\)-th satisfying point of
    \(S\), indexed by the ordinal counting those points. Its finite selected
    enumeration is materialized once, not recomputed on every rank query; that
    selection is the subset's point sequence, so its hash is the hash of those
    points and no reader walks them again; a declined computation
    constructs no order.
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
    # The points hash (the rule of FiniteOrderedSets), so the inverse is a table.
    inverse_lookup = dict(zip(points, positions, strict=True))
    if len(inverse_lookup) != len(points):
        raise ValueError("a filtered enumeration cannot contain duplicate points")
    def element_at(index):
        return points[int(index)]

    def index_of(element):
        # A candidate that refuses a hash, or whose equality is undecided,
        # raises the table's TypeError, as ``[0] in {}`` does.
        return inverse_lookup.get(element)

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
        description=description,
        point_sequence=_interned_point_sequence(points),
    )


class _OrderedSubsetEngine:
    r"""A subobject of a finite enumerated set, enumerated by the selection it retains.

    Shared realization of the subset engines below: a subset of a finite
    enumerated set is itself an ordered set, whose enumeration is the selection
    the construction retained, and whose inclusion into the universe is the
    subobject it is.  Each engine supplies that selection and the decision of
    membership in it, so the two differ only in how membership is decided.
    """

    def universe(self) -> Sets().ObjectType:
        r"""The set \(X\) this subset is cut out of."""
        return self._universe

    @cached_method
    def inclusion(self):
        r"""The inclusion of this subset into the set it is cut out of."""
        return Sets().Mono(self, self.universe())._from_subset_inclusion()

    def __iter__(self):
        return (self.enumeration()(index) for index in self.index_set())

    def _repr_(self) -> str:
        described = self.description()
        return described if described else f"Ordered subset of {self.universe()}"


class _FilteredOrderedSetEngine(_OrderedSubsetEngine):
    r"""Private computation class (``OWN-06``) of the ordered subset \(\{x\in S : P(x)\}\).

    The datum this class keeps is \((S, P)\); the inclusion into \(S\) is
    the subobject the set is.
    """

    def __init__(self, universe: Parent, predicate: Callable[[PointT], bool], **rest) -> None:
        self._universe = universe
        self._predicate = predicate
        super().__init__(**rest)

    def predicate(self) -> Callable[[PointT], bool]:
        r"""The predicate \(P\) cutting this subset out of \(S\)."""
        return self._predicate


def _subset_on_positions(
    universe: Parent,
    positions: Iterable[int],
    *,
    description: Callable[[], str] | None = None,
) -> FiniteOrderedSets().ObjectType:
    r"""The subobject of ``universe`` on the given positions, with its inclusion.

    Protected construction contract (``OWN-05``), owned by ``FiniteOrderedSets``
    and called only by an operation that already retains a selection of a finite
    enumeration.  The defining datum is that selected enumeration: the points at
    the given positions of ``universe``, in the order of ``universe``.  The
    construction asks nothing about any point of ``universe``, so it costs what
    reading the selection costs; a description given as a function is rendered
    when a reader asks for the subset's description, as every named or described
    order is.

    A block of a partition of a finite enumerated set is the case this exists
    for.  The partition is computed once, as the label of each position, and each
    block is then the subobject on the positions carrying that label.  A subset
    cut out point by point instead decides its membership predicate on every
    point of the universe, once for each block.

    Membership is membership of a point's position in the selection, which is the
    question ``universe`` decides, and a point's index is its position's rank in
    the selection, so the enumeration and membership cannot disagree.  A position
    outside ``universe`` is refused rather than silently dropped: it is not a
    position of the enumeration being selected from.
    """
    assert Sets().is_provably_finite(universe) and universe in EnumeratedSets(), (
        f"a subset on given positions needs a finite enumerated universe, but {universe} is not one"
    )
    selected = tuple(int(position) for position in positions)
    size = int(cardinal(universe.cardinality()).finite_value())
    assert all(0 <= position < size for position in selected), (
        f"the positions {selected} are not positions of the {size} points of {universe}"
    )
    ranking = universe.ranking_map()
    ranks = frozenset(selected)
    order = {position: index for index, position in enumerate(selected)}

    def element_at(index):
        return universe[selected[int(index)]]

    def index_of(element):
        return order.get(int(ranking(element)))

    def contains(element):
        admission = universe.is_parent_of(element)
        if admission is not True:
            return admission
        return int(ranking(element)) in ranks

    return _object_of(
        FiniteOrderedSets(),
        _engine=(FiniteOrderedSets(), _SubsetOnPositionsEngine, None),
        universe=universe,
        positions=selected,
        index_set=finite_ordinal_set(len(selected)),
        element_at=element_at,
        index_of=index_of,
        contains=contains,
        description=description,
    )


class _SubsetOnPositionsEngine(_OrderedSubsetEngine):
    r"""Private computation class (``OWN-06``) of the ordered subobject on positions.

    The datum this class keeps is \((X, P)\): the finite enumerated set \(X\) and
    the selected positions \(P\) of \(X\), which are the enumeration of the
    subset.  The inclusion into \(X\) is the subobject the set is.
    """

    def __init__(self, universe: Parent, positions: tuple[int, ...], **rest) -> None:
        self._universe = universe
        self._positions = positions
        super().__init__(**rest)

    def positions(self) -> tuple[int, ...]:
        r"""The positions of \(X\) this subset selects, in the order of \(X\)."""
        return self._positions


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


@cached_function(key=lambda labels: labels)
def interned_finite_ordered_set(labels):
    r"""The one finite ordered set an ordered tuple of labels names.

    A free module's framing records the *actual* label set it was constructed
    on, so two separately built sets of the same labels give two modules and
    therefore two algebras out of one datum: ``R[x, y]``,
    ``R.free_module(("x", "y")).symmetric_algebra()`` and ``R["x,y"]`` are one
    object only if they reach one label set (``OWN-02``).  Interning the set
    constructor is where that identity belongs: the datum is the ordered
    labels, not the Python object that carried them in.

    The labels are the points of the set, so they hash (the rule of
    :class:`FiniteOrderedSets`) and key the cache by value.
    """
    return finite_ordered_set(labels)

