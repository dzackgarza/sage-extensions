r"""Owned topological spaces and continuous maps.

A topological space is a set together with a topology; a morphism is a
continuous set map.  The general public constructor implemented here is the
exact finite case, where the topology axioms and continuity are decidable by
enumeration.  Infinite geometric realizations (manifolds and scheme
underlying spaces) supply private topology data to this same owner and may
assert at the computational frontier when arbitrary openness is not
represented.
"""

from itertools import combinations

from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.set_categories import (
    EnumeratedSets,
    FiniteSets,
    Sets,
)
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.logic import AtomicProposition, conjunction
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def _members_of_subset(base_set, candidate):
    r"""The members of ``candidate <= base_set`` in the order of ``base_set``."""

    subset = base_set.power_set()(candidate)
    return tuple(point for point in base_set if point in subset)


class _FiniteTopologyData(SageObject):
    r"""The exact topology on a finite enumerated set, retained by its opens."""

    def __init__(self, point_set, open_subsets) -> None:
        assert point_set in FiniteSets() and point_set in EnumeratedSets(), (
            f"cannot check the topology axioms for a topology on {point_set}: they are "
            f"checked only for a finite enumerated set of points, and {point_set} is in "
            f"{point_set.category()}"
        )
        opens = []
        for candidate in open_subsets:
            members = _members_of_subset(point_set, candidate)
            if members not in opens:
                opens.append(members)
        self._point_set = point_set
        self._open_member_families = tuple(opens)
        self._verify_topology_axioms()

    def point_set(self):
        return self._point_set

    def _union(self, left, right):
        return tuple(
            point
            for point in self.point_set()
            if point in left or point in right
        )

    def _intersection(self, left, right):
        return tuple(
            point
            for point in self.point_set()
            if point in left and point in right
        )

    def _verify_topology_axioms(self) -> None:
        opens = self._open_member_families
        empty = ()
        whole = tuple(self.point_set())
        if empty not in opens or whole not in opens:
            raise ValueError(
                f"the subsets {opens} of {self.point_set()} are not a topology: a topology "
                f"must contain the empty set and the whole space"
            )
        for left in opens:
            for right in opens:
                if self._intersection(left, right) not in opens:
                    raise ValueError(
                        f"the subsets {opens} of {self.point_set()} are not a topology: the "
                        f"intersection of the open sets {left} and {right} is not open"
                    )
                if self._union(left, right) not in opens:
                    raise ValueError(
                        f"the subsets {opens} of {self.point_set()} are not a topology: the "
                        f"union of the open sets {left} and {right} is not open"
                    )

    def open_subsets(self, space):
        r"""The open sets of ``space``, the points of ``space`` at the members of each open of ``tau``."""
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, candidate) -> bool:
        r"""Whether the subset ``candidate`` of ``space`` is the image of an open of ``tau``."""
        index_of = space.enumeration_inverse()
        members = tuple(index_of(point) for point in _members_of_subset(space, candidate))
        return members in self._open_member_families


class _FiniteSpacePoint:
    r"""A point of a finite space ``X = (S, tau)``: the point of ``X`` at a point ``s`` of ``S``."""

    def __init__(self, parent, index) -> None:
        self._index = index
        super().__init__(parent)

    def index(self):
        r"""The point ``s`` of ``S`` at which the enumeration ``S -> X`` places this point."""
        return self._index

    def _repr_(self) -> str:
        return repr(self._index)

    def __eq__(self, other) -> bool:
        r"""Equal to the point of the same space at the same point of ``S``.

        The points of two spaces on one ``S`` are different points, so a datum
        of another parent is unequal here rather than sent through coercion.
        """
        return element_parent(other) is self.parent() and other.index() == self.index()

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(self._index)


class _FiniteTopologicalSpaceEngine:
    r"""A finite topological space ``X = (S, tau)``, constructed on its set of points ``S``.

    A topology is chosen structure: many topologies sit on one ``S``, so each
    space is its own object with its own points.  The set level of ``X`` is the
    finite ordered set enumerated by ``S``, whose point at ``s`` is the point
    of ``X`` at ``s``; its finiteness, counting well-order and cardinality are
    the ones that level derives from ``S``.  A point of ``S`` names a point of
    ``X`` through that enumeration, which is the element constructor of ``X``.
    ``S`` is retained as defining data, and this level adds only ``tau``.
    """

    _derived_construction_parameters = frozenset({"index_set", "element_at", "index_of"})

    def __init__(self, point_set, **rest) -> None:
        super().__init__(
            index_set=point_set,
            element_at=self._point_at,
            index_of=self._index_of,
            **rest,
        )

    def _point_at(self, index):
        r"""The point of ``X`` at the point ``index`` of ``S``."""
        return self.element_class(self, index)

    def _index_of(self, datum):
        r"""The point of ``S`` that names ``datum``, or ``None`` when ``datum`` names no point of ``X``."""
        match datum:
            case _ if element_parent(datum) is self:
                return datum.index()
            case _ if datum in self.index_set():
                return self.index_set()(datum)
            case _:
                return None

    def _element_constructor_(self, datum):
        r"""The point of ``X`` that ``datum`` names: a point of ``X``, or the point at a point of ``S``.

        A point of ``S`` is not a point of ``X``, so it is not a member here;
        the enumeration ``S -> X`` sends it to the point it names.
        """
        index = self._index_of(datum)
        assert index is not None, f"{datum!r} names no point of {self}"
        return self._point_at(index)

    def unstructured_set(self):
        r"""The set ``S`` on which this topology was placed, retained as defining data."""
        return self.index_set()

    underlying_set = unstructured_set


class _FinalTopologyData(SageObject):
    r"""The final topology on a set ``Q`` along a set map ``q: UY -> Q``.

    A subset ``V`` of ``Q`` is open exactly when ``q^{-1}(V)`` is open in
    ``Y``; it is the finest topology on ``Q`` making ``q`` continuous
    (Mathlib, ``TopologicalSpace.coinduced``).  Openness is asked of ``Y``
    on the preimage, so it is decided wherever ``Y`` decides it.
    """

    def __init__(self, source_space, set_projection) -> None:
        self._source_space = source_space
        self._set_projection = set_projection

    def open_subsets(self, space):
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset) -> bool:
        selected = space.power_set()(subset)
        projection = self._set_projection
        preimage = self._source_space.power_set().from_predicate(
            lambda point: projection(point) in selected
        )
        return self._source_space.is_open_subset(preimage)


class _CoproductTopologyData(SageObject):
    r"""The final topology along the injections into a disjoint union.

    A subset is open exactly when its trace on each summand is open.
    Reference: Mathlib.Topology.Category.TopCat.Limits.Basic,
    ``TopCat.isOpen_iff_of_isColimit``.
    """

    def __init__(self, factors, point_set) -> None:
        self._factors = factors
        self._point_set = point_set

    def open_subsets(self, space):
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset):
        power = space.power_set()
        selected = power(subset)
        if selected is power.top() or selected is power.bottom():
            return True
        indices = self._factors.index_set()
        if not Sets().is_provably_finite(indices) or indices not in EnumeratedSets():
            return AtomicProposition("is_open_subset", space, selected)

        def trace_is_open(index):
            factor = self._factors[index]
            injection = self._point_set.injection(index)
            trace = factor.power_set().from_predicate(
                lambda point: injection(point) in selected
            )
            return factor.is_open_subset(trace)

        return conjunction(trace_is_open(index) for index in indices)


class _TransportedTopologyData(SageObject):
    r"""The topology of a space ``X`` on a set with the same points as ``X``.

    A subset is open exactly when the subset of ``X`` with the same points is
    open in ``X``: the final topology along the identity of points.  When the
    opens of ``X`` form a finite enumerated set, they are enumerated here.
    """

    def __init__(self, source_space) -> None:
        self._source_space = source_space

    def open_subsets(self, space):
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset) -> bool:
        selected = space.power_set()(subset)
        source = self._source_space
        return source.is_open_subset(source.power_set().from_predicate(lambda point: point in selected))


class _FinalTopologySpaceEngine:
    r"""A set ``Q`` with the final topology along ``q: UY -> Q``.

    The topology is chosen structure on ``Q``, so the space is its own object;
    its points are the points of ``Q``, which is retained as defining data.
    """

    def __init__(self, point_set, **rest) -> None:
        self._point_set = point_set
        super().__init__(facade=point_set, **rest)

    def unstructured_set(self):
        r"""The set ``Q`` on which the final topology was placed."""
        return self._point_set

    underlying_set = unstructured_set

    def __contains__(self, point) -> bool:
        return point in self._point_set

    is_parent_of = __contains__

    def _element_constructor_(self, datum):
        return self._point_set(datum)

    def cardinality(self):
        return self._point_set.cardinality()

    def _repr_(self) -> str:
        return f"{self._point_set} with the final topology"


class _OrbitSpaceEngine(_FinalTopologySpaceEngine):
    r"""The orbit space ``G\X``: the orbit set of ``UX`` with the final topology along ``q``.

    The ``G``-space ``X`` is retained as defining data, so the space is named
    by the action it is the quotient of.
    """

    def __init__(self, g_space, **rest) -> None:
        self._g_space = g_space
        super().__init__(**rest)

    def g_space(self):
        r"""The ``G``-space ``X`` whose orbit space this is."""
        return self._g_space

    def _repr_(self) -> str:
        from sage_extensions.categories.manifolds import TopologicalManifolds

        g_space = self.g_space()
        group = g_space.acting_group()
        match g_space:
            case _ if g_space in TopologicalManifolds():
                name = g_space.manifold_name()
                return f"{group}\\{name}, the orbit space of the {group}-action on {name}"
            case _:
                return f"The orbit space of {g_space}"


def _final_topology_space(source_space, set_projection, *, category, engine, **engine_data):
    r"""Return ``(Q, q, rho)``: ``Q`` the codomain of ``set_projection`` with its final topology.

    ``q: Y -> Q`` is the continuous map whose underlying set map is
    ``set_projection``, and ``rho`` sends a point of the space ``Q`` to the
    point of the underlying set it names.  A finite enumerated ``Q`` receives
    its exact finite topology, whose opens are enumerated; any other ``Q``
    receives the final topology data, which asks ``Y`` about preimages.
    ``category`` is the subcategory of ``TopologicalSpaces()`` the caller's
    construction places ``Q`` in, ``engine`` the computation class serving
    it, and ``engine_data`` the data that class introduces.
    """
    point_set = set_projection.codomain()
    match Sets().is_provably_finite(point_set) and point_set in EnumeratedSets():
        case True:
            members = tuple(point_set)
            source_power = source_space.power_set()
            opens = tuple(
                selected
                for size in range(len(members) + 1)
                for selected in combinations(members, size)
                if source_space.is_open_subset(
                    source_power.from_predicate(
                        lambda point, chosen=selected: set_projection(point) in chosen
                    )
                )
                is True
            )
            assert category is TopologicalSpaces(), (
                f"cannot place the finite quotient {point_set} of {source_space} in "
                f"{category}: a finite space with its enumerated final topology is "
                f"constructed in {TopologicalSpaces()} only"
            )
            space = TopologicalSpaces()(point_set, opens)
            set_map = Sets().Mor(source_space, space)(
                lambda point: space(set_projection(point))
            )
            return space, TopologicalSpaces().Mor(source_space, space)._from_continuous_set_map(set_map), (
                lambda point: point.index()
            )
        case False:
            space = _object_of(
                category,
                _engine=(TopologicalSpaces(), engine, None),
                topology_data=_FinalTopologyData(source_space, set_projection),
                point_set=point_set,
                **engine_data,
            )
            set_map = Sets().Mor(source_space, space)(lambda point: space(set_projection(point)))
            return space, TopologicalSpaces().Mor(source_space, space)._from_continuous_set_map(set_map), (
                lambda point: point
            )


class ContinuousMap:
    r"""A continuous map, retaining its underlying set morphism."""

    def __init__(self, parent, set_morphism) -> None:
        if (
            set_morphism.domain() is not parent.domain()
            or set_morphism.codomain() is not parent.codomain()
        ):
            raise ValueError(
                f"{set_morphism} cannot underlie a continuous map {parent.domain()} -> "
                f"{parent.codomain()}: it is a map {set_morphism.domain()} -> "
                f"{set_morphism.codomain()}"
            )
        self._set_morphism = set_morphism
        super().__init__(parent, set_morphism)

    def underlying_set_morphism(self):
        return self._set_morphism

    def is_embedding(self):
        pass

    def simplicial_approximation(self, source_triangulation, target_triangulation):
        r"""Select a simplicial map after source subdivision and a homotopy to this map.

        The supplied triangulations lie over this map's exact domain and
        codomain. The comparison uses their selected realization arrows.
        """
        pass

    def is_homotopic_to(self, other):
        r"""Decide homotopy between maps with the same exact endpoints."""
        pass

    def is_weak_equivalence(self):
        r"""Decide whether this map is bijective on components and on pointed homotopy groups."""
        pass

    @validator
    def validate_continuity(self) -> None:
        r"""Raise ``ValueError`` unless the preimage of each open set of ``Y`` is open in ``X`` (``OWN-22``)."""
        parent = self.parent()
        if not parent._preimages_of_opens_are_open(self.underlying_set_morphism()):
            raise ValueError(
                f"{self.underlying_set_morphism()} is not continuous from {parent.domain()} to "
                f"{parent.codomain()}: the preimage of an open set of {parent.codomain()} is not "
                f"open in {parent.domain()}"
            )

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        mor = TopologicalSpaces().Mor(other.domain(), self.codomain())
        return mor._from_continuous_set_map(
            self.underlying_set_morphism()
            * other.underlying_set_morphism()
        )

    def __eq__(self, other) -> bool:
        return (
            element_parent(other) is self.parent()
            and other.underlying_set_morphism() == self.underlying_set_morphism()
        )

    def __ne__(self, other) -> bool:
        return not self == other

    __hash__ = None


class TopologicalSpaceMor(CategoricalMor):
    r"""``Mor_Top(X, Y)``: the subset of ``Mor_Set(X, Y)`` of the continuous maps.

    The forgetful functor ``U: Top -> Set`` is faithful and is the identity on
    objects, since ``X`` is an object of ``Sets()`` through its construction.
    A continuous map ``X -> Y`` is therefore a set map ``X -> Y`` with a
    property: the preimage of each open set of ``Y`` is open in ``X``.  The
    supercategory of this Mor is ``Mor_Set(X, Y)``
    (``CategoricalMor.super_categories``), and a set map lies in this Mor
    exactly when it is continuous (``CON-17``).
    """

    ElementMethods = ContinuousMap

    def __init__(self, family, domain, codomain) -> None:
        r"""Place ``Mor_Top(X, Y)`` as a set, a subset of ``Y^X``.

        It is finite when ``X`` and ``Y`` are finite, and ``End_Top(X)`` is a
        monoid under composition.
        """
        from sage_extensions.categories.group.magmas import Monoids

        match domain, codomain:
            case _ if domain in FiniteSets() and codomain in FiniteSets():
                sets = FiniteSets()
            case _:
                sets = Sets()
        monoids = (Monoids(),) if domain is codomain else ()
        super().__init__(family, domain, codomain, category=owned_category_join((sets, *monoids)))

    def _preimages_of_opens_are_open(self, set_map) -> bool:
        r"""Continuity of ``set_map: UX -> UY``, decided from its definition.

        For each open set ``V`` of ``Y``, the preimage ``f^{-1}(V)`` is formed
        as a subset of ``X``, and ``X`` is asked whether it is open.  When
        ``X`` is finite and every point of ``X`` is open, ``X`` is discrete,
        so every subset of ``X`` is open and every map out of ``X`` is
        continuous (Munkres, *Topology*, §12 and §18).
        """
        source = self.domain()
        match source in FiniteSets() and source in EnumeratedSets():
            case True if all(
                source.is_open_subset(
                    source.power_set().from_predicate(lambda point, chosen=chosen: point == chosen)
                )
                is True
                for chosen in source
            ):
                return True
            case _:
                pass
        target_opens = self.codomain().open_subsets()
        assert target_opens in FiniteSets() and target_opens in EnumeratedSets(), (
            f"cannot decide whether {set_map} is continuous: continuity is decided "
            f"here only when the topology of the codomain {self.codomain()} has a finite "
            f"enumerated set of open sets, and its open sets are in {target_opens.category()}"
        )
        source_power = self.domain().power_set()
        return all(
            self.domain().is_open_subset(
                source_power.from_predicate(
                    lambda point, selected=open_subset: set_map(point) in selected
                )
            )
            is True
            for open_subset in target_opens
        )

    def accepts(self, arrow) -> bool:
        r"""Membership: a continuous map ``X -> Y``, or a continuous set map ``X -> Y``."""
        if self._already_parented_arrow(arrow):
            return True
        return (
            arrow in Sets().Mor(self.domain(), self.codomain())
            and self._preimages_of_opens_are_open(arrow)
        )

    def _element_constructor_(self, datum, check=False):
        r"""A continuous map, given by a set map ``X -> Y`` or by a function on points.

        The datum is read as a set map in ``Mor_Set(X, Y)``.  The caller states
        that it is continuous, the condition that cuts this subset out of it;
        the validator :meth:`validate_continuity` checks it when asked
        (``check=True``) or under strict checking (``OWN-22``).
        """
        if element_parent(datum) is self:
            return datum
        arrow = self.element_class(self, Sets().Mor(self.domain(), self.codomain())(datum))
        arrow.validate_continuity(check=check)
        return arrow

    def _from_continuous_set_map(self, set_morphism):
        r"""Construct a map whose continuity follows from a categorical theorem.

        Used by identity, composition, and the maps of a final topology:
        the projection ``q: Y -> Q`` is continuous by the definition of the
        final topology, and the map ``Q -> Z`` induced by a continuous
        ``h: Y -> Z`` is continuous because the ``q``-preimage of the preimage
        of an open ``V`` is ``h^{-1}(V)``. The same statement for a family
        of injections supplies coproduct injections and their universal maps.
        The prime-spectrum functor uses ``PrimeSpectrum.continuous_comap``:
        preimages of basis opens are basis opens, ``D(a)`` pulling back to
        ``D(f(a))`` along a ring map ``f``.
        No arbitrary caller datum enters
        through this route.
        """
        return self.element_class(self, set_morphism)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity map from {self.domain()} to {self.codomain()}: an "
                f"identity needs its domain and codomain to be the same topological space"
            )
        return self._from_continuous_set_map(
            Sets().Mor(self.domain(), self.domain()).identity()
        )

    def _repr_(self):
        return f"Mor_Top({self.domain()}, {self.codomain()})"


class TopologicalSpaceMorCategoryConstruction(MorCategoryConstruction):
    r"""The Mor family of topological spaces."""

    def fixed_category_class(self):
        return TopologicalSpaceMor


class TopologicalSpaces(OwnedCategory):
    r"""Sets equipped with a topology, with continuous maps as morphisms."""

    _MorCategory = TopologicalSpaceMorCategoryConstruction

    @property
    def Coslices(self):
        r"""``X/Top``; for ``X`` the one-point space, the pointed spaces ``*/Top``."""
        from sage_extensions.categories.pointed_topological_spaces import (
            TopologicalSpaceCoslices,
        )

        return TopologicalSpaceCoslices

    def super_categories(self):
        return [Sets()]

    def an_object(self):
        r"""The Sierpiński two-point space."""
        points = Sets.Δ[1]
        return self(points, ((), (points(1),), points))

    @cached_method
    def terminal_object(self):
        r"""``*``, the one-point space: every space has exactly one continuous map to it."""
        point = Sets.Δ[0]
        return self(point, ((), (point(0),)))

    def pointed_space(self, space, base_point):
        r"""``(B, b)`` as an object of ``*/Top``: the coslice object on the map ``* -> B``, ``* -> b``."""
        point = self.terminal_object()
        return self.CosliceUnder(point)(point.Mor(space)(lambda _: base_point))

    def mapping_cylinder(self, morphism):
        r"""The pushout ``X ∪_f (A × [0,1])`` for ``f: A -> X``, with its selected cocone."""
        pass

    def subspace(self, subset_inclusion):
        r"""Give the selected subset its induced topology and inclusion into its exact space."""
        pass

    @cached_method
    def fundamental_groupoid_functor(self):
        from sage_extensions.categories.fundamental_groupoids import _FundamentalGroupoidFunctor

        return _FundamentalGroupoidFunctor()

    def _call_(self, point_set, open_subsets):
        r"""Construct the exact finite topology ``open_subsets`` on ``point_set``.

        The space is constructed on ``S = point_set`` through its set level:
        the finite ordered set enumerated by ``S``, with a point of its own at
        each point of ``S``.  The topology level adds the open sets, given as
        subsets of ``S``.
        """
        point_set = Sets()(point_set)
        topology_data = _FiniteTopologyData(point_set, open_subsets)
        # The engine serves the join: it derives the enumeration that the
        # ordered-set level of the join consumes, so it precedes that level.
        finite_spaces = owned_category_join((self, FiniteOrderedSets()))
        # The space is an object of Top built by Top's constructor; the ordered
        # set level is its presentation, so its arrows are continuous maps.
        return _object_of(
            finite_spaces,
            _engine=(finite_spaces, _FiniteTopologicalSpaceEngine, _FiniteSpacePoint),
            _ambient=self,
            topology_data=topology_data,
            point_set=point_set,
        )

    def _categorical_coequalizer(self, left_morphism, right_morphism):
        return self._categorical_coequalizer_construction(left_morphism, right_morphism).object()

    def _categorical_coproduct_construction(self, factors):
        r"""The coproduct of a family of spaces, with its universal maps.

        The underlying set is the disjoint union; its topology is final for
        the summand injections. A map out is continuous exactly when its
        restrictions to the summands are continuous (Mathlib,
        ``TopCat.continuous_iff_of_isColimit``).

        Unexecuted Sierpinski-space specimen::

            sage: from dzack_research.preamble.all import *
            sage: top = TopologicalSpaces()
            sage: X = top((0, 1), ((), (1,), (0, 1)))
            sage: construction = top._categorical_coproduct_construction((X, X))
            sage: Q = construction.object()
            sage: shape = construction.diagram().domain()
            sage: left = construction.costructure_morphism(shape(0))
            sage: right = construction.costructure_morphism(shape(1))
            sage: left(X(0)) != right(X(0))
            True
            sage: component = Q.power_set().from_predicate(lambda point: point.summand_index() == 0)
            sage: Q.is_open_subset(component)
            True
            sage: closed_point = Q.power_set().from_predicate(
            ....:     lambda point: point.summand_index() == 0 and point.summand_element() == X(0)
            ....: )
            sage: Q.is_open_subset(closed_point)
            False
            sage: cocone = construction.diagram().CoproductCocones().cocone(
            ....:     X, lambda index: top.Mor(X, X).identity()
            ....: )
            sage: fold = construction.factor(cocone).apex_map()
            sage: fold(left(X(0))) == X(0) and fold(right(X(1))) == X(1)
            True
        """
        from sage_extensions.categories.abstract_categories.products import (
            SelectedColimitConstruction,
            _discrete_diagram,
            _factor_family,
        )
        from sage_extensions.categories.sets.indexed_families import indexed_family

        supplied = _factor_family(factors, name="Topological coproduct factors")

        def factor_at(index):
            factor = supplied[index]
            if factor not in self:
                raise TypeError(f"a coproduct in {self} requires topological spaces, got {factor}")
            return factor

        family = indexed_family(supplied.index_set(), factor_at, name="Topological coproduct factors")
        set_construction = Sets()._categorical_coproduct_construction(family)
        point_set = set_construction.object()
        coproduct = _object_of(
            self,
            _engine=(TopologicalSpaces(), _FinalTopologySpaceEngine, None),
            topology_data=_CoproductTopologyData(family, point_set),
            point_set=point_set,
        )
        diagram = _discrete_diagram(family, self)

        def injection(index):
            factor = family[index.value()]
            set_injection = point_set.injection(index.value())
            return self.Mor(factor, coproduct)._from_continuous_set_map(
                Sets().Mor(factor, coproduct)(lambda point: coproduct(set_injection(point)))
            )

        universal_cocone = diagram.CoproductCocones().cocone(coproduct, injection)

        def factorizer(cocone):
            apex = cocone.apex()
            set_cocone = set_construction.diagram().CoproductCocones().cocone(
                apex,
                lambda index: cocone.costructure_morphism(
                    diagram.domain()(index.value())
                ).underlying_set_morphism(),
            )
            set_factor = set_construction.factor(set_cocone).apex_map()
            return self.Mor(coproduct, apex)._from_continuous_set_map(
                Sets().Mor(coproduct, apex)(lambda point: set_factor(point))
            )

        return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

    def _categorical_coequalizer_construction(self, left_morphism, right_morphism):
        r"""The coequalizer ``(Q, q)`` of continuous ``f, g: X -> Y``.

        ``U: Top -> Set`` creates coequalizers: ``Q`` is the coequalizer of
        the underlying set maps ``Uf, Ug`` with the final topology along
        ``q: UY -> Q`` (Mathlib, ``TopCat.coequalizer_isOpen_iff``: ``V`` is
        open exactly when ``q^{-1}(V)`` is open).  The universal pair is
        ``(Q, q)`` with ``q f = q g``; a continuous ``h: Y -> Z`` with
        ``h f = h g`` factors as ``h = h' q`` through the set map ``h'`` of the
        set coequalizer, which is continuous for the final topology.
        """
        from sage_extensions.categories.abstract_categories.products import (
            SelectedColimitConstruction,
            _parallel_pair_diagram,
        )

        source = left_morphism.domain()
        target = left_morphism.codomain()
        assert right_morphism.domain() is source and right_morphism.codomain() is target, (
            f"a coequalizer needs parallel maps f, g: X -> Y, but {left_morphism} is "
            f"{source} -> {target} and {right_morphism} is "
            f"{right_morphism.domain()} -> {right_morphism.codomain()}"
        )
        mor = self.Mor(source, target)
        assert left_morphism in mor and right_morphism in mor, (
            f"a coequalizer in {self} needs continuous maps {source} -> {target}, but "
            f"{left_morphism} or {right_morphism} is not in {mor}"
        )
        left_set_map = left_morphism.underlying_set_morphism()
        right_set_map = right_morphism.underlying_set_morphism()
        set_construction = Sets()._categorical_coequalizer_construction(left_set_map, right_set_map)
        set_shape = set_construction.diagram().domain()
        quotient, projection, point_of_set = _final_topology_space(
            target,
            set_construction.costructure_morphism(set_shape.target()),
            category=self,
            engine=_FinalTopologySpaceEngine,
        )
        diagram = _parallel_pair_diagram(left_morphism, right_morphism, self)
        shape = diagram.domain()
        universal_cocone = diagram.Cocones().cocone(
            quotient,
            lambda index: projection * left_morphism if index is shape.source() else projection,
        )

        def factorizer(cocone):
            apex = cocone.apex()
            target_map = cocone.costructure_morphism(shape.target()).underlying_set_morphism()
            set_cocone = set_construction.diagram().Cocones().cocone(
                apex,
                lambda index: target_map * left_set_map if index is set_shape.source() else target_map,
            )
            set_factor = set_construction.factor(set_cocone).apex_map()
            return self.Mor(quotient, apex)._from_continuous_set_map(
                Sets().Mor(quotient, apex)(lambda point: set_factor(point_of_set(point)))
            )

        return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

    def singular_cohomology_functor(self, coefficients):
        r"""The contravariant functor ``H^*(-; R): Top^op -> GradedAlgebras(R, ZZ).Supercommutative()``.

        It sends a space ``X`` to ``X.singular_cohomology(R)`` and a continuous
        map ``f: X -> Y`` to the pullback ``f^*: H^*(Y; R) -> H^*(X; R)``, the
        map induced on cohomology by the cochain map dual to
        ``f_*: C_*(X) -> C_*(Y)``.  The pullback is a morphism of graded
        algebras, ``f^*(a b) = f^*(a) f^*(b)`` (Hatcher, *Algebraic Topology*,
        §3.2, the naturality preceding Thm 3.11).  Its domain is the opposite
        category of this category.  The object part is computed; the pullback
        on arrows is not.
        """
        from sage_extensions.categories.functors.cohomology import (
            _singular_cohomology_functor,
        )

        return _singular_cohomology_functor(coefficients)

    @classmethod
    def _repr_object_names(cls):
        return "topological spaces"

    class SubcategoryMethods:
        def Compact(self):
            r"""Return this category with the axiom that its objects are compact."""
            return self._with_axiom("Compact")

    class Compact(CategoryWithAxiom):
        r"""Compact spaces: every open cover has a finite subcover (Mathlib ``CompactSpace``)."""

    class ParentMethods:
        def __init__(self, topology_data, **rest) -> None:
            self._represented_topology_data = topology_data
            super().__init__(**rest)


        def _topology_data(self):
            return self._represented_topology_data

        def open_subsets(self):
            r"""The set of open subsets defining this topology."""
            return self._topology_data().open_subsets(self)

        topology = open_subsets

        def open_complement(self, closed_inclusion):
            pass

        def open_complement_inclusion(self, closed_inclusion):
            pass

        @cached_method
        def open_subsets_site(self):
            r"""``Open(X)``, the poset category of the open subsets of ``X`` ordered by inclusion.

            Its objects are the opens ``U`` of ``X``, with one arrow ``U -> V``
            exactly when ``U <= V``, and ``X`` is its terminal object.  With the
            covers ``{U_i -> U}`` whose union is ``U`` it is the site of
            ``OpenCoveringFamilies(X)``, on which ``Sh(X, D)`` is the full
            subcategory of ``[Open(X)^op, D]`` satisfying descent (Mathlib,
            ``TopologicalSpace.Opens`` and ``TopCat.Sheaf``).  The order is the
            inclusion order of the power set restricted along the inclusion of
            the opens into it.
            """
            from sage_extensions.categories.abstract_categories.products import (
                PosetCategory,
            )

            opens = self.open_subsets()
            inclusion = opens.inclusion()
            inclusion_order = inclusion.codomain().inclusion_order()
            return PosetCategory(
                opens,
                le=lambda smaller, larger: inclusion_order.le(inclusion(smaller), inclusion(larger)),
            )

        def is_open_subset(self, subset) -> bool:
            r"""Whether ``subset`` is open in this topology."""
            return self._topology_data().is_open_subset(self, subset)

        def continuous_map(self, codomain, map_):
            return self.Mor(codomain)(map_)

        def singular_cohomology(self, coefficients):
            r"""``H^*(X; R)``, the singular cohomology algebra of this space with coefficients ``R``.

            It is the cohomology of the singular cochain algebra
            ``C^*(X; R) = Hom_ZZ(C_*(X), R)``, with the coboundary ``delta`` dual
            to the singular boundary and the cup product of cochains, so the
            value of ``CohomologyAlgebras(R)`` on that differential graded
            algebra.  The cup product is graded-commutative on cohomology,
            ``a b = (-1)^{k l} b a`` for ``a`` of degree ``k`` and ``b`` of
            degree ``l`` (Hatcher, *Algebraic Topology*, Thm 3.11), although it
            is not on cochains, so the result is an object of
            ``GradedAlgebras(R, ZZ).Supercommutative()``, graded by ``ZZ`` and
            concentrated in degrees ``k >= 0``.  Its degree-``k`` piece
            ``graded_piece(k)`` is ``H^k(X; R)``, an object of ``Modules(R)``.
            """
            assert False, "singular_cohomology on TopologicalSpaces: not implemented"

        def integral_singular_cohomology(self, degree):
            r"""``H^degree(X; ZZ)``, the degree piece of ``singular_cohomology(ZZ)``.

            A realization that computes the group directly supplies this method.
            """
            from sage_extensions.categories.rings.ring_foundation import (
                _owned_integers,
            )

            return self.singular_cohomology(_owned_integers()).graded_piece(degree)

        def betti_number(self, degree):
            r"""``b_k(X) = rank H^k(X; ZZ)``, the ``k``-th Betti number.

            Hatcher, *Algebraic Topology* [Hat02], §2.2 (before Thm. 2.44),
            defines ``b_k`` as the rank of ``H_k(X; ZZ)``.  When ``H_k`` and
            ``H_{k-1}`` are finitely generated, Cor. 3.3 (universal
            coefficients) gives ``H^k = H_k / T_k + T_{k-1}`` with ``T`` the
            torsion, so ``H^k`` and ``H_k`` have the same rank.
            """
            return self.integral_singular_cohomology(degree).module_rank()

        def euler_characteristic(self):
            r"""``chi(X) = sum_k (-1)^k b_k(X)``.

            Hatcher [Hat02], Thm. 2.44: for a finite CW complex ``X``,
            ``chi(X) = sum_n (-1)^n rank H_n(X)``.  The sum runs over the
            degrees up to the dimension of a finite CW complex homotopy
            equivalent to ``X``, which the realization states in
            :meth:`_finite_cw_dimension`.  The sum is the contraction of the
            Betti vector ``(b_0, ..., b_d)`` with the covector
            ``((-1)^0, ..., (-1)^d)``.
            """
            from sage_extensions.categories.rings.ring_foundation import (
                _own_ring,
                _owned_integers,
            )
            from sage_extensions.tensors import tensor
            from sage.rings.integer_ring import ZZ as SageZZ

            integers = _owned_integers()
            degrees = range(int(self._finite_cw_dimension()) + 1)
            betti_vector = tensor.vector(
                integers, [integers(int(self.betti_number(degree))) for degree in degrees]
            )
            alternating_signs = tensor.covector(
                integers, [integers((-1) ** degree) for degree in degrees]
            )
            return alternating_signs.contract(betti_vector)

        def _finite_cw_dimension(self):
            r"""A bound ``d`` with ``X`` homotopy equivalent to a finite CW complex of dimension ``<= d``.

            Protected contract of :class:`TopologicalSpaces`.  The owner is
            this category; a realization engine that knows a finite CW
            structure up to homotopy overrides it and returns a Python
            ``int``.  The only caller is :meth:`euler_characteristic`, which
            needs the degrees where ``H^k`` can be nonzero.  A space without
            such a statement stops here.
            """
            assert False, (
                f"{self} is not known to have the homotopy type of a finite CW complex, so its "
                "Euler characteristic is not defined by Hatcher, Thm. 2.44"
            )

        def _homotopy_group_module(self, base_point, degree):
            r"""``pi_degree(X, x)`` for ``degree >= 1``, an object of ``Modules(ZZ)`` when the group is abelian.

            Protected contract of :class:`TopologicalSpaces`.  The owner is
            this category; a realization engine that knows the homotopy
            groups of its space overrides it.  The only caller is
            ``TopologicalSpaceCoslices.ParentMethods``, which assembles the
            homotopy Lie algebra of the pointed space ``(X, x)``.  Repeated
            calls with one degree return the same module.
            """
            assert False, (
                f"the homotopy group pi_{degree}({self}, {base_point}) is not known to this space"
            )

        def _fundamental_group_at(self, base_point):
            r"""``pi_1(X, x)``, an object of ``Groups``.

            Protected contract of :class:`TopologicalSpaces`, with the owner
            and caller of :meth:`_homotopy_group_module`.
            """
            pass

        def fundamental_groupoid(self):
            r"""A ``Cat`` object with this space's points and path-homotopy arrows."""
            from sage_extensions.categories.fundamental_groupoids import FundamentalGroupoid

            return FundamentalGroupoid(self)

        def local_systems(self, fiber_category):
            r"""Functors from this space's fundamental groupoid to the fiber category."""
            from sage_extensions.categories.abstract_categories.cat import Cat

            return Cat().Mor(self.fundamental_groupoid(), fiber_category)

        def _whitehead_pairing(self, base_point, left_degree, right_degree):
            r"""The Whitehead product ``pi_p(X, x) x pi_q(X, x) -> pi_{p+q-1}(X, x)``, a bilinear map.

            Protected contract of :class:`TopologicalSpaces`, with the owner
            and caller of :meth:`_homotopy_group_module`.  Its factors and
            codomain are the modules that :meth:`_homotopy_group_module`
            returns.  The product is ``[alpha, beta] = (alpha v beta) o w``
            for the attaching map ``w: S^{p+q-1} -> S^p v S^q`` of the top
            cell of ``S^p x S^q`` (Hatcher, *Algebraic Topology*, Example 4.52).
            """
            assert False, (
                f"the Whitehead product pi_{left_degree} x pi_{right_degree} -> "
                f"pi_{left_degree + right_degree - 1} of ({self}, {base_point}) is not known to this space"
            )


__all__ = [
    "ContinuousMap",
    "TopologicalSpaceMor",
    "TopologicalSpaces",
]
