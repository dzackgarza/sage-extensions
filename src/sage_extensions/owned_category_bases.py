r"""One owned class per Sage category base class.

Sage gives a category a different base class for each shape.  The shapes are
plain, parameterized, singleton, with an axiom, over a base, over a base ring,
and one for each functorial construction.  Declare a preamble category over
the class here that has its shape.  Do not declare it over Sage's class.

This gives the category two properties.

Its ``ParentMethods``, ``ElementMethods`` and ``MorphismMethods`` become bases
of the named classes.  Thus they hold fields and a constructor, and
zero-argument ``super()`` operates.

The category also becomes an object of :math:`\mathbf{Cat}`.  Thus
``category()`` gives ``Cat()``, and not Sage's ``Objects()``.

:mod:`sage_extensions.owned_category` has the mechanism for both
properties, and the measurements that show it is correct.

The base order is:

``OwnedCategoryMixin, OwnedCategoryObject, <the Sage category base>, Parent``

A different Sage behaviour makes each position necessary.

* ``OwnedCategoryMixin`` is first.  Thus its ``_make_named_class`` wins.
  ``CategoryWithParameters._make_named_class`` calls
  ``Category._make_named_class`` **by name**.  ``Category_over_base``,
  ``CategoryWithAxiom`` and the functorial-construction categories inherit
  that call.  Thus an override lower in the ``Category`` hierarchy does not
  operate.
* ``OwnedCategoryObject`` is before the Sage base.  This is the one change of
  meaning.  Sage's ``Category.category`` gives ``Objects()``.  An owned
  category gives ``Cat()``.
* The Sage base is before ``Parent``.  If ``Parent`` is first,
  ``__contains__``, ``__call__``, ``base``, ``base_ring`` and
  ``element_class`` resolve to element-construction code.  That code is wrong
  for a category.
* ``Parent`` is last.  It is present only to make the category a parent.

The two singleton wrappers put their classcall bridge before all of these.
Sage's singleton classcall makes an assertion about ``__mro__[1]``.  See
:class:`_SingletonClasscallMixin`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from sage.categories.algebra_functor import AlgebrasCategory as SageAlgebrasCategory
from sage.categories.category import Category as SageCategory
from sage.categories.category import (
    CategoryWithParameters as SageCategoryWithParameters,
)
from sage.categories.category_singleton import (
    Category_singleton as SageCategorySingleton,
)
from sage.categories.category_types import Category_ideal as SageCategoryIdeal
from sage.categories.category_types import Category_module as SageCategoryModule
from sage.categories.category_types import Category_over_base as SageCategoryOverBase
from sage.categories.category_types import (
    Category_over_base_ring as SageCategoryOverBaseRing,
)
from sage.categories.category_with_axiom import (
    CategoryWithAxiom as SageCategoryWithAxiom,
)
from sage.categories.category_with_axiom import (
    CategoryWithAxiom_over_base_ring as SageCategoryWithAxiomOverBaseRing,
)
from sage.categories.category_with_axiom import (
    CategoryWithAxiom_singleton as SageCategoryWithAxiomSingleton,
)
from sage.categories.covariant_functorial_construction import (
    CovariantConstructionCategory as SageCovariantConstructionCategory,
)
from sage.categories.covariant_functorial_construction import (
    FunctorialConstructionCategory as SageFunctorialConstructionCategory,
)
from sage.categories.covariant_functorial_construction import (
    RegressiveCovariantConstructionCategory as SageRegressiveCovariantConstructionCategory,  # noqa: E501
)
from sage.categories.dual import DualObjectsCategory as SageDualObjectsCategory
from sage.categories.filtered_modules import (
    FilteredModulesCategory as SageFilteredModulesCategory,
)
from sage.categories.graded_modules import (
    GradedModulesCategory as SageGradedModulesCategory,
)
from sage.categories.homsets import Homsets as SageHomsets
from sage.categories.homsets import HomsetsCategory as SageHomsetsCategory
from sage.categories.homsets import HomsetsOf as SageHomsetsOf
from sage.categories.isomorphic_objects import (
    IsomorphicObjectsCategory as SageIsomorphicObjectsCategory,
)
from sage.categories.quotients import QuotientsCategory as SageQuotientsCategory
from sage.categories.realizations import (
    RealizationsCategory as SageRealizationsCategory,
)
from sage.categories.subobjects import SubobjectsCategory as SageSubobjectsCategory
from sage.categories.subquotients import (
    SubquotientsCategory as SageSubquotientsCategory,
)
from sage.categories.super_modules import (
    SuperModulesCategory as SageSuperModulesCategory,
)
from sage.categories.tensor import TensorProductsCategory as SageTensorProductsCategory
from sage.categories.with_realizations import (
    WithRealizationsCategory as SageWithRealizationsCategory,
)
from sage.misc.constant_function import ConstantFunction
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoryPacketMethods,
)
from sage_extensions.owned_category import (
    OwnedCategoryMixin,
    OwnedCategoryObject,
)

if TYPE_CHECKING:
    from sage_extensions.lexicon.category_theory import ObjectOfCategory
    from sage_extensions.lexicon.set_theory import SetObject
    from sage.categories.morphism import Morphism
    from sage.structure.category_object import CategoryObject
    from sage.structure.element import Element as CategoryElement


class _SingletonClasscallMixin:
    r"""Classcall bridge for an owned singleton category.

    Sage's ``Category_singleton.__classcall__`` asserts that ``cls.__mro__[1]``
    is exactly Sage's ``Category_singleton`` or ``CategoryWithAxiom_singleton``
    (``sage/categories/category_singleton.pyx``).  Any owned MRO breaks that
    assertion twice over: the flip and ``OwnedCategoryObject`` both precede the
    Sage base, and a singleton wrapper inherited from another singleton wrapper
    would break it again.

    So this isolates the one compatibility exception.  Sage's singleton caching
    is preserved exactly -- the same ``ConstantFunction`` classcall installed on
    both the concrete class and Sage's dynamic ``*_with_category`` class -- and
    only the direct-subclass assertion is bypassed.
    """

    @staticmethod
    @final
    def __classcall__(cls: type[SageCategorySingleton]) -> SageCategory:
        match cls:
            case DynamicMetaclass():
                cls = cls.__base__
        obj = super(SageCategorySingleton, cls).__classcall__(cls)
        cls._set_classcall(ConstantFunction(obj))
        obj.__class__._set_classcall(ConstantFunction(obj))
        return obj


class _SingletonAxiomClasscallMixin:
    r"""Classcall bridge for an owned singleton axiom category.

    Same exception as :class:`_SingletonClasscallMixin`, over the two
    construction paths Sage uses for a singleton axiom category.  A public call
    such as ``TopologicalSpaces()`` carries no base category and goes through
    ``CategoryWithAxiom.__classcall__``, which redirects to the declared base
    category and axiom.  A reconstruction call such as
    ``Sets().Finite().__class__(Sets())`` supplies the base category and
    constructs that singleton instance.  The optional ``base_category`` is that
    closed two-case dispatch, not a variadic catch-all.
    """

    @staticmethod
    @final
    def __classcall__(
        cls: type[SageCategoryWithAxiomSingleton],
        base_category: SageCategory | None = None,
    ) -> SageCategory:
        match cls:
            case DynamicMetaclass():
                cls = cls.__base__
        if base_category is None:
            return SageCategoryWithAxiom.__classcall__(cls)
        obj = super(SageCategorySingleton, cls).__classcall__(
            cls,
            base_category,
        )
        cls._set_classcall(ConstantFunction(obj))
        obj.__class__._set_classcall(ConstantFunction(obj))
        return obj


class Category(OwnedCategoryMixin, OwnedCategoryObject, SageCategory, Parent):
    r"""Owned base over Sage's ``Category``.  Most categories use this one.

    To declare a category over this base, write three things.  Write
    ``super_categories()``.  Write the nested method classes for the surfaces
    of this level.  If the level adds a datum, write one ``__init__`` that
    takes that datum and sends the remainder up with
    ``super().__init__(**rest)``.  There is no other place to register data.

    A parameterized category or a functorial construction uses one of the
    other bases below.  Those bases differ only in the Sage base class.
    """

    def __init__(self) -> None:
        self._init_cat_object()
        SageCategory.__init__(self)


class CategoryWithParameters(
    OwnedCategoryMixin, OwnedCategoryObject, SageCategoryWithParameters, Parent
):
    r"""Owned base over Sage's parameterized category base."""

    def __init__(self) -> None:
        self._init_cat_object()
        SageCategoryWithParameters.__init__(self)


class Category_singleton(
    _SingletonClasscallMixin,
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageCategorySingleton,
    Parent,
):
    r"""Owned base over Sage's singleton category base."""

    def __init__(self) -> None:
        self._init_cat_object()
        SageCategorySingleton.__init__(self)


class CategoryWithAxiom(
    CategoryPacketMethods,
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageCategoryWithAxiom,
    Parent,
):
    r"""Owned base over Sage's category-with-axiom base.

    An axiom states a property of the objects and no new morphisms, so the
    Mor packet is the one the refined category already has; carrying
    ``CategoryPacketMethods`` here is what lets an axiom category be asked for
    it, and the Mor family's supercategory walk is what makes the answer the
    same object rather than a second parent for the same maps.

    Sage's ``CategoryWithAxiom_over_base_ring`` is not the base to use for an
    axiom on an owned category over a ring: it asks Sage's own ``Rings()``
    about the base, and an owned ring is not placed there.  An owned category
    over a base ring carries the ring itself as its parameter, so the axiom
    category reads it from the category it refines.
    """

    def __init__(self, base_category: SageCategory) -> None:
        self._init_cat_object()
        SageCategoryWithAxiom.__init__(self, base_category)

    @classmethod
    def an_instance(cls) -> SageCategory:
        r"""Return the axiom applied to a sample of the category it refines.

        This is how Sage's ``CategoryWithAxiom.__classcall__`` builds an axiom
        category from its base (category_with_axiom.py): the base category
        with the axiom applied.  The base's own ``an_instance`` supplies the
        parameter, e.g. the rational field for a category over a ring.
        """
        base_category_class, axiom = cls._base_category_class_and_axiom
        return base_category_class.an_instance()._with_axiom(axiom)

    def base_ring(self) -> ObjectOfCategory:
        r"""Return the base ring of the category this axiom refines."""
        return self._base_category.base_ring()

    def base(self) -> ObjectOfCategory:
        return self._base_category.base()


class CategoryWithAxiom_singleton(
    CategoryPacketMethods,
    _SingletonAxiomClasscallMixin,
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageCategoryWithAxiomSingleton,
    Parent,
):
    r"""Owned base over Sage's singleton axiom category base."""

    def __init__(self, base_category: SageCategory | None = None) -> None:
        assert base_category is not None, (
            f"cannot construct the category {type(self).__name__}: a category with an "
            f"axiom needs the base category the axiom is added to, and none was given"
        )
        self._init_cat_object()
        SageCategoryWithAxiomSingleton.__init__(self, base_category)


class CategoryWithAxiom_over_base_ring(
    CategoryPacketMethods,
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageCategoryWithAxiomOverBaseRing,
    Parent,
):
    r"""Owned base over Sage's base-ring axiom category base."""

    def __init__(self, base_category: SageCategory) -> None:
        self._init_cat_object()
        SageCategoryWithAxiomOverBaseRing.__init__(self, base_category)


class Category_over_base(
    OwnedCategoryMixin, OwnedCategoryObject, SageCategoryOverBase, Parent
):
    r"""Owned base over Sage's category-over-base base."""

    def __init__(self, base: CategoryObject, name: str | None = None) -> None:
        self._init_cat_object()
        SageCategoryOverBase.__init__(self, base, name)


class Category_over_base_ring(
    OwnedCategoryMixin, OwnedCategoryObject, SageCategoryOverBaseRing, Parent
):
    r"""Owned base over Sage's category-over-base-ring base."""

    def __init__(self, base: CategoryObject, name: str | None = None) -> None:
        self._init_cat_object()
        SageCategoryOverBaseRing.__init__(self, base, name)


class Category_module(
    OwnedCategoryMixin, OwnedCategoryObject, SageCategoryModule, Parent
):
    r"""Owned base over Sage's module category base."""

    def __init__(self, base: CategoryObject, name: str | None = None) -> None:
        self._init_cat_object()
        SageCategoryModule.__init__(self, base, name)


class Category_ideal(
    OwnedCategoryMixin, OwnedCategoryObject, SageCategoryIdeal, Parent
):
    r"""Owned base over Sage's ideal category base."""

    def __init__(self, ring: CategoryObject, name: str | None = None) -> None:
        self._init_cat_object()
        SageCategoryIdeal.__init__(self, ring, name)


class MorCategoryConstruction(
    OwnedCategoryMixin, OwnedCategoryObject, SageHomsetsCategory, Parent
):
    r"""Sage-Mor backend for a category's ``MorCategory``.

    This class is a specialization, not the definition of a Mor category.
    Categories whose Mor objects are not sets use another implementation.
    """

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageHomsetsCategory.__init__(self, category)

    def extra_super_categories(self) -> list:
        r"""A set-valued Mor object inherits the owned set Mor implementation.

        Sage's ``MorsOf`` answers a flat ``[Mors()]``: it does not carry
        a category's own super categories across the construction, so
        ``Modules(R).MorCategory()`` would not inherit
        ``Sets().MorCategory()``.  The owned set-valued Mor chain has a root, and a chain
        that does not reach its root cannot construct -- cooperative
        ``super().__init__`` runs off the end into ``object``.  This states
        the missing edge once for every category using this backend.
        """
        from sage_extensions.categories.sets.set_categories import Sets

        owned_sets = Sets()
        categorical_mor = self.base_category().MorCategory()
        if self.base_category() is owned_sets:
            return [categorical_mor]
        return [categorical_mor, owned_sets.MorCategory()]

    def Of(self, source: Parent, target: Parent) -> SetObject:
        r"""Return the set-valued Mor object supplied by Sage's Mor backend."""
        return self._object(source, target, self)

    def _object(
        self,
        source: Parent,
        target: Parent,
        placement: SageCategory,
    ) -> SetObject:
        r"""Construct one locally small Mor object through its owned type."""
        return placement.ObjectType(
            domain=source,
            codomain=target,
            category=self.base_category(),
        )


class _SageMorCategoryOf(
    OwnedCategoryMixin, OwnedCategoryObject, SageHomsetsOf, Parent
):
    r"""Owned base over Sage's category-specific mors base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageHomsetsOf.__init__(self, category)


class _SageMorCategoryRoot(
    _SingletonClasscallMixin,
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageHomsets,
    Parent,
):
    r"""Owned base over Sage's singleton mors category."""

    def __init__(self) -> None:
        self._init_cat_object()
        SageHomsets.__init__(self)

    def Endset(self) -> SageCategory:
        r"""Return Sage's root category of endomorphism sets.

        Forced by Sage's singleton-axiom descriptor, not by mathematics.
        Sage's ``Mors.Endset`` nested class records Sage's own ``Mors``
        as its base category class, and ``CategoryWithAxiom.__classget__``
        asserts that the class it is reached through is that one
        (``sage/categories/category_with_axiom.py``).  Reached through an owned
        ``Mors`` the assertion fails, so the axiom is named here instead.
        A subcategory that owns the ``Endset`` axiom declares it as its own
        nested class, which replaces this method outright.
        """
        return SageHomsets().Endset()


class FunctorialConstructionCategory(
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageFunctorialConstructionCategory,
    Parent,
):
    r"""Owned base over Sage's functorial construction category.

    Sage's construction methods for subobjects, quotients, and similar
    constructions do not build axiom categories; they build
    ``FunctorialConstructionCategory`` descendants.  A construction declared
    over Sage's raw base keeps ``category() == Objects()`` and leaves
    :math:`\mathbf{Cat}` even when the base category it is taken over is owned.
    """

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageFunctorialConstructionCategory.__init__(self, category)


class CovariantConstructionCategory(
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageCovariantConstructionCategory,
    Parent,
):
    r"""Owned base over Sage's covariant construction base."""

    def __init__(self, category: SageCategory, *structure: CategoryObject) -> None:
        self._init_cat_object()
        SageCovariantConstructionCategory.__init__(self, category, *structure)


class RegressiveCovariantConstructionCategory(
    OwnedCategoryMixin,
    OwnedCategoryObject,
    SageRegressiveCovariantConstructionCategory,
    Parent,
):
    r"""Owned base over Sage's regressive covariant construction base."""

    def __init__(self, category: SageCategory, *structure: CategoryObject) -> None:
        self._init_cat_object()
        SageRegressiveCovariantConstructionCategory.__init__(
            self, category, *structure
        )


class SubobjectsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageSubobjectsCategory, Parent
):
    r"""Owned base over Sage's subobject construction base."""

    @classmethod
    def default_super_categories(
        cls,
        category: SageCategory,
    ) -> SageCategory:
        r"""Keep the object category without adding set-theoretic subquotients."""
        return category

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageSubobjectsCategory.__init__(self, category)

    class ParentMethods:
        r"""A subobject is its inclusion.  Read the remainder from that.

        A subobject of :math:`B` is the pair :math:`(A, f: A \hookrightarrow
        B)`.  Thus the object that contains it is ``f.codomain()``.

        The migrated source also declared ``ambient()``.  That declaration is
        not here.  It gives the codomain a second name, and it is a
        data-accessor obligation.  The construction chain supplies such data.
        """

        def inclusion(self) -> Morphism:
            r"""Return the inclusion morphism of this subobject."""
            return self.structure_morphism()

        @final
        def lift(self, x: CategoryElement) -> CategoryElement:
            r"""Return the image of ``x`` under the inclusion."""
            return self.inclusion()(x)


class QuotientsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageQuotientsCategory, Parent
):
    r"""Owned base over Sage's quotient construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageQuotientsCategory.__init__(self, category)


class SubquotientsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageSubquotientsCategory, Parent
):
    r"""Owned base over Sage's subquotient construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageSubquotientsCategory.__init__(self, category)


class IsomorphicObjectsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageIsomorphicObjectsCategory, Parent
):
    r"""Owned base over Sage's isomorphic-object construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageIsomorphicObjectsCategory.__init__(self, category)


class RealizationsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageRealizationsCategory, Parent
):
    r"""Owned base over Sage's realization construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageRealizationsCategory.__init__(self, category)


class WithRealizationsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageWithRealizationsCategory, Parent
):
    r"""Owned base over Sage's with-realizations construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageWithRealizationsCategory.__init__(self, category)


class DualObjectsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageDualObjectsCategory, Parent
):
    r"""Owned base over Sage's dual-object construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageDualObjectsCategory.__init__(self, category)


class TensorProductsCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageTensorProductsCategory, Parent
):
    r"""Owned base over Sage's tensor-product construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageTensorProductsCategory.__init__(self, category)


class AlgebrasCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageAlgebrasCategory, Parent
):
    r"""Owned base over Sage's algebra functor construction base."""

    def __init__(self, category: SageCategory, base_ring: CategoryObject) -> None:
        self._init_cat_object()
        SageAlgebrasCategory.__init__(self, category, base_ring)


class FilteredModulesCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageFilteredModulesCategory, Parent
):
    r"""Owned base over Sage's filtered-module construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageFilteredModulesCategory.__init__(self, category)


class GradedModulesCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageGradedModulesCategory, Parent
):
    r"""Owned base over Sage's graded-module construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageGradedModulesCategory.__init__(self, category)


class SuperModulesCategory(
    OwnedCategoryMixin, OwnedCategoryObject, SageSuperModulesCategory, Parent
):
    r"""Owned base over Sage's super-module construction base."""

    def __init__(self, category: SageCategory) -> None:
        self._init_cat_object()
        SageSuperModulesCategory.__init__(self, category)
