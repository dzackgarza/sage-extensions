r"""A represented category ``Cat`` of categories, functors, and natural transformations."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, overload

from sage.categories.category import Category
from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.element import parent
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoryPacketMethods,
    FixedMorCategory,
    MorCategories,
    MorCategoryConstruction,
    _category_mor_parent,
    _declared_construction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import Objects
from sage_extensions.categories.functors.core import (
    _CompositeFunctor,
    Functor,
    IdentityFunctor,
    NaturalTransformation,
)
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow, object_level

if TYPE_CHECKING:
    from sage_extensions.categories.sets.indexed_families import IndexedFamily
    from sage_extensions.logic import Predicate


class FunctorMorCategoryConstruction(MorCategoryConstruction):
    r"""The family ``(C,D) |-> [C,D]``, with its actual natural transformations."""

    def fixed_category_class(self) -> type[_FunctorCategory]:
        return _FunctorCategory

    def fixed_category_class_for(
        self,
        domain: Category,
        codomain: Category,
    ) -> type[_FunctorCategory]:
        r"""The realization of ``[C, D]`` for these endpoints.

        One category object for each pair.  Out of the walking arrow
        ``[1] = FiniteOrdinalCategory(2)`` it is the arrow category, whose
        realization adds the vocabulary the shape ``[1]`` names (an arrow,
        its source and target, the two edges of a square) and nothing else.
        """
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            _WalkingArrowFunctorCategory,
        )
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
            _FiniteSequenceFunctorCategory,
        )

        match domain:
            case shape if shape is FiniteOrdinalCategory(2):
                realization = _WalkingArrowFunctorCategory
            case FiniteOrdinalCategory():
                realization = _FiniteSequenceFunctorCategory
            case _:
                return self.fixed_category_class()
        # [shape, D] is a functorial construction in D: the codomain's class
        # declares the construction's class for its arrow and sequence
        # diagrams as the nested ``ArrowDiagrams`` / ``SequenceDiagrams``
        # (subclasses of these realizations), through its class inheritance.
        name = "ArrowDiagrams" if realization is _WalkingArrowFunctorCategory else "SequenceDiagrams"
        construction = _declared_construction(codomain, name)
        return realization if construction is None else construction

    def Of(
        self,
        domain: Category,
        codomain: Category,
    ) -> _FunctorCategory:
        category = self.base_category()
        source, target = category.object(domain), category.object(codomain)
        cached = self._cached_between(source, target)
        if cached is not None:
            return cached
        return self._remember_between(
            source, target,
            typecall(
                self.fixed_category_class_for(source, target),
                category,
                source,
                target,
            ),
        )

    Between = Of


class Cat(CategoryPacketMethods, Category):
    r"""The represented category of categories.

    A category is an object of ``Cat`` by placement: the owned category bases
    record ``Cat()`` as a category's category when it is built
    (``OwnedCategoryObject`` in ``owned_category.py``), a fixed Mor category
    records ``MorCategories()``, and ``Cat`` records itself.  The expectation
    ``Cat() in Cat()`` (``tests/constructions/test_categorical_constructions_construct.py``)
    is that last placement; ``Cat`` is not built on the owned base, which
    would ask for ``Cat()`` while ``Cat`` is under construction.
    """

    _MorCategory = FunctorMorCategoryConstruction
    _construction_instance = None

    def __init__(self) -> None:
        self._arrows = {}
        if Cat._construction_instance is not None:
            raise RuntimeError("Cat construction is re-entrant before its owned Objects root is initialized")
        # Objects records Cat as its placement category. Publish this partially
        # initialized instance only across the superclass construction, so
        # Objects._init_cat_object can reuse it rather than recursively calling
        # Cat() while Cat's supercategories are being assembled.
        Cat._construction_instance = self
        try:
            super().__init__()
        finally:
            Cat._construction_instance = None

    def an_object(self) -> Category:
        r"""The category of sets, which every owned chain roots at."""
        from sage_extensions.categories.sets.set_categories import Sets

        return Sets()

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.objects import Objects

        return [Objects()]

    def category(self) -> Cat:
        r"""``Cat`` is placed in itself."""
        return self

    def __contains__(self, candidate: Any) -> bool:
        r"""Whether ``candidate`` is a category, read from its placement.

        Placement answers it for every category whose ``category()`` records
        ``Cat`` or a subcategory of it.  A Mor category realized on Sage's
        ``Mor`` records its enrichment there instead, and its placement
        among Mor categories is recorded by the family that built it, which
        ``MorCategories`` reads.
        """
        return super().__contains__(candidate) or candidate in MorCategories()

    def object(self, category: Category) -> Category:
        r"""Admit the actual category as an object of ``Cat``."""
        if not isinstance(category, Category):
            raise TypeError(f"an object of Cat is a category, but {category!r} is not a category")
        return category

    _mor_endpoint = object

    @cached_method(key=lambda self, domain, codomain: (id(self.object(domain)), id(self.object(codomain))))
    def functor_mor(
        self,
        domain: Category,
        codomain: Category,
    ) -> _FunctorCategory:
        return self.MorCategory().Of(
            self.object(domain),
            self.object(codomain),
        )

    def arrow(self, functor: Functor) -> Functor:
        key = id(functor)
        cached = self._arrows.get(key)
        if cached is not None and cached.functor() is functor:
            return cached
        result = self.functor_mor(functor.domain(), functor.codomain())(functor)
        self._arrows[key] = result
        return result

    def identity(self, category: Category) -> Functor:
        return self.functor_mor(category, category).identity()

    def compose(
        self,
        second: Functor,
        first: Functor,
    ) -> Functor:
        if first.codomain() is not second.domain():
            raise ValueError(
                f"cannot compose the functors {second} o {first}: {first} ends at {first.codomain()}, but "
                f"{second} starts at {second.domain()}"
            )
        return second * first

    def SliceOver(self, base_object: Category) -> Category:
        r"""Return the slice ``Cat/base_object``."""
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            SliceCategory,
        )

        return SliceCategory(self, base_object)

    def fiber(self, functor: Functor, target_object: ObjectOfCategory) -> Category:
        r"""Objects over ``target_object`` and arrows mapping to its identity.

        This is ``Functor.Fiber`` in Mathlib's
        ``CategoryTheory/FiberedCategory/Fiber.lean``.
        """
        pass

    def fiber_inclusion(self, functor: Functor, target_object: ObjectOfCategory) -> Functor:
        r"""Include the strict fiber of ``functor`` in its domain category."""
        pass

    class ParentMethods:
        r"""What a category can do, as an object of ``Cat``.

        Sage requires a nested ``ParentMethods`` declaration to be a plain class:
        inheriting another implementation class makes category construction
        emit ``ParentMethods should not have a super class`` in a fresh session.
        The Mor-packet operations below are therefore aliases of their single
        implementation in :class:`CategoryPacketMethods`, not a second
        implementation and not a superclass of this declaration.

        Every owned category receives these methods through
        ``subcategory_class``; ``CatConstructionsMixin`` on the owned root
        carries it through joins and functorial constructions.
        """

        _mor_endpoint = CategoryPacketMethods._mor_endpoint
        _mor_endpoints_in_supercategory = CategoryPacketMethods._mor_endpoints_in_supercategory
        ArrowCategory = CategoryPacketMethods.ArrowCategory
        Core = CategoryPacketMethods.Core
        category_packet = CategoryPacketMethods.category_packet
        MorCategory = CategoryPacketMethods.MorCategory
        EndCategory = CategoryPacketMethods.EndCategory
        MonoCategory = CategoryPacketMethods.MonoCategory
        EpiCategory = CategoryPacketMethods.EpiCategory
        IsoCategory = CategoryPacketMethods.IsoCategory
        AutCategory = CategoryPacketMethods.AutCategory
        Mor = CategoryPacketMethods.__dict__["Mor"]
        End = CategoryPacketMethods.__dict__["End"]
        Mono = CategoryPacketMethods.__dict__["Mono"]
        Epi = CategoryPacketMethods.__dict__["Epi"]
        Iso = CategoryPacketMethods.__dict__["Iso"]
        Aut = CategoryPacketMethods.__dict__["Aut"]

        def identity_functor(self):
            return Cat().identity(self)

        def Diagram(self, index_category: Category) -> Category:
            r"""Return the category of diagrams in ``self`` indexed by ``index_category``."""
            return Cat().Mor(index_category, self)

        def Product(self, factors) -> Category:
            r"""Return the category of cones over the selected discrete product diagram."""
            from sage_extensions.categories.abstract_categories.products import (
                _ProductConeCategory,
            )

            return _ProductConeCategory(self.product_construction(factors).diagram())

        def Coproduct(self, cofactors) -> Category:
            r"""Return the category of cocones under the selected discrete coproduct diagram."""
            from sage_extensions.categories.abstract_categories.products import (
                _CoproductCoconeCategory,
            )

            return _CoproductCoconeCategory(self.coproduct_construction(cofactors).diagram())

        def Biproduct(self, factors) -> Category:
            r"""Return the owned category of the selected biproduct object."""
            construction = getattr(self, "biproduct", None)
            if construction is None:
                raise TypeError(f"biproducts are not represented in {self}")
            return construction(factors).category()

        def TensorProduct(self, factors) -> Category:
            r"""Return the owned category of the selected tensor-product object."""
            construction = getattr(self, "tensor_product", None)
            if construction is None:
                raise TypeError(f"tensor products are not represented in {self}")
            return construction(factors).category()

        def DirectSum(self) -> Category:
            r"""Return objects of ``self`` with a chosen direct-sum decomposition."""
            from sage_extensions.categories.abstract_categories.direct_sum_objects import (
                DirectSumObjects,
            )

            return DirectSumObjects(self)

        def DirectedSystem(self, index_category: Category) -> Category:
            r"""Return covariant diagrams in ``self`` on a directed index category."""
            from sage_extensions.categories.abstract_categories.products import (
                DirectedSystem,
            )

            return DirectedSystem(index_category, self)

        def InverseSystem(self, index_category: Category) -> Category:
            r"""Return inverse diagrams in ``self`` indexed by ``index_category``."""
            from sage_extensions.categories.abstract_categories.products import (
                InverseSystem,
            )

            return InverseSystem(index_category, self)

        def Cone(self, diagram: Functor) -> Category:
            r"""Return the category of cones over ``diagram`` in ``self``."""
            from sage_extensions.categories.abstract_categories.products import (
                _ConeCategory,
            )

            if diagram.codomain() is not self:
                raise ValueError(f"the diagram {diagram} does not take values in {self}")
            return _ConeCategory(diagram)

        def Cocone(self, diagram: Functor) -> Category:
            r"""Return the category of cocones under ``diagram`` in ``self``."""
            from sage_extensions.categories.abstract_categories.products import (
                _CoconeCategory,
            )

            if diagram.codomain() is not self:
                raise ValueError(f"the diagram {diagram} does not take values in {self}")
            return _CoconeCategory(diagram)

        def Arrow(self) -> Category:
            r"""Return the arrow category ``[1, self]`` through Cat's owned Mor construction."""
            return self.ArrowCategory()

        def IsoArrow(self) -> Category:
            r"""Return the full subcategory of ``Arrow()`` on isomorphisms."""
            return self.IsoArrowCategory()

        def core(self):
            r"""Return the core groupoid of this category."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _CoreCategory,
            )

            return _CoreCategory(self)

        def inclusion_into(self, supercategory: Category):
            r"""Return the canonical inclusion functor into a declared supercategory."""
            from sage_extensions.categories.functors.core import _CategoryInclusionFunctor

            return _CategoryInclusionFunctor(self, supercategory)

        def domain_functor(self):
            r"""Return the domain functor ``Ar(self) -> self``."""
            from sage_extensions.categories.abstract_categories.functors import (
                _domain_functor,
            )

            return _domain_functor(self)

        def codomain_functor(self):
            r"""Return the codomain functor ``Ar(self) -> self``."""
            from sage_extensions.categories.abstract_categories.functors import (
                _codomain_functor,
            )

            return _codomain_functor(self)

        @cached_method
        def class_set_construction(self):
            r"""Coequalize source and target on a complete selected arrow set.

            The result is objects modulo zigzags of morphisms, and hence
            isomorphism classes when the category is a groupoid. This
            implementation requires a finite selected set of objects and
            a represented complete set of arrows, retaining the actual
            source/target maps and their universal quotient.
            """
            from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
            from sage_extensions.categories.sets.indexed_families import IndexedFamily
            from sage_extensions.categories.sets.set_categories import EnumeratedSets, FiniteSets, Sets

            indices = self.object_set()
            if indices not in FiniteSets() or indices not in EnumeratedSets():
                raise TypeError(
                    f"the class set of {self} requires its complete object and "
                    "arrow sets, not an unenumerated possible-object collection"
                )
            objects = (
                finite_ordered_set(tuple(self.objects()))
                if hasattr(self, "objects") else indices
            )
            if not all(obj in self for obj in objects):
                raise TypeError(f"the selected object set of {self} is not admitted in that category")
            presented = self.arrows()
            arrows = (
                finite_ordered_set(tuple(presented))
                if isinstance(presented, IndexedFamily)
                and presented.index_set() in FiniteSets()
                and presented.index_set() in EnumeratedSets()
                else presented
            )
            if arrows not in Sets():
                raise TypeError(
                    f"the category {self} needs a complete owned arrow set, "
                    f"but its arrow presentation is {arrows}"
                )
            source = Sets().Mor(arrows, objects)(
                lambda arrow: objects(arrow.domain())
            )
            target = Sets().Mor(arrows, objects)(
                lambda arrow: objects(arrow.codomain())
            )
            return Sets().coequalizer_construction(source, target)

        @cached_method
        def class_set(self):
            r"""Return connected components, or iso-classes of a groupoid."""
            return self.class_set_construction().object()

        def diagonal_functor(self):
            r"""Return the diagonal functor ``self -> self x self``."""
            from sage_extensions.categories.abstract_categories.functors import (
                _diagonal_functor,
            )

            return _diagonal_functor(self)

        def product_functor(self):
            r"""Return this category's selected binary-product functor."""
            from sage_extensions.categories.abstract_categories.functors import (
                _product_functor,
            )

            return _product_functor(self)

        def coproduct_functor(self):
            r"""Return this category's selected binary-coproduct functor."""
            from sage_extensions.categories.abstract_categories.functors import (
                _coproduct_functor,
            )

            return _coproduct_functor(self)

        def limit_functor(self, index_category: Category):
            r"""Return the selected limit functor ``[index_category,self] -> self``."""
            return self.Limits(index_category).defining_functor()

        def colimit_functor(self, index_category: Category):
            r"""Return the selected colimit functor ``[index_category,self] -> self``."""
            return self.Colimits(index_category).defining_functor()

        def Limits(self, index_category: Category) -> Category:
            r"""Return the selected-limit construction category for this target."""
            from sage_extensions.categories.abstract_categories.products import (
                _LimitsOfCategory,
            )

            return _LimitsOfCategory(index_category, self)

        def Colimits(self, index_category: Category) -> Category:
            r"""Return the selected-colimit construction category for this target."""
            from sage_extensions.categories.abstract_categories.products import (
                _ColimitsOfCategory,
            )

            return _ColimitsOfCategory(index_category, self)

        def Products(self, index_category: Category) -> Category:
            r"""Return the selected-product construction category for this target."""
            from sage_extensions.categories.abstract_categories.products import (
                _ProductsOfCategory,
            )

            return _ProductsOfCategory(index_category, self)

        def Coproducts(self, index_category: Category) -> Category:
            r"""Return the selected-coproduct construction category for this target."""
            from sage_extensions.categories.abstract_categories.products import (
                _CoproductsOfCategory,
            )

            return _CoproductsOfCategory(index_category, self)

        ObjectType = CategoryPacketMethods.ObjectType
        ElementType = CategoryPacketMethods.ElementType

        @abstract_method(optional=True)
        def _categorical_tensor_product(self, left: Parent, right: Parent) -> ObjectOfCategory:
            r"""Return this category's represented tensor product of two objects."""

        @abstract_method(optional=True)
        def _categorical_biproduct(self, left: Parent, right: Parent) -> ObjectOfCategory:
            r"""Return this category's represented biproduct of two objects."""

        @abstract_method(optional=True)
        def _categorical_product(self, left: Parent, right: Parent) -> ObjectOfCategory:
            r"""Return this category's represented product of two objects."""

        @abstract_method(optional=True)
        def _categorical_product_construction(self, factors):
            r"""Return the selected product with its discrete diagram and universal cone."""

        @abstract_method(optional=True)
        def _categorical_coproduct(self, left: Parent, right: Parent) -> ObjectOfCategory:
            r"""Return this category's represented coproduct of two objects."""

        @abstract_method(optional=True)
        def _categorical_coproduct_construction(self, factors):
            r"""Return the selected coproduct with its discrete diagram and universal cocone."""

        @abstract_method(optional=True)
        def _categorical_pushout(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ) -> ObjectOfCategory:
            r"""Return this category's represented pushout of a span."""

        @abstract_method(optional=True)
        def _categorical_pullback(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ) -> ObjectOfCategory:
            r"""Return this category's represented pullback of a cospan."""

        @abstract_method(optional=True)
        def _categorical_equalizer(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ) -> ObjectOfCategory:
            r"""Return this category's represented equalizer of parallel arrows."""

        @abstract_method(optional=True)
        def _categorical_equalizer_construction(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ):
            r"""Return the selected equalizer with its diagram, cone and factorization."""

        @abstract_method(optional=True)
        def _categorical_coequalizer(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ) -> ObjectOfCategory:
            r"""Return this category's represented coequalizer of parallel arrows."""

        @abstract_method(optional=True)
        def _categorical_coequalizer_construction(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ):
            r"""Return the selected coequalizer with its diagram, cocone and factorization."""

        @abstract_method(optional=True)
        def _categorical_equalizer_family(self, morphisms: IndexedFamily) -> ObjectOfCategory:
            r"""Return this category's represented equalizer of an indexed arrow family."""

        @abstract_method(optional=True)
        def _categorical_equalizer_family_construction(self, morphisms: IndexedFamily):
            r"""Return the selected wide equalizer with its diagram, cone and factorization."""

        @abstract_method(optional=True)
        def _categorical_coequalizer_family(self, morphisms: IndexedFamily) -> ObjectOfCategory:
            r"""Return this category's represented coequalizer of an indexed arrow family."""

        @abstract_method(optional=True)
        def _categorical_coequalizer_family_construction(self, morphisms: IndexedFamily):
            r"""Return the selected wide coequalizer with its diagram, cocone and factorization."""

        def product_construction(self, factors):
            r"""Return this category's selected product construction on ``factors``."""
            construction = self._categorical_product_construction
            assert construction is not NotImplemented, (
                f"no construction of products is available in {self}"
            )
            return construction(factors)

        def coproduct_construction(self, factors):
            r"""Return this category's selected coproduct construction on ``factors``."""
            construction = self._categorical_coproduct_construction
            assert construction is not NotImplemented, (
                f"no construction of coproducts is available in {self}"
            )
            return construction(factors)

        def coproduct(self, factors):
            r"""Return this category's selected binary coproduct.

            The universal operation is common to categories.  Its selected
            supplier determines the object and its structure maps: a module
            sum and a commutative-algebra tensor product are different
            constructions, even when their inputs share module placement.
            """
            from sage_extensions.categories.abstract_categories.products import (
                _two_factors_of,
            )

            left, right = _two_factors_of(factors, name="Coproduct factors")
            construction = self._categorical_coproduct
            assert construction is not NotImplemented, (
                f"no construction of binary coproducts is available in {self}"
            )
            return construction(left, right)

        def equalizer_construction(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ):
            r"""Return this category's selected equalizer construction."""
            assert left_morphism.domain() is right_morphism.domain(), (
                f"an equalizer needs parallel maps f, g: X -> Y, but {left_morphism} starts at "
                f"{left_morphism.domain()} and {right_morphism} starts at {right_morphism.domain()}"
            )
            assert left_morphism.codomain() is right_morphism.codomain(), (
                f"an equalizer needs parallel maps f, g: X -> Y, but {left_morphism} ends at "
                f"{left_morphism.codomain()} and {right_morphism} ends at {right_morphism.codomain()}"
            )
            construction = self._categorical_equalizer_construction
            assert construction is not NotImplemented, (
                f"no construction of equalizers is available in {self}"
            )
            return construction(left_morphism, right_morphism)

        def coequalizer_construction(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ):
            r"""Return this category's selected coequalizer construction."""
            assert left_morphism.domain() is right_morphism.domain(), (
                f"a coequalizer needs parallel maps f, g: X -> Y, but {left_morphism} starts at "
                f"{left_morphism.domain()} and {right_morphism} starts at {right_morphism.domain()}"
            )
            assert left_morphism.codomain() is right_morphism.codomain(), (
                f"a coequalizer needs parallel maps f, g: X -> Y, but {left_morphism} ends at "
                f"{left_morphism.codomain()} and {right_morphism} ends at {right_morphism.codomain()}"
            )
            construction = self._categorical_coequalizer_construction
            assert construction is not NotImplemented, (
                f"no construction of coequalizers is available in {self}"
            )
            return construction(left_morphism, right_morphism)

        def equalizer(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ) -> ObjectOfCategory:
            r"""Return this category's represented equalizer of a parallel pair."""
            assert left_morphism.domain() is right_morphism.domain(), (
                f"an equalizer needs parallel maps f, g: X -> Y, but {left_morphism} starts at "
                f"{left_morphism.domain()} and {right_morphism} starts at {right_morphism.domain()}"
            )
            assert left_morphism.codomain() is right_morphism.codomain(), (
                f"an equalizer needs parallel maps f, g: X -> Y, but {left_morphism} ends at "
                f"{left_morphism.codomain()} and {right_morphism} ends at {right_morphism.codomain()}"
            )
            construction = self._categorical_equalizer
            assert construction is not NotImplemented, (
                f"no construction of the equalizer of {left_morphism} and {right_morphism} is available in {self}"
            )
            return construction(left_morphism, right_morphism)

        def coequalizer(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
        ) -> ObjectOfCategory:
            r"""Return this category's represented coequalizer of a parallel pair."""
            assert left_morphism.domain() is right_morphism.domain(), (
                f"a coequalizer needs parallel maps f, g: X -> Y, but {left_morphism} starts at "
                f"{left_morphism.domain()} and {right_morphism} starts at {right_morphism.domain()}"
            )
            assert left_morphism.codomain() is right_morphism.codomain(), (
                f"a coequalizer needs parallel maps f, g: X -> Y, but {left_morphism} ends at "
                f"{left_morphism.codomain()} and {right_morphism} ends at {right_morphism.codomain()}"
            )
            construction = self._categorical_coequalizer
            assert construction is not NotImplemented, (
                f"no construction of the coequalizer of {left_morphism} and {right_morphism} is available in {self}"
            )
            return construction(left_morphism, right_morphism)

        def equalizer_of_family(self, morphisms) -> ObjectOfCategory:
            r"""Return this category's represented wide equalizer.

            ``morphisms`` is a nonempty indexed family of parallel arrows
            ``f_i : X -> Y``.  An :class:`IndexedFamily` retains its actual
            index set; a bare iterable is finite ingress on the canonical
            finite ordinal.  The selected construction is responsible for the
            common equalizing map and universal factorization.
            """
            from sage_extensions.categories.sets.indexed_families import IndexedFamily

            match morphisms:
                case IndexedFamily():
                    family = morphisms
                case _:
                    from sage_extensions.categories.sets.finite_families import (
                        finite_family,
                    )

                    family = finite_family(tuple(morphisms))
            construction = self._categorical_equalizer_family
            assert construction is not NotImplemented, (
                f"no construction of wide equalizers is available in {self}"
            )
            return construction(family)

        def equalizer_of_family_construction(self, morphisms):
            r"""Return the selected wide equalizer with its indexed diagram and universal cone.

            The construction retains the family of parallel arrows rather than
            replacing it by a binary fold.  Its apex is
            :meth:`equalizer_of_family`; its structure map and ``factor`` record
            the universal property.
            """
            from sage_extensions.categories.sets.indexed_families import IndexedFamily

            match morphisms:
                case IndexedFamily():
                    family = morphisms
                case _:
                    from sage_extensions.categories.sets.finite_families import (
                        finite_family,
                    )

                    family = finite_family(tuple(morphisms))
            construction = self._categorical_equalizer_family_construction
            assert construction is not NotImplemented, (
                f"no selected construction of wide equalizers is available in {self}"
            )
            return construction(family)

        def coequalizer_of_family(self, morphisms) -> ObjectOfCategory:
            r"""Return this category's represented wide coequalizer.

            ``morphisms`` is a nonempty indexed family of parallel arrows
            ``f_i : X -> Y``.  An :class:`IndexedFamily` retains its actual
            index set; a bare iterable is finite ingress on the canonical
            finite ordinal.  The selected construction is responsible for the
            common coequalizing map and universal factorization.
            """
            from sage_extensions.categories.sets.indexed_families import IndexedFamily

            match morphisms:
                case IndexedFamily():
                    family = morphisms
                case _:
                    from sage_extensions.categories.sets.finite_families import (
                        finite_family,
                    )

                    family = finite_family(tuple(morphisms))
            construction = self._categorical_coequalizer_family
            assert construction is not NotImplemented, (
                f"no construction of wide coequalizers is available in {self}"
            )
            return construction(family)

        def coequalizer_of_family_construction(self, morphisms):
            r"""Return the selected wide coequalizer with its indexed diagram and universal cocone.

            The construction retains the family of parallel arrows rather than
            replacing it by a binary fold.  Its apex is
            :meth:`coequalizer_of_family`; its costructure map and ``factor``
            record the universal property.
            """
            from sage_extensions.categories.sets.indexed_families import IndexedFamily

            match morphisms:
                case IndexedFamily():
                    family = morphisms
                case _:
                    from sage_extensions.categories.sets.finite_families import (
                        finite_family,
                    )

                    family = finite_family(tuple(morphisms))
            construction = self._categorical_coequalizer_family_construction
            assert construction is not NotImplemented, (
                f"no selected construction of wide coequalizers is available in {self}"
            )
            return construction(family)

        @abstract_method(optional=True)
        def _categorical_product_morphism(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
            source: Parent,
            target: Parent,
        ) -> Morphism:
            r"""Return the induced morphism between represented binary products."""

        @abstract_method(optional=True)
        def _categorical_coproduct_morphism(
            self,
            left_morphism: Morphism,
            right_morphism: Morphism,
            source: Parent,
            target: Parent,
        ) -> Morphism:
            r"""Return the induced morphism between represented binary coproducts."""

        def fiber_product(self, left_leg: Morphism, right_leg: Morphism) -> ObjectOfCategory:
            r"""Return the fiber product of the cospan these two legs form.

            \(A\times_C B\) is the equalizer of \(f p_A\) and \(g p_B\) on
            \(A\times B\): the subobject on which the two legs agree.  A
            category with products and equalizers has this, so it is defined
            here once, from those; a category with a better construction of its
            own supplies it instead.
            """
            return self.pullback_construction(left_leg, right_leg).object()

        def pullback_construction(self, left_leg: Morphism, right_leg: Morphism):
            r"""Return the selected pullback cone of ``X -> Z <- Y``.

            A pullback is a limit of the literal cospan diagram. The existing
            finite-diagram limit constructor supplies its universal cone,
            projections to X and Y, compatibility map to Z and factorization.
            """
            from sage_extensions.categories.abstract_categories.products import (
                _TwoLegDiagram,
            )

            diagram = _TwoLegDiagram(left_leg, right_leg, self, cospan=True)
            return self.Limits(diagram.domain()).construction(diagram)

        def span(self, left_leg: Morphism, right_leg: Morphism) -> ObjectOfCategory:
            r"""Return the span these two legs form, as an object of this category.

            The span is an object: it has an apex, two legs, a diagram over
            the shape \(\cdot\leftarrow\cdot\rightarrow\cdot\), and its own
            colimit, which it asks this category for.
            """
            from sage_extensions.categories.abstract_categories.products import (
                _discrete_diagram,
            )

            assert left_leg.domain() is right_leg.domain(), (
                f"a span X <- Z -> Y needs both legs to start at one object, but {left_leg} starts at "
                f"{left_leg.domain()} and {right_leg} starts at {right_leg.domain()}"
            )
            legs = (left_leg, right_leg)
            diagram = _discrete_diagram(
                (left_leg.codomain(), right_leg.codomain()),
                target_category=self,
            )
            return (diagram).Spans().cone(
                left_leg.domain(),
                lambda index: legs[int(index.value())],
            )

        def ProductCones(self, factors) -> Category:
            r"""Return the category of product cones on ``factors`` in this category."""
            from sage_extensions.categories.abstract_categories.products import (
                _discrete_diagram,
            )

            return (_discrete_diagram(factors, target_category=self)).ProductCones()

        def CoproductCocones(self, factors) -> Category:
            r"""Return the category of coproduct cocones on ``factors`` in this category."""
            from sage_extensions.categories.abstract_categories.products import (
                _discrete_diagram,
            )

            return (_discrete_diagram(factors, target_category=self)).CoproductCocones()

        def pushout(self, left_leg: Morphism, right_leg: Morphism) -> ObjectOfCategory:
            r"""Return the pushout of the span these two legs form.

            A selected span supplier retains its existing construction.
            Otherwise use the common coproduct/coequalizer construction:
            Dual to the fiber product: the coequalizer of \(\iota_A f\) and
            \(\iota_B g\) on \(A\sqcup B\), which identifies \(f(c)\) with
            \(g(c)\).  A category with coproducts and coequalizers has this.
            """
            assert left_leg.domain() is right_leg.domain(), (
                f"a pushout needs a span X <- Z -> Y, but {left_leg} starts at {left_leg.domain()} "
                f"and {right_leg} starts at {right_leg.domain()}"
            )
            construction = self._categorical_pushout
            if construction is not NotImplemented:
                return construction(left_leg, right_leg)
            return self.pushout_construction(left_leg, right_leg).object()

        def pushout_construction(self, left_leg: Morphism, right_leg: Morphism):
            r"""Return the selected pushout cocone of ``X <- Z -> Y``.

            The existing finite-diagram colimit constructor retains the
            literal span, its two coprojections and the universal factor.
            """
            from sage_extensions.categories.abstract_categories.products import (
                _TwoLegDiagram,
            )

            diagram = _TwoLegDiagram(left_leg, right_leg, self, cospan=False)
            return self.Colimits(diagram.domain()).construction(diagram)

        def opposite(self) -> Category:
            r"""Return \(C^{op}\)."""
            from sage_extensions.categories.abstract_categories.category_constructions import (
                _OppositeCategory,
            )

            return _OppositeCategory(self)

        def presheaves(self, value_category: Category | None = None) -> Category:
            r"""Return \(\mathrm{Presh}(C, D) = [C^{op}, D]\), with \(D = \mathbf{Set}\) by default.

            The functor category itself, not a new class: presheaves are its
            objects and natural transformations its morphisms.  Sheaves on
            \(C\) for a coverage are a full subcategory of this one.
            """
            from sage_extensions.categories.sets.set_categories import Sets

            if value_category is None:
                value_category = Sets()
            return Cat().Mor(self.opposite(), value_category)

        def yoneda_embedding(self):
            r"""Return \(y: C \to [C^{op}, \mathbf{Set}]\), \(X \mapsto \mathrm{Mor}_C(-, X)\)."""
            from sage_extensions.categories.abstract_categories.presheaves import (
                _YonedaEmbedding,
            )

            return _YonedaEmbedding(self)

        def EndArrowCategory(self) -> Category:
            r"""Return the full arrow subcategory on endomorphisms."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _EndArrowCategory,
            )

            return _EndArrowCategory(self)
        def IsoArrowCategory(self) -> Category:
            r"""Return the full arrow subcategory on represented isomorphisms."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _IsoArrowCategory,
            )

            return _IsoArrowCategory(self)
        def AutomorphismArrowCategory(self) -> Category:
            r"""Return the full arrow subcategory on automorphisms."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _AutomorphismArrowCategory,
            )

            return _AutomorphismArrowCategory(self)
        def MonomorphismArrowCategory(self) -> Category:
            r"""Return the full arrow subcategory on represented monomorphisms."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _MonomorphismArrowCategory,
            )

            return _MonomorphismArrowCategory(self)
        def EpimorphismArrowCategory(self) -> Category:
            r"""Return the full arrow subcategory on represented epimorphisms."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _EpimorphismArrowCategory,
            )

            return _EpimorphismArrowCategory(self)
        def WideSubcategory(self, arrow_category: Category) -> Category:
            r"""Return the wide subcategory with the selected arrow class."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _WideSubcategory,
            )

            return _WideSubcategory(self, arrow_category)
        def SliceOver(self, base_object: Parent) -> Category:
            r"""Return the slice \(C/X\)."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                SliceCategory,
            )

            return SliceCategory(self, base_object)
        def CosliceUnder(self, base_object: Parent) -> Category:
            r"""Return the coslice \(X/C\)."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                CosliceCategory,
            )

            return CosliceCategory(self, base_object)
        def SubobjectCategory(self, base_object: Parent) -> Category:
            r"""Return the category of subobjects of ``base_object`` here."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                SubobjectCategory,
            )

            return SubobjectCategory(self, base_object)

        def SubObject(self, base_object: Parent) -> Category:
            r"""Return the subobject category under the legacy construction name."""
            return self.SubobjectCategory(base_object)

        def SuperobjectCategory(self, base_object: Parent) -> Category:
            r"""Return the category of monic superobjects of ``base_object`` here."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                SuperobjectCategory,
            )

            return SuperobjectCategory(self, base_object)

        def SuperObject(self, base_object: Parent) -> Category:
            r"""Return the superobject category under the legacy construction name."""
            return self.SuperobjectCategory(base_object)

        def CoveringObjectCategory(self, base_object: Parent) -> Category:
            r"""Return the category of epic objects covering ``base_object`` here."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                CoveringObjectCategory,
            )

            return CoveringObjectCategory(self, base_object)

        def CoveringObject(self, base_object: Parent) -> Category:
            r"""Return the covering-object category under the legacy construction name."""
            return self.CoveringObjectCategory(base_object)

        def CoveredObjectCategory(self, base_object: Parent) -> Category:
            r"""Return the category of epic quotients covered by ``base_object`` here."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                CoveredObjectCategory,
            )

            return CoveredObjectCategory(self, base_object)

        def CoveredObject(self, base_object: Parent) -> Category:
            r"""Return the covered-object category under the legacy construction name."""
            return self.CoveredObjectCategory(base_object)

        def Kernel(self, morphism: Morphism) -> Category:
            r"""Return the category of kernel subobjects of ``morphism``."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                KernelCategory,
            )

            return KernelCategory(self, morphism)

        def Cokernel(self, morphism: Morphism) -> Category:
            r"""Return the category of cokernel quotients of ``morphism``."""
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                CokernelCategory,
            )

            return CokernelCategory(self, morphism)

        def Subobjects(self, base_object: Parent) -> Category:
            return self.SubobjectCategory(base_object)
        def Superobjects(self, base_object: Parent) -> Category:
            return self.SuperobjectCategory(base_object)
        def CoveringObjects(self, base_object: Parent) -> Category:
            return self.CoveringObjectCategory(base_object)
        def CoveredObjects(self, base_object: Parent) -> Category:
            return self.CoveredObjectCategory(base_object)

    def meet(self, categories: Iterable[Category]) -> Category:
        r"""Return the largest category contained in all of ``categories``.

        Categories are ordered here by inclusion: a subcategory is below its
        supercategories, which is what ``super_categories`` and
        ``is_subcategory`` already say throughout the owned graph.  In that
        order the greatest lower bound of a family is the category of the
        objects lying in every member, so this is the meet, and
        ``Modules(ZZ)`` met with ``FiniteSets()`` is the finite
        ``ZZ``-modules.

        Sage spells it ``Category.join`` because it orders categories
        the other way round, by their axioms: joining the axiom sets gives the
        more structured category, which is the smaller class of objects.
        Neither order is wrong and they are opposite, so the owned graph
        states its own rather than inheriting Sage's words.  The
        Sage's *operators* already read in the owned order -- ``A & B`` is
        this meet and ``A | B`` is the join below -- and only the two names
        are inverted.
        """
        members = tuple(categories)
        assert members, "the meet of categories needs at least one category, but none was given"

        # ``Category.join`` builds one dynamic class from every supplied
        # branch.  A strict supercategory contributes no new mathematics to
        # an intersection once one of its subcategories is already present,
        # and retaining both can make Sage linearize the same inherited
        # method provider twice.  Determine that redundancy only from the
        # declared category ancestry.  Calling ``is_subcategory`` here can
        # force ``parent_class`` construction while this meet is itself still
        # assembling those implementation classes, making the redundancy
        # check circular.  A relation known only through a runtime hook is
        # therefore conservatively left unpruned.
        reduced = []
        for member in members:
            if any(
                other is not member
                and member in other._set_of_super_categories
                and other not in member._set_of_super_categories
                for other in members
            ):
                continue
            if all(member is not known for known in reduced):
                reduced.append(member)

        if len(reduced) == 1:
            return reduced[0]
        from sage_extensions.owned_category import owned_category_join

        return owned_category_join(tuple(reduced))

    def join(self, categories: Iterable[Category]) -> Category:
        r"""Return the smallest category containing all of ``categories``.

        The least upper bound in the inclusion order: the objects of every
        member are objects of it, and it asks of them only what all of them
        ask.  ``Modules(ZZ)`` joined with ``FiniteSets()`` is ``Sets``.

        Sage spells it ``Category.meet``; see :meth:`meet` for why the
        two names arrive inverted.
        """
        members = tuple(categories)
        assert members, "the join of categories needs at least one category, but none was given"
        return Category.meet(members)

    def presheaves(self, category: Category, value_category: Category | None = None) -> Category:
        r"""The presheaf bifunctor on objects: \((C, D) \mapsto [C^{op}, D]\).

        ``Cat`` is not an object of itself here, so the bifunctor
        \(\mathbf{Cat}^{op} \times \mathbf{Cat} \to \mathbf{Cat}\) is stated by its two
        actions: this one on objects and :meth:`presheaf_transport` on arrows.
        """
        return category.presheaves(value_category)

    def presheaf_transport(self, site_functor: Functor, value_functor: Functor) -> Functor:
        r"""The presheaf bifunctor on arrows.

        For \(F: C' \to C\) and \(G: D \to D'\), the functor
        \([C^{op}, D] \to [C'^{op}, D']\) sending \(P \mapsto G \circ P \circ F^{op}\)
        and a natural transformation \(\eta\) to \(G \eta F^{op}\).
        """
        from sage_extensions.categories.abstract_categories.presheaves import (
            _PresheafTransport,
        )

        return _PresheafTransport(site_functor, value_functor)

    def product(self, factors: Iterable[Category]) -> Category:
        r"""Return $\prod_{i \in I} C_i$, the product of a family of categories.

        This is the same word as ``Modules(R).product``: ``Cat`` is a category
        with products, and its objects happen to be categories.  ``C * D`` is
        the operator notation that delegates here.

        The represented product category has objects
        are pairs ``(X, Y)`` addressed as ``first()`` and ``second()`` and over
        which the bifunctors are defined, so only the two-element index set is
        represented.  A larger index set is not folded into nested pairs: that
        object has projections only to the two halves of the nest, which is
        not the product over the index set that was asked for.
        """
        from sage_extensions.categories.abstract_categories.products import (
            _two_factors_of,
        )

        left, right = _two_factors_of(factors, name="Product factors")
        return self._categorical_product(left, right)

    def _categorical_product(self, left, right):
        from sage_extensions.categories.abstract_categories.category_constructions import (
            _ProductCategory,
        )

        return _ProductCategory(left, right)

    Mor = ParentMethods.__dict__["Mor"]
    End = ParentMethods.__dict__["End"]
    Mono = ParentMethods.__dict__["Mono"]
    Epi = ParentMethods.__dict__["Epi"]
    Iso = ParentMethods.__dict__["Iso"]
    Aut = ParentMethods.__dict__["Aut"]

    def _repr_(self) -> str:
        return "Cat: categories with functors as morphisms"


class NaturalTransformationMorphism(CategoricalArrow, CategoricalMor.ElementMethods):
    r"""A natural transformation as a morphism in a functor category."""

    def __init__(
        self,
        parent: NaturalTransformationMor,
        transformation: NaturalTransformation,
    ) -> None:
        Morphism.__init__(self, parent)
        if transformation.source() is not parent.source():
            raise ValueError(
                f"a morphism {self.domain()} -> {self.codomain()} in the functor category needs a natural "
                f"transformation from {parent.source()}, but {transformation} starts at {transformation.source()}"
            )
        if transformation.target() is not parent.target():
            raise ValueError(
                f"a morphism {self.domain()} -> {self.codomain()} in the functor category needs a natural "
                f"transformation to {parent.target()}, but {transformation} ends at {transformation.target()}"
            )
        self._transformation = transformation

    def transformation(self) -> NaturalTransformation:
        return self._transformation

    def component(self, obj: Parent) -> Morphism:
        return self.transformation().component(obj)

    def naturality_target_composite(self, morphism: Map) -> Morphism:
        return self.transformation().naturality_target_composite(morphism)

    def naturality_source_composite(self, morphism: Map) -> Morphism:
        return self.transformation().naturality_source_composite(morphism)

    def naturality_square(self, morphism: Map):
        return self.transformation().naturality_square(morphism)

    def __eq__(self, other: Any) -> bool | Predicate:
        r"""Compare every component when the domain is a represented finite chain.

        Equality of natural transformations is equality of their component
        families.  A finite ordinal supplies its complete object family, so
        the conjunction of the component equalities decides equality whenever
        those morphism equalities are decidable.  An undecided component stays
        a proposition; an arbitrary category is not silently enumerated.
        """
        if parent(other) is not self.parent():
            return False
        if self.transformation() is other.transformation():
            return True
        from sage_extensions.categories.abstract_categories.products import FiniteOrdinalCategory
        from sage_extensions.logic import AtomicProposition, conjunction

        shape = self.transformation().source().domain()
        if isinstance(shape, FiniteOrdinalCategory):
            return conjunction(self.component(obj) == other.component(obj) for obj in shape.objects())
        return AtomicProposition("equal", self, other)

    def __ne__(self, other: Any) -> bool | Predicate:
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self) -> int:
        return hash(id(self.parent()))

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        if self.domain() is self.codomain() and self is self.parent().identity():
            return other
        if other.domain() is other.codomain() and other is other.parent().identity():
            return self
        source = other.parent().source()
        target = self.parent().target()

        composite = NaturalTransformation(
            source,
            target,
            lambda obj: self.component(obj) * other.component(obj),
        )
        return self.parent().functor_category().Mor(other.domain(), self.codomain())(
            composite
        )


class NaturalTransformationMor(CategoricalMor):
    ElementMethods = NaturalTransformationMorphism

    def __init__(
        self,
        family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(
            self, family, domain, codomain
        )

    def functor_category(self) -> _FunctorCategory:
        return self.base_category()

    def source(self) -> Functor:
        return self.domain().functor()

    def target(self) -> Functor:
        return self.codomain().functor()

    def _element_constructor_(self, transformation):
        r"""A natural transformation between these two functors, given as one or by its components."""
        return self._transformation(transformation)

    def _transformation(self, transformation, *, element_class=None, construction_data=None):
        r"""Construct one transformation, optionally with a private realization."""
        match transformation:
            case NaturalTransformationMorphism():
                if transformation.parent() is self and element_class is None and construction_data is None:
                    return transformation
                transformation = transformation.transformation()
            case NaturalTransformation():
                pass
            case _:
                transformation = NaturalTransformation(
                    self.source(), self.target(), transformation
                )
        selected = self.element_class if element_class is None else element_class
        return selected(self, transformation, **dict(construction_data or {}))

    @object_level
    @cached_method
    def identity(self) -> NaturalTransformationMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity natural transformation exists only on Mor(F, F), but this is "
                f"Mor({self.domain()}, {self.codomain()})"
            )
        functor = self.source()
        return self(
            NaturalTransformation(
                functor,
                functor,
                lambda obj: _category_mor_parent(
                    functor.codomain(), functor(obj), functor(obj)
                ).identity(),
            )
        )


class NaturalTransformationMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = NaturalTransformationMor


class _EvaluationFunctor(Functor):
    r"""Evaluation at an object ``c`` of ``C``: the functor ``[C, D] -> D``.

    It sends a functor ``F`` to ``F(c)`` and a natural transformation
    ``alpha : F => G`` to its component ``alpha_c : F(c) -> G(c)``. This is
    Mathlib's ``CategoryTheory.evaluation`` (``CategoryTheory/Products/Basic.lean``).
    For a presheaf category ``[C^op, D]`` and an object ``U`` of ``C^op``, it is
    the sections functor ``Gamma(U, -)``.
    """

    def __init__(self, functor_category, index):
        assert index in functor_category.domain_category()
        self._index = index
        super().__init__(functor_category, functor_category.codomain_category())

    def evaluation_object(self):
        r"""Return the object of the domain category at which this functor evaluates."""
        return self._index

    def _apply_object(self, functor_object):
        return functor_object.functor()(self.evaluation_object())

    def _apply_morphism(self, transformation):
        return transformation.component(self.evaluation_object())


def _apex_isomorphism_in_subgroup(witness, subgroup, stabilizer_generators):
    r"""An element of ``w S`` in ``H``, using the finite coset action on ``G/H``.

    Here ``w = witness`` lies in ``G = subgroup.supergroup()``, ``H`` is
    ``subgroup``, and the supplied generators generate ``S``, the apex
    image of the source marking's automorphisms.  The functor and coslice
    categories own those markings and reconstruct the resulting marked
    isomorphism.  They share this finite-action computation.
    """
    from sage_extensions.categories.group.g_sets import FiniteGSets

    group = subgroup.supergroup()
    assert witness.domain() is witness.codomain() and witness.parent() is group, (
        f"{subgroup} is a subgroup of {group}, but the apex isomorphism "
        f"{witness.domain()} -> {witness.codomain()} does not lie in it"
    )
    cosets = group.left_cosets(subgroup)
    assert cosets in FiniteGSets(group), (
        f"an apex isomorphism in {subgroup} is found in the finite coset space "
        f"{group}/{subgroup}, which is not realized as a finite {group}-set"
    )
    stabilizer = group.subgroup(stabilizer_generators)
    inclusion = stabilizer.inclusion()
    action = FiniteGSets(stabilizer)(cosets, lambda element, point: cosets.act(inclusion(element), point))
    transporter = action.transporter_witness(cosets.coset_of(~witness), cosets.base_point())
    return None if transporter is None else witness * ~inclusion(transporter)


class _FunctorCategory(CategoricalMor):
    r"""The category ``[C,D]`` of represented functors and natural transformations.

    Unverified construction specimens: all Cat Mor entrances select one
    category, whose morphisms are actual natural transformations::

        sage: from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: points = finite_ordered_set(("a", "b"))
        sage: category = DiscreteCategory(points)
        sage: cat = Cat()
        sage: Mor = cat.Mor(category, category)
        sage: Mor is cat.MorCategory().Of(category, category)
        True
        sage: Mor is cat.EndCategory().Between(category, cat.object(category))
        True
        sage: Mor.arrow_set() is cat.functor_mor(category, category)
        True
        sage: identity = IdentityFunctor(category)
        sage: transformations = identity.natural_transformations_to(identity)
        sage: transformations is Mor.Mor(Mor(identity), Mor(identity))
        True
        sage: transformations is Mor.arrow_set().two_mor(identity, identity)
        True
        sage: transformations is Mor.arrow_set().category_packet().Mors().Of(identity, identity)
        True
        sage: eta = transformations(lambda obj: category.Mor(obj, obj).identity())
        sage: (eta * eta).component(category("a")) == eta.component(category("a"))
        True
        sage: transformations.identity() * eta is eta
        True
        sage: eta * transformations.identity() is eta
        True
        sage: IdentityFunctor(Mor)(eta) is eta
        True
        sage: Mor.identity_2(cat.arrow(identity)).parent() is transformations
        True
        sage: arrows = cat.ArrowCategory()
        sage: obj = arrows(cat.arrow(identity))
        sage: square = arrows.Mor(obj, obj).identity()
        sage: square * square == square
        True
    """

    _MorCategory = NaturalTransformationMorCategoryConstruction
    Element = Functor

    @staticmethod
    def __classcall__(cls, category_of_categories: Cat, domain: Category, codomain: Category):
        r"""``[C, D]`` is built only by ``Cat``'s Mor family, which interns it.

        Naming a realization directly asks that family, so the walking-arrow
        realization is the same object as ``Cat().Mor([1], C)``.  A subclass
        that is a category of its own states its own classcall.
        """
        match cls:
            case DynamicMetaclass():
                return cls.__base__(category_of_categories, domain, codomain)
        return category_of_categories.MorCategory().Of(domain, codomain)

    def __init__(
        self,
        category_of_categories: Cat,
        domain: Category,
        codomain: Category,
    ) -> None:
        self._cat = category_of_categories
        self._domain_category = domain
        self._codomain_category = codomain
        CategoricalMor.__init__(
            self,
            category_of_categories.MorCategory(),
            category_of_categories.object(domain),
            category_of_categories.object(codomain),
        )

    def _make_named_class_key(self, name):
        return self._cat, self._domain_category, self._codomain_category

    def category_of_categories(self) -> Cat:
        return self._cat

    def domain_category(self) -> Category:
        return self._domain_category

    def codomain_category(self) -> Category:
        return self._codomain_category

    def arrow_set(self) -> _FunctorCategory:
        r"""The canonical Mor object of functors classified by ``[C,D]``."""
        return self

    underlying_mor = arrow_set

    def from_object_map(self, object_map):
        r"""Return the functor induced by an object-set map between discrete categories."""
        from sage_extensions.categories.abstract_categories.functors import (
            _DiscreteFunctor,
        )

        return _DiscreteFunctor(
            self.domain_category(),
            self.codomain_category(),
            object_map,
        )

    def discrete_diagram(self, values):
        r"""Return the diagram on a discrete domain with the selected object family."""
        from sage_extensions.categories.abstract_categories.functors import (
            _DiscreteDiagram,
        )

        return _DiscreteDiagram(
            self.domain_category(),
            self.codomain_category(),
            values,
        )

    def constant_functor(self, value):
        r"""Return the constant functor at ``value`` in this functor category."""
        from sage_extensions.categories.abstract_categories.functors import (
            _ConstantDiagram,
        )

        return _ConstantDiagram(
            self.domain_category(),
            self.codomain_category(),
            value,
        )

    @cached_method(key=lambda self, index: id(index))
    def evaluation(self, index):
        r"""Return evaluation at ``index``, the functor ``[C, D] -> D``, ``F |-> F(index)``."""
        return _EvaluationFunctor(self, index)

    def super_categories(self):
        return [Objects()]

    # Protected contract (OWN-05): isomorphisms of marked diagrams.
    #
    # Purpose: the core groupoid of ``[J, D]`` for ``J = FiniteOrdinalCategory(n)``
    # whose every arrow into the apex ``n-1`` is a monomorphism of ``D`` (a
    # marking: a sublattice, a flag).  A natural isomorphism ``F => G`` of such
    # diagrams is then determined by its apex component ``g: F(n-1) -> G(n-1)``:
    # the component over ``j`` is the unique ``alpha_j`` with
    # ``G(j -> n-1) alpha_j = g F(j -> n-1)``.  No public operation of ``D``
    # decides which apex isomorphisms carry one marking onto another, so ``D``
    # supplies that decision.
    # Owner: ``_FunctorCategory``, which builds the natural isomorphisms.
    # Caller: ``CoreMor`` (``is_empty``, ``an_element``, ``group_generators``,
    # ``an_element_in``) through ``_CoreCategory.base_category()``; and, for
    # ``D._marked_automorphism_generators`` only, ``LatticeIsometryMor``
    # (``split_orbit`` and ``vector_stabilizer_generators``), which needs the
    # apex image of ``Aut`` of a marking as a subgroup of ``O(L)``; no other.
    # Implementer: the codomain category ``D``, through
    #   ``D._marked_isometry(diagram_category, source, target)`` -> apex
    #   isomorphism ``F(n-1) -> G(n-1)`` of ``D``, or ``None`` when none exists;
    #   ``D._marked_automorphism_generators(diagram_category, marked)`` -> a set
    #   of apex automorphisms generating ``Aut`` of the marking;
    #   ``D._marking_component(source_marking, target_marking, apex)`` -> the
    #   component over a marking, as a morphism of ``D``.
    # All values are preamble objects.  A codomain category supplying no such
    # decision fails at the call.

    def _marking_shape(self):
        r"""``J = FiniteOrdinalCategory(n)`` and its apex ``n-1`` (protected contract above)."""
        from sage_extensions.categories.abstract_categories.products import FiniteOrdinalCategory

        shape = self.domain_category()
        size = int(shape.object_set().cardinality())
        assert size >= 1 and shape is FiniteOrdinalCategory(size), (
            f"an isomorphism of {self} is read off its apex component only for diagrams on a finite "
            f"ordinal [n] with n >= 1, but the shape is {shape}"
        )
        return shape, shape(size - 1)

    def _natural_transformation_from_apex(self, source, target, apex):
        r"""The natural transformation ``F => G`` with apex component ``apex`` (protected contract above)."""
        shape, top = self._marking_shape()
        first, second = source.functor(), target.functor()
        codomain = self.codomain_category()
        components = {
            obj.position(): (
                apex
                if obj is top
                else codomain._marking_component(
                    first(shape.Mor(obj, top).unique()),
                    second(shape.Mor(obj, top).unique()),
                    apex,
                )
            )
            for obj in shape.objects()
        }
        return NaturalTransformation(first, second, lambda obj: components[obj.position()])

    def _core_isomorphism_from_apex(self, core_mor, apex):
        r"""The isomorphism of ``core_mor`` whose apex component is ``apex`` (protected contract above)."""
        source, target = core_mor.domain(), core_mor.codomain()
        forward = self.Mor(source, target)(self._natural_transformation_from_apex(source, target, apex))
        inverse = self.Mor(target, source)(self._natural_transformation_from_apex(target, source, ~apex))
        return core_mor(forward, inverse)

    def _core_isomorphism_witness(self, core_mor):
        r"""One isomorphism of ``core_mor``, or ``None`` when the codomain decides there is none."""
        apex = self.codomain_category()._marked_isometry(self, core_mor.domain(), core_mor.codomain())
        return None if apex is None else self._core_isomorphism_from_apex(core_mor, apex)

    def _core_automorphism_generators(self, core_mor):
        r"""Automorphisms of the marked diagram generating its automorphism group."""
        from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

        assert core_mor.domain() is core_mor.codomain(), (
            f"group generators belong to Aut(X) = Iso(X, X), but {core_mor} has distinct endpoints"
        )
        apexes = self.codomain_category()._marked_automorphism_generators(self, core_mor.domain())
        return finite_ordered_set(tuple(self._core_isomorphism_from_apex(core_mor, apex) for apex in apexes))

    def _core_isomorphism_in(self, core_mor, subgroup):
        r"""An isomorphism of ``core_mor`` whose apex component lies in ``subgroup``, or ``None``.

        ``H = subgroup`` is a subgroup of ``G = Aut(A)``, ``A`` the common apex.
        The apex components of the isomorphisms form the coset ``w S``, with
        ``w`` one of them and ``S`` the apex image of the automorphisms of the
        source marking.  ``w s`` lies in ``H`` exactly when ``s^-1`` carries
        the point ``w^-1 H`` of ``G/H`` to the base point ``H``, so the search
        is a transporter in the finite ``S``-set ``G/H``.  The hypothesis is
        that ``G/H`` is realized as a finite ``G``-set (``H`` of finite index,
        realized as a kernel or preimage, or ``G`` finite).
        """
        if core_mor.is_empty():
            return None
        isomorphism = core_mor.an_element()
        _shape, top = self._marking_shape()
        witness = isomorphism.forward().component(top)
        apex = _apex_isomorphism_in_subgroup(
            witness,
            subgroup,
            self.codomain_category()._marked_automorphism_generators(self, core_mor.domain()),
        )
        return None if apex is None else self._core_isomorphism_from_apex(core_mor, apex)

    def __call__(self, functor: Functor):
        r"""Admit the actual functor with this Mor category's endpoints."""
        if not isinstance(functor, Functor) or not self._has_endpoints_of(functor):
            raise ValueError(
                f"{functor} is not an object of the functor category {self}: its domain or codomain is wrong"
            )
        return functor

    def _has_endpoints_of(self, functor: Functor) -> bool:
        r"""Whether ``functor`` has the exact categories selected by this packet.

        Equal-valued Mor parents may represent different endpoint objects.
        Such a comparison cannot identify functor domains or codomains:
        the category's identity-sensitive construction must retain both.
        """
        return (
            functor.domain() is self.domain_category()
            and functor.codomain() is self.codomain_category()
        )

    def _mor_endpoint(
        self,
        obj: Parent | Category | Functor,
    ):
        r"""An endpoint of a natural-transformation Mor: an object, or the functor it is built on."""
        match obj:
            case Functor():
                return self(obj)
            case _:
                return obj

    def __contains__(self, candidate: Any) -> bool:
        r"""A functor ``C -> D`` is itself an object of ``[C,D]``."""
        return isinstance(candidate, Functor) and self._has_endpoints_of(candidate)

    def Mor(
        self,
        domain: Parent | Functor,
        codomain: Parent | Functor,
    ) -> NaturalTransformationMor:
        domain = self._mor_endpoint(domain)
        codomain = self._mor_endpoint(codomain)
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in the functor category {self} needs two functors in it, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    two_mor = Mor

    def identity_2(self, arrow: Functor) -> NaturalTransformationMorphism:
        obj = self(arrow)
        return self.Mor(obj, obj).identity()

    @object_level
    @cached_method
    def identity(self):
        if self.domain_category() is not self.codomain_category():
            raise ValueError(f"an identity functor needs the same domain and codomain, but got {self}")
        return self(IdentityFunctor(self.domain_category()))

    def evaluation_functor(self, obj: Parent) -> _EvaluationFunctor:
        r"""``ev_c: [C, D] -> D``, evaluation at the object ``c`` of ``C``.

        Domain: this functor category ``[C, D]``.  Codomain: ``D``.  It sends
        a functor ``F`` to ``F(c)`` and a natural transformation ``eta`` to
        its component ``eta_c``; it is the evaluation bifunctor
        ``[C, D] x C -> D`` with ``c`` fixed (Mathlib,
        ``CategoryTheory.evaluation``, ``Mathlib/CategoryTheory/Products/Basic.lean``).
        """
        assert obj in self.domain_category(), (
            f"evaluation on {self} is at an object of {self.domain_category()}, but {obj} is in "
            f"{obj.category()}"
        )
        return _EvaluationFunctor(self, obj)

    def _repr_(self) -> str:
        return f"Functor category [{self.domain_category()}, {self.codomain_category()}]"


class _EvaluationFunctor(Functor):
    r"""``ev_c: [C, D] -> D``, ``F |-> F(c)`` and ``eta |-> eta_c``, for one object ``c`` of ``C``."""

    def __init__(self, functor_category: _FunctorCategory, obj: Parent) -> None:
        self._object = obj
        super().__init__(functor_category, functor_category.codomain_category())

    def evaluated_object(self) -> Parent:
        return self._object

    def _apply_object(self, functor_object: Parent) -> ObjectOfCategory:
        return functor_object.functor()(self.evaluated_object())

    def _apply_morphism(self, morphism: Map) -> Map:
        return morphism.component(self.evaluated_object())

    def _repr_(self) -> str:
        return f"Evaluation at {self.evaluated_object()} on {self.domain()}"


__all__ = [
    "Cat",
    "NaturalTransformationMor",
    "NaturalTransformationMorphism",
]
