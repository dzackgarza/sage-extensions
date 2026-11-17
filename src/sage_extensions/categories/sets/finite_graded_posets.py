r"""Finite graded posets with selected integer grades and rank-preserving maps."""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.arrow_categories import (
    CoreMor,
    _CoreCategory,
)
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalIsomorphism,
    CategoricalMor,
    IsoCategoryConstruction,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import (
    FiniteSets,
    PartiallyOrderedSets,
    Sets,
)
from sage_extensions.owned_category import _object_of
from sage_extensions.validation import validator


class FiniteGradedPosetMorphism(CategoricalMor.ElementMethods):
    r"""Methods for a generated monotone map preserving the selected integer grade."""

    def __init__(self, parent, order_map):
        Morphism.__init__(self, parent)
        self._order_map = order_map

    def underlying_order_map(self):
        return self._order_map

    def __call__(self, point):
        return self.codomain()(self.underlying_order_map()(self.domain()(point)))

    def __eq__(self, other):
        r"""Two such arrows are equal when they are of one Mor and send every point alike.

        The retained datum is the monotone map, and a map of a finite carrier is
        decided by its values, so equality is the conjunction of those.  Sage's
        generic comparison of ``Map`` would compare the endpoints as parents with
        generators, which a graded poset need not have.
        """
        from sage_extensions.logic import conjunction

        if element_parent(other) is not self.parent():
            return False
        if self is other:
            return True
        return conjunction(self(point) == other(point) for point in self.domain())

    def __ne__(self, other):
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self) -> int:
        r"""Hash the retained order map, which :meth:`__eq__` compares."""
        return hash(self.underlying_order_map())

    @validator
    def validate_grade(self):
        if not all(
            self.domain().grade(point) == self.codomain().grade(self(point))
            for point in self.domain()
        ):
            raise ValueError(f"{self.underlying_order_map()} does not preserve the selected grade")

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        if other.parent().base_category() is not FiniteGradedPosets():
            return NotImplemented
        return FiniteGradedPosets().Mor(other.domain(), self.codomain())(
            self.underlying_order_map() * other.underlying_order_map()
        )


class FiniteGradedPosetMor(CategoricalMor):
    r"""The rank-preserving monotone maps between two finite graded posets."""

    ElementMethods = FiniteGradedPosetMorphism

    def _element_constructor_(self, order_map, *, check=False):
        if element_parent(order_map) is self:
            return order_map
        source = self.domain().underlying_poset()
        target = self.codomain().underlying_poset()
        arrow = self.element_class(
            self,
            PartiallyOrderedSets().Mor(source, target)(order_map),
        )
        arrow.validate_grade(check=check)
        return arrow

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError("a graded-poset identity requires the same source and target")
        poset = self.domain().underlying_poset()
        return self(PartiallyOrderedSets().Mor(poset, poset).identity())


class FiniteGradedPosetMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = FiniteGradedPosetMor


class FiniteGradedPosetIsomorphism(CategoricalIsomorphism):
    r"""An isomorphism of finite graded posets, as a pair of inverse order maps.

    An isomorphism of graded posets is an arrow of the base Mor too -- a monotone
    map preserving the selected grade -- so composing two composable ones is the
    composition of their forward arrows, whose inverse is the reversed composite
    of the two inverses.  The composite is an isomorphism of the core, so the
    automorphisms of one graded poset are closed under it.
    """

    def __mul__(self, other):
        match other:
            case FiniteGradedPosetIsomorphism() if other.codomain() is self.domain():
                pass
            case _:
                return super().__mul__(other)
        return self.parent().core_category().Mor(other.domain(), self.codomain())._from_known_inverse_pair(
            self.forward() * other.forward(),
            other.inverse().forward() * self.inverse().forward(),
        )


class FiniteGradedPosetIsomorphismMor(CoreMor):
    r"""``Iso`` of finite graded posets: an inverse pair of rank-preserving order maps.

    An isomorphism of finite graded posets is a monotone bijection preserving
    the selected integer grade whose inverse is monotone too
    (``lean-categories/LeanCategories/Orders/FiniteGradedPoset.lean``: ``Hom`` is
    an ``OrderHom`` with ``grade_eq``, and ``Iso`` is the generic isomorphism on
    that ``Hom``).  The datum retained here is exactly that pair: the forward
    arrow is an element of :class:`FiniteGradedPosetMor`, and the inverse is the
    reversed one.

    On the diagonal these arrows are the automorphisms of the graded poset and
    ``Aut(X)`` is their group, the core's vertex group.  It is placed in
    ``OwnedFiniteGroups()`` because an automorphism of a finite graded poset is a
    permutation of its finite carrier, so its finiteness is a theorem and not a
    computation.  What computes the group is the engine's permutation group on
    the carrier's positions -- Sage's automorphism group of the incidence graph
    of the order relation, whose vertex colours are the grades -- and the
    operations below cross between that engine's permutations and the arrows
    they represent.  No automorphism is a bare permutation here: the order and
    the grade stay on the arrow.
    """

    ElementMethods = FiniteGradedPosetIsomorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        from sage_extensions.categories.group.groups import OwnedFiniteGroups

        CoreMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
            category=OwnedFiniteGroups() if domain is codomain else None,
        )

    def core_category(self) -> _CoreCategory:
        r"""The core of ``FiniteGradedPosets``, whose arrows are these isomorphisms."""
        return FiniteGradedPosets().Core()

    def _require_the_automorphism_group(self) -> None:
        assert self.domain() is self.codomain(), (
            f"the engine of a finite graded poset is its automorphism group Aut(X), but {self} is "
            f"the isomorphisms {self.domain()} -> {self.codomain()}"
        )

    def _engine_group(self):
        r"""The engine permutation group of the automorphisms of the domain (``OWN-05``)."""
        self._require_the_automorphism_group()
        return self.domain()._engine_automorphism_group()

    def _engine_permutation(self, image_positions):
        r"""The engine permutation carrying each carrier position to a supplied position.

        The engine's points are the carrier's positions themselves, so the
        permutation is written in their own labels: its cycle decomposition, each
        cycle listing the positions it moves in the order it moves them.  A
        position it fixes is in no cycle.
        """
        images = tuple(int(position) for position in image_positions)
        seen = set()
        cycles = []
        for start in range(len(images)):
            if start in seen:
                continue
            cycle = []
            position = start
            while position not in seen:
                seen.add(position)
                cycle.append(position)
                position = images[position]
            if len(cycle) > 1:
                cycles.append(tuple(cycle))
        return self._engine_group()(tuple(cycles))

    def _positions_of(self, order_map):
        r"""The positions this arrow sends the carrier positions to."""
        domain = self.domain()
        position_of = domain._carrier_positions()
        return tuple(int(position_of(order_map(point))) for point in domain)

    def _isomorphism_of_positions(self, image_positions):
        r"""The isomorphism of the domain carrying each position to a supplied one.

        A permutation of the carrier's positions names one monotone bijection with
        a monotone inverse, so both arrows are read off it: the forward arrow sends
        the point at one position to the point at the image position, and the
        inverse sends it back.  Which permutations are automorphisms is decided by
        the caller's own data; :meth:`automorphism_from_positions` decides it by
        the engine group's membership test.
        """
        domain = self.domain()
        images = tuple(int(position) for position in image_positions)
        size = len(tuple(domain))
        assert sorted(images) == list(range(size)), (
            f"a permutation of the {size} positions of {domain} takes each position to one position, "
            f"but the images given are {images}"
        )
        position_of = domain._carrier_positions()
        point_at = domain._carrier_points()
        inverse_images = [0] * size
        for position, image in enumerate(images):
            inverse_images[image] = position
        order_maps = FiniteGradedPosets().Mor(domain, domain)
        forward = order_maps(
            lambda point: point_at(images[int(position_of(point))])
        )
        inverse = order_maps(
            lambda point: point_at(inverse_images[int(position_of(point))])
        )
        return self._from_known_inverse_pair(forward, inverse)

    def _to_engine(self, isomorphism):
        return self._engine_permutation(self._positions_of(isomorphism.forward()))

    def _from_engine(self, engine_element):
        size = len(tuple(self.domain()))
        return self._isomorphism_of_positions(
            tuple(int(engine_element(position)) for position in range(size))
        )

    def _engine_subgroup_from_generators(self, generators):
        return self._engine_group().subgroup(
            tuple(self._to_engine(generator) for generator in generators)
        )

    def _to_subgroup_engine(self, element, engine_subgroup):
        return engine_subgroup(self._to_engine(element))

    def _engine_subgroup_contains(self, element, engine_subgroup):
        return self._to_engine(element) in engine_subgroup

    def _from_subgroup_engine(self, engine_element):
        return self._from_engine(engine_element)

    def __iter__(self):
        r"""Enumerate the automorphisms of the domain, in the engine's order."""
        self._require_the_automorphism_group()
        return (self._from_engine(element) for element in self._engine_group())


class FiniteGradedPosetIsoCategoryConstruction(IsoCategoryConstruction):
    r"""The isomorphisms of finite graded posets."""

    def fixed_category_class(self):
        return FiniteGradedPosetIsomorphismMor


class _FiniteGradedPosetCore(_CoreCategory):
    r"""The core of ``FiniteGradedPosets``: its objects and its isomorphisms.

    Its Mor at two objects is the isomorphism Mor of this category, so ``Aut(X)``
    -- the vertex group of this core -- is the very object :meth:`Isom` returns,
    and products and inverses of automorphisms stay in it.
    """

    def Mor(self, domain, codomain):
        return _finite_graded_poset_isomorphism_mor(domain, codomain)


class _UnderlyingPosetFunctor(Functor):
    r"""Forget the selected integer grading on objects and maps."""

    def __init__(self):
        super().__init__(FiniteGradedPosets(), PartiallyOrderedSets())

    def _apply_object(self, graded_poset):
        return graded_poset.underlying_poset()

    def _apply_morphism(self, morphism):
        return morphism.underlying_order_map()


class FiniteGradedPosets(OwnedCategory):
    r"""Finite partial orders with a selected integer grade.

    The definition and rank-preserving arrows are those of
    ``lean-categories/LeanCategories/Orders/FiniteGradedPoset.lean``.
    """

    _MorCategory = FiniteGradedPosetMorCategoryConstruction
    _IsoCategory = FiniteGradedPosetIsoCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "finite graded posets"

    @cached_method
    def Core(self) -> _CoreCategory:
        r"""The core of this category: its objects and its isomorphisms.

        Its vertex groups are the ``Aut(X)`` of graded posets, so the automorphisms
        of one graded poset are retained as the arrows of its own poset.
        """
        return _FiniteGradedPosetCore(self)

    def _core_isomorphism_witness(self, core_mor):
        r"""Implementer side of ``CoreMor``'s core contract: one isomorphism, or ``None``.

        A graded poset is isomorphic to itself by its identity, and no other
        isomorphism between graded posets is computed here: two graded posets of
        equal carrier cardinality are isomorphic only when some rank-preserving
        bijection exists, which is a search this owner does not select.
        """
        if core_mor.domain() is core_mor.codomain():
            return core_mor.one()
        return None

    def _core_automorphism_generators(self, core_mor):
        r"""Implementer side of ``CoreMor``'s core contract: generators of ``Aut(X)``.

        ``CoreMor.group_generators`` reads a selected resolution first and asks
        this only without one.  The generators are the engine permutation group's,
        crossed into the arrows they represent, so they are automorphisms of the
        graded poset and not permutations of something else.
        """
        engine = core_mor._engine_group()
        return finite_ordered_set(
            tuple(core_mor._from_engine(generator) for generator in engine.gens())
        )

    def an_object(self):
        integers = _owned_integers()
        points = finite_ordered_set((integers(-1), integers.zero()))
        poset = PartiallyOrderedSets()(points, lambda left, right: left <= right)
        return self.on(poset, lambda point: point)

    def on(self, poset, grade, *, check=False):
        r"""Select an integer grading on the exact finite partial order ``poset``."""
        if poset not in PartiallyOrderedSets() or poset not in FiniteSets():
            raise TypeError(f"{poset} is not a finite partially ordered set")
        integers = _owned_integers()
        grade_map = Sets().Mor(poset, integers)(grade)
        graded = _object_of(self, underlying_poset=poset, grading_map=grade_map)
        graded.validate_grading(check=check)
        return graded

    @cached_method
    def forget(self):
        return _UnderlyingPosetFunctor()

    class ParentMethods:
        def __init__(self, underlying_poset, grading_map, **rest):
            self._underlying_poset = underlying_poset
            self._grading_map = grading_map
            super().__init__(**rest)

        def underlying_poset(self):
            return self._underlying_poset

        def grading_map(self):
            return self._grading_map

        def grade(self, point):
            return self.grading_map()(self.underlying_poset()(point))

        @validator
        def validate_grading(self):
            r"""Check ``GradeOrder`` in Mathlib ``Order/Grade.lean``: strict monotonicity and cover preservation."""
            poset = self.underlying_poset()
            points = tuple(poset)
            for lower in points:
                for upper in points:
                    if lower == upper or not poset.le(lower, upper):
                        continue
                    lower_grade = self.grade(lower)
                    upper_grade = self.grade(upper)
                    if lower_grade >= upper_grade:
                        raise ValueError(f"the grade of {lower} must be below the grade of {upper}")
                    covered = not any(
                        middle != lower
                        and middle != upper
                        and poset.le(lower, middle)
                        and poset.le(middle, upper)
                        for middle in points
                    )
                    if covered and upper_grade != lower_grade + 1:
                        raise ValueError(f"a cover {lower} < {upper} must raise the grade by one")

        def __iter__(self):
            return iter(self.underlying_poset())

        def __contains__(self, point):
            return point in self.underlying_poset()

        def _element_constructor_(self, point):
            return self.underlying_poset()(point)

        def Isom(self, codomain):
            r"""Return the isomorphisms of graded posets from this one to ``codomain``."""
            return _finite_graded_poset_isomorphism_mor(self, codomain)

        @object_level
        def Aut(self):
            r"""Return ``Isom(X, X)``, the automorphism group of this graded poset.

            An element is a pair of mutually inverse rank-preserving order maps of
            this poset, so it acts on the points of the poset it belongs to.
            """
            return self.Isom(self)

        @cached_method
        def _carrier_points(self):
            r"""The point at each position of this poset, in its selected order."""
            return self._carrier_positions().inverse()

        @cached_method
        def _carrier_positions(self) -> CategoricalIsomorphism:
            r"""The position in the selected order of each point of this poset.

            The positions are what a permutation notation names, so they are read
            from the carrier's own chosen enumeration and not counted here.
            """
            return self.underlying_poset().underlying_set().ranking_map()

        @cached_method
        def _engine_automorphism_group(self):
            r"""The engine permutation group of the rank-preserving order automorphisms.

            An automorphism of a graded poset is a bijection of its carrier that
            preserves the order and the selected grade, so it is an automorphism of
            the directed graph of the order relation whose vertices are coloured by
            their grades; the private engine computes that group (Sage's
            ``automorphism_group`` of the graph, over the carrier's positions).
            Reading every comparable pair rather than only the covers keeps the
            relation the definition names, and no hypothesis on the poset is
            needed to read it.

            This is a computation, not a definition: the automorphisms are the
            arrows :meth:`Aut` retains, and this group is what counts them.
            """
            from sage.graphs.digraph import DiGraph

            points = tuple(self)
            position_of = self._carrier_positions()
            poset = self.underlying_poset()
            by_grade = {}
            for point in points:
                by_grade.setdefault(int(self.grade(point)), []).append(
                    int(position_of(point))
                )
            graph = DiGraph(loops=False, multiedges=False)
            graph.add_vertices(range(len(points)))
            for left, first in enumerate(points):
                for right, second in enumerate(points):
                    if left != right and poset.le(first, second):
                        graph.add_edge(left, right)
            return graph.automorphism_group(
                partition=[by_grade[grade] for grade in sorted(by_grade)]
            )

        def automorphism_from_positions(self, image_positions):
            r"""The automorphism of this poset carrying each point to a supplied position.

            A permutation of the carrier's positions induces one permutation of the
            points, and that is an automorphism exactly when it preserves the order
            and the grade; the engine group decides that, so an arbitrary
            permutation is refused here rather than retained as an automorphism.
            The returned element is an arrow of :meth:`Aut`, and it is the same
            arrow the engine's corresponding permutation represents.
            """
            images = tuple(int(position) for position in image_positions)
            size = len(tuple(self))
            assert sorted(images) == list(range(size)), (
                f"a permutation of the {size} positions of {self} takes each position to one "
                f"position, but the images given are {images}"
            )
            automorphisms = self.Aut()
            permutation = automorphisms._engine_permutation(images)
            assert permutation in automorphisms._engine_group(), (
                f"the positions {images} do not permute {self} by an automorphism: the induced map "
                "does not preserve the order relation and the grade, so it is no automorphism of "
                "the graded poset"
            )
            return automorphisms._isomorphism_of_positions(images)


def _finite_graded_poset_isomorphism_mor(domain, codomain):
    r"""The isomorphism Mor of ``FiniteGradedPosets`` at these endpoints.

    On the diagonal it is the automorphism group ``Aut(X)``, the same object
    whether it is asked as ``Isom(X, X)``, as ``Aut(X)`` or as a vertex group of
    the core, so a product of two automorphisms is an automorphism of the poset
    and not an arrow of some other family.
    """
    category = FiniteGradedPosets()
    return category.Aut(domain) if domain is codomain else category.Iso(domain, codomain)
