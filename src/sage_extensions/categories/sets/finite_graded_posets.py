r"""Finite graded posets with selected integer grades and rank-preserving maps."""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
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


class FiniteGradedPosetMorphism(Morphism):
    r"""A monotone map preserving the selected integer grade."""

    def __init__(self, parent, order_map):
        Morphism.__init__(self, parent)
        self._order_map = order_map

    def underlying_order_map(self):
        return self._order_map

    def __call__(self, point):
        return self.codomain()(self.underlying_order_map()(self.domain()(point)))

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

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "finite graded posets"

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
