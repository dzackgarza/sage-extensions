r"""The one-object category ``BG`` and the functor induced by a group map.

The category constructs one formal object. The represented group's elements
name its endomorphisms, and group multiplication is composition. Sage's ``Morphism`` and
the existing owned Mor construction supply the runtime representation;
the group owner supplies multiplication, inverses and equality.
"""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.structure.richcmp import richcmp

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoryPacketMethods,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.groups import OwnedGroups, _owned_group
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class ClassifyingMorphism(Morphism):
    r"""An arrow of ``BG``, named by its group element."""

    def __init__(self, parent, group_element) -> None:
        self._group_element = parent.mor_category().group()(group_element)
        Morphism.__init__(self, parent)

    def group_element(self):
        return self._group_element

    def _composition(self, right):
        r"""Composition in ``BG`` is the group law; Sage's ``Map.__mul__`` has checked ``right`` is a map into the one object."""
        if right.parent() is not self.parent():
            return NotImplemented
        return self.parent()(self.group_element() * right.group_element())

    def inverse(self):
        return self.parent()(~self.group_element())

    __invert__ = inverse

    def _richcmp_(self, other, op):
        r"""Compare two arrows of ``BG`` by their group elements; Sage calls this with one parent."""
        return richcmp(self.group_element(), other.group_element(), op)

    def _repr_(self):
        return f"{self.group_element()} in B({self.parent().mor_category().group()})"


class ClassifyingMor(CategoricalMor):
    r"""The single Mor object of ``BG``."""

    Element = ClassifyingMorphism

    def _element_constructor_(self, datum):
        if isinstance(datum, ClassifyingMorphism):
            assert datum.parent() is self, (
                f"{datum} is an arrow of {datum.parent()}, not of {self}: an element of "
                f"B(G) must be an arrow of the classifying category of that same group G"
            )
            return datum
        return self.element_class(self, datum)

    @object_level
    @cached_method
    def identity(self):
        return self(self.mor_category().group().one())


class ClassifyingMorCategory(MorCategoryConstruction):
    def fixed_category_class(self):
        return ClassifyingMor


class ClassifyingCategory(CategoryPacketMethods, OwnedParameterizedCategory):
    r"""The one-object category with endomorphism group ``G``."""

    @staticmethod
    def __classcall__(cls, group):
        return OwnedParameterizedCategory.__classcall__(cls, _owned_group(group))

    def parameter_category(self):
        return OwnedGroups()

    def group(self):
        return self.parameter()

    class ParentMethods:
        r"""The unique formal object of ``BG``; ``G`` lives in its endomorphisms."""

        def classifying_category(self):
            return self.category()

        def _repr_(self):
            return f"* in B({self.classifying_category().group()})"

    @cached_method
    def object(self):
        return _object_of(self)

    @cached_method
    def object_set(self):
        r"""The singleton set of objects of the one-object category ``BG``.

        The object here is the actual formal object of this category, not
        the identity element of its endomorphism group.  In particular the
        object set is unchanged when the group is replaced by another group.

        Unexecuted mathematical specimen::

            sage: from dzack_research.preamble.all import Groups, Sets
            sage: B = Groups.S(3).classifying_category()
            sage: B.object() in B.object_set()
            True
            sage: B.object_set().cardinality() == 1
            True
            sage: B.Mor(B.object(), B.object()).identity().group_element() == B.group().one()
            True
        """
        from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

        return finite_ordered_set((self.object(),))

    def arrows(self):
        r"""The complete set of arrows of ``BG``, namely ``Mor_BG(*,*)``.

        For infinite ``G``, this is still a represented Hom set; it is
        not replaced by a finite sample of group elements. Each element
        retains its source and target object and the selected group element
        that defines its composition.
        """
        point = self.object()
        return self.Mor(point, point).arrow_set()

    def an_object(self):
        return self.object()

    def super_categories(self):
        return [Objects()]

    _MorCategory = ClassifyingMorCategory

    def _repr_object_names(self):
        return f"the unique object of B({self.group()})"


class ClassifyingFunctor(Functor):
    r"""``B(phi): BH -> BG`` for a group morphism ``phi: H -> G``."""

    def __init__(self, group_morphism) -> None:
        self._group_morphism = group_morphism
        super().__init__(
            group_morphism.domain().classifying_category(),
            group_morphism.codomain().classifying_category(),
        )

    def group_morphism(self):
        return self._group_morphism

    def _apply_object(self, obj):
        return self.codomain().an_object()

    def _apply_morphism(self, morphism):
        point = self.codomain().an_object()
        return self.codomain().Mor(point, point)(
            self.group_morphism()(morphism.group_element())
        )
