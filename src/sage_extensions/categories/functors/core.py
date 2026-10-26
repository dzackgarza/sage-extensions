r"""Functors, natural transformations, and adjunctions.

These are deliberately small mathematical objects.  The existing Sage/owned
categories remain the domain and codomain; this module adds no parallel
category graph and no registry of relationships.

A functor ``F: C -> D`` is an object of the functor category ``[C, D]``, which
is ``Cat().Mor(C, D)``; a natural transformation ``F => G`` is an arrow of that
category; an adjunction ``F -| U`` is the pair of functors together with its
unit and counit.  ``Cat`` owns the functor category and its morphisms.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, final, overload

from sage.categories.category import Category
from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.lexicon.category_theory import ObjectOfCategory

if TYPE_CHECKING:
    from sage_extensions.logic import Predicate


@cached_function
def _structured_functor_realization(
    implementation: type,
    category: Category,
    engine: type | None,
) -> type:
    r"""Realize added category data on an already constructed functor."""
    from _abc import _abc_init

    from sage_extensions.owned_category import _abc_metaclass_for
    from sage_extensions.refine import owned_parent_class

    def finish(structured, *, _structured_category: Category, **remaining) -> None:
        assert not remaining, (
            f"the category levels added to {structured} did not consume "
            f"their construction data {sorted(remaining)}"
        )
        structured._structured_category = _structured_category

    boundary_bases = (implementation,)
    boundary = _abc_metaclass_for(boundary_bases)(
        f"{implementation.__name__}WithChosenStructureBoundary",
        boundary_bases,
        {
            "__init__": finish,
            "__module__": implementation.__module__,
            "__doc__": implementation.__doc__,
        },
    )
    _abc_init(boundary)
    if engine is None:
        staged = boundary
    else:
        bases = (engine, boundary)
        staged = _abc_metaclass_for(bases)(
            f"{implementation.__name__}WithChosenStructure",
            bases,
            {
                "__module__": implementation.__module__,
                "__doc__": implementation.__doc__,
            },
        )
        _abc_init(staged)
    return owned_parent_class(staged, category)


def _functor_factor_family(factors):
    r"""Return a finite ordinal-indexed family of composition factors without a foundational import cycle."""
    from sage_extensions.categories.sets.indexed_families import (
        finite_indexed_family,
    )
    from sage_extensions.categories.sets.set_categories import Sets

    factors = tuple(factors)
    positions = Sets.Δ[len(factors) - 1]
    return finite_indexed_family(
        positions,
        lambda index: factors[int(index)],
        name="Functor-composition factors",
    )


class Functor(CategoricalArrow):
    r"""A functor with explicit object and arrow actions.

    The functor itself is an arrow of ``Cat`` and an object of ``[C,D]``.

    Unverified specimen: a proposed identity on underlying sets is not a
    functor to the category of injections when applied to a noninjective map::

        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: injections = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
        sage: class ProposedInclusion(Functor):
        ....:     def __init__(self):
        ....:         super().__init__(Sets(), injections)
        ....:     def _apply_object(self, obj):
        ....:         return obj
        ....:     def _apply_morphism(self, arrow):
        ....:         return arrow
        sage: points = finite_ordered_set(("a", "b"))
        sage: maps = Sets().Mor(points, points)
        sage: swap = maps(lambda point: {"a": "b", "b": "a"}[point])
        sage: proposed = ProposedInclusion()
        sage: proposed(swap) is swap
        True
        sage: proposed(maps(lambda point: "a"))
        Traceback (most recent call last):
        ...
        TypeError: the image is not a morphism of the functor's codomain
    """

    _faithful: bool | None = None

    def __init__(self, domain: Category, codomain: Category) -> None:
        self._domain = domain
        self._codomain = codomain
        from sage_extensions.categories.abstract_categories.cat import Cat

        CategoricalArrow.__init__(self, Cat().functor_mor(domain, codomain))
        # Cache the forward action by source identity.  A codomain object does
        # not determine a preimage; chosen preimages belong to ImageOfFunctor.
        self._object_images: dict[int, tuple[ObjectOfCategory, ObjectOfCategory]] = {}
        self._morphism_images: dict[int, tuple[Map, Map]] = {}
        from sage_extensions.refine import owned_parent_class

        self.__class__ = owned_parent_class(type(self), self.functor_category())

    def _cache_key(self) -> int:
        r"""Functors have identity semantics as parameters of categorical constructions."""
        return id(self)

    def domain(self) -> Category:
        return self._domain

    def codomain(self) -> Category:
        return self._codomain

    def category(self):
        return getattr(self, "_structured_category", self.functor_category())

    def _with_structure(
        self,
        categories: tuple[Category, ...],
        construction_data: dict[str, object],
        *,
        engine: type | None = None,
    ) -> Functor:
        r"""Retain this actual functor while adding chosen category data."""
        from sage_extensions.owned_category import owned_category_join

        target = owned_category_join((*categories, self.functor_category()))
        implementation = _structured_functor_realization(type(self), target, engine)
        self.__class__ = implementation
        implementation.__init__(
            self,
            _structured_category=target,
            **construction_data,
        )
        return self

    @abstract_method
    def _apply_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        r"""Return the image of one object of the domain."""

    @abstract_method
    def _apply_morphism(self, morphism: Map) -> Map:
        r"""Return the image of one morphism of the domain."""

    def _cached_object_image(self, preimage: ObjectOfCategory) -> ObjectOfCategory | None:
        recorded = self._object_images.get(id(preimage))
        if recorded is not None and recorded[0] is preimage:
            return recorded[1]
        return None

    def _record_object_image(
        self,
        preimage: ObjectOfCategory,
        image: ObjectOfCategory,
    ) -> ObjectOfCategory:
        key = id(preimage)
        recorded = self._object_images.get(key)
        if recorded is not None and recorded[0] is preimage and recorded[1] is not image:
            raise ValueError(
                f"the functor {self} already sends {preimage} to {recorded[1]}, so it cannot also send it to {image}"
            )
        self._object_images[key] = (preimage, image)
        return image

    def _cached_morphism_image(self, preimage: Map) -> Map | None:
        recorded = self._morphism_images.get(id(preimage))
        if recorded is not None and recorded[0] is preimage:
            return recorded[1]
        return None

    def _record_morphism_image(self, preimage: Map, image: Map) -> Map:
        key = id(preimage)
        recorded = self._morphism_images.get(key)
        if recorded is not None and recorded[0] is preimage and recorded[1] is not image:
            raise ValueError(
                f"the functor {self} already sends {preimage} to {recorded[1]}, so it cannot also send it to {image}"
            )
        self._morphism_images[key] = (preimage, image)
        return image

    def object_image(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        if obj not in self.domain():
            raise TypeError(f"{obj} is not an object of {self.domain()}")
        cached = self._cached_object_image(obj)
        if cached is not None:
            return cached
        image = self._apply_object(obj)
        if image not in self.codomain():
            raise TypeError(
                f"the image of {obj} under {self} is not an object of {self.codomain()}"
            )
        return self._record_object_image(obj, image)

    @cached_method
    def Image(self):
        r"""Return the category of functor outputs with an explicit chosen preimage."""
        from sage_extensions.categories.abstract_categories.functor_images import (
            ImageOfFunctor,
        )

        return ImageOfFunctor(self)

    def adopt_object_image(
        self,
        preimage: ObjectOfCategory,
        image: ObjectOfCategory,
    ) -> ObjectOfCategory:
        r"""Use the stated exact object as this functor instance's forward image of ``preimage``."""
        if preimage not in self.domain() or image not in self.codomain():
            raise TypeError(
                f"cannot set F({preimage}) = {image} for F = {self}: F is a functor {self.domain()} -> "
                f"{self.codomain()}, and {preimage} or {image} is not in the right category"
            )
        return self._record_object_image(preimage, image)

    def on_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        return self.object_image(obj)

    def morphism_image(self, morphism: Map) -> Map:
        r"""The image ``F(f): F(A) -> F(B)`` of an arrow ``f: A -> B`` of the domain.

        Both sides are admitted by the Mor categories that own them: ``f``
        is an arrow of ``Hom_C(A, B)``, and its image is an arrow of
        ``Hom_D(F(A), F(B))``. This is admission of the actual maps, not
        placement of the objects constructed on them in those categories.
        """
        from sage_extensions.categories.abstract_categories.mor_categories import (
            _category_accepts_morphism,
        )

        if not _category_accepts_morphism(self.domain(), morphism.domain(), morphism.codomain(), morphism):
            raise TypeError(
                f"cannot apply {self} to {morphism}: it is not a morphism {morphism.domain()} -> "
                f"{morphism.codomain()} of {self.domain()}"
            )
        cached = self._cached_morphism_image(morphism)
        if cached is not None:
            return cached
        domain = self.object_image(morphism.domain())
        codomain = self.object_image(morphism.codomain())
        image = self._apply_morphism(morphism)
        if not _category_accepts_morphism(self.codomain(), domain, codomain, image):
            raise TypeError(
                f"the image of {morphism} under {self} is {image}, which is not a morphism {domain} -> "
                f"{codomain} of {self.codomain()}"
            )
        return self._record_morphism_image(morphism, image)

    def on_morphism(self, morphism: Map) -> Map:
        return self.morphism_image(morphism)

    def map_isomorphism(self, isomorphism):
        r"""The isomorphism F(f), with inverse F(f^{-1}) (Mathlib Functor.mapIso)."""
        from sage_extensions.categories.abstract_categories.arrow_categories import _core_mor
        from sage_extensions.categories.abstract_categories.mor_categories import _category_accepts_morphism

        assert _category_accepts_morphism(
            self.domain().Core(), isomorphism.domain(), isomorphism.codomain(), isomorphism
        ), f"{isomorphism} is not an isomorphism of {self.domain()}"
        target = _core_mor(
            self.object_image(isomorphism.domain()),
            self.object_image(isomorphism.codomain()),
            base_category=self.codomain(),
        )
        return target._from_inverse_computation(
            self.morphism_image(isomorphism.forward()),
            lambda: self.morphism_image(isomorphism.inverse().forward()),
        )

    @overload
    def __call__(self, value: ObjectOfCategory) -> ObjectOfCategory: ...

    @overload
    def __call__(self, value: Map) -> Map: ...

    def __call__(self, value: ObjectOfCategory | Map) -> ObjectOfCategory | Map:
        r"""Apply the object action to an object of the domain, the arrow action otherwise.

        Whether ``value`` is an object is the domain category's question.
        Asking it first is what lets a functor out of a Mor category, whose
        objects are themselves arrows, read an arrow as the object it is.
        """
        match value:
            case _ if value in self.domain():
                return self.object_image(value)
            case _:
                return self.morphism_image(value)

    def then(self, other: Functor) -> Functor:
        r"""Return ``other ∘ self``, retaining the nonidentity factor when possible.

        An identity functor is the composite of no factors, so a side with no
        factors is dropped.
        """
        if self.codomain() != other.domain():
            raise ValueError(
                f"cannot compose {other} after {self}: {self} ends at {self.codomain()}, but {other} starts at "
                f"{other.domain()}"
            )
        if self.factors().cardinality() == 0:
            return other
        if other.factors().cardinality() == 0:
            return self
        return _CompositeFunctor(self, other)

    def restrict(self, indexing_functor: Functor) -> Functor:
        r"""Return this diagram precomposed by ``indexing_functor``."""
        from sage_extensions.categories.abstract_categories.products import (
            RestrictedDiagram,
        )

        return RestrictedDiagram(self, indexing_functor)

    def Cones(self):
        r"""Return the category of cones over this diagram."""
        from sage_extensions.categories.abstract_categories.products import _ConeCategory

        return _ConeCategory(self)

    def Cocones(self):
        r"""Return the category of cocones under this diagram."""
        from sage_extensions.categories.abstract_categories.products import _CoconeCategory

        return _CoconeCategory(self)

    @cached_method
    def category_of_elements(self):
        r"""Return the category of elements ``int F`` of this functor to ``Sets``.

        Its objects are the pairs ``(X, x)`` with ``x`` an element of ``F(X)``,
        and a morphism ``(X, x) -> (Y, y)`` is ``f: X -> Y`` with
        ``F(f)(x) = y`` (Mac Lane, *Categories for the Working
        Mathematician*, II.6).  This reads ``F`` covariantly on its domain; a
        presheaf on ``C`` returns its category of elements over ``C``, whose
        morphisms are the ``f`` with ``F(f)(y) = x``.
        """
        from sage_extensions.categories.abstract_categories.categories_of_elements import (
            _CategoryOfElements,
        )

        return _CategoryOfElements(self, self.domain())

    @cached_method
    def algebras(self):
        r"""Return the category of algebras ``T(X) -> X`` of this endofunctor."""
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            _EndofunctorAlgebraCategory,
        )

        return _EndofunctorAlgebraCategory(self)

    def ProductCones(self):
        r"""Return the category of product cones over this discrete diagram."""
        from sage_extensions.categories.abstract_categories.products import (
            _ProductConeCategory,
        )

        return _ProductConeCategory(self)

    def CoproductCocones(self):
        r"""Return the category of coproduct cocones under this discrete diagram."""
        from sage_extensions.categories.abstract_categories.products import (
            _CoproductCoconeCategory,
        )

        return _CoproductCoconeCategory(self)

    def Spans(self):
        r"""Return the span category carried by this discrete diagram."""
        from sage_extensions.categories.abstract_categories.products import _SpanCategory

        return _SpanCategory(self)

    def functor_category(self):
        r"""Return the represented functor category containing this functor."""
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().functor_mor(self.domain(), self.codomain())

    def object(self):
        return self

    def functor(self):
        return self

    def Mor(self, target):
        return self.natural_transformations_to(target)

    def arrow(self):
        r"""Return this same functor as the corresponding morphism in ``Cat``."""
        return self

    def __mul__(self, other):
        if not isinstance(other, Functor) or other.codomain() is not self.domain():
            return NotImplemented
        return other.then(self)

    def natural_transformations_to(self, target: Functor):
        r"""Return the Mor of natural transformations ``self ⇒ target``."""
        if self.domain() != target.domain() or self.codomain() != target.codomain():
            raise ValueError(
                f"natural transformations {self} => {target} need parallel functors, but {self} is "
                f"{self.domain()} -> {self.codomain()} and {target} is {target.domain()} -> {target.codomain()}"
            )
        category = self.functor_category()
        return category.Mor(self, target)

    def natural_isomorphism_to(
        self,
        target: Functor,
        components: Callable[[Parent], Morphism],
        inverse_components: Callable[[Parent], Morphism],
    ):
        r"""Return the selected natural isomorphism ``self ≅ target``."""
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            _isomorphism_from_known_inverse_pair,
        )

        forward = self.natural_transformations_to(target)(components)
        inverse = target.natural_transformations_to(self)(inverse_components)
        return _isomorphism_from_known_inverse_pair(forward, inverse)

    def induced_mor_functor(
        self, domain_object: Parent, codomain_object: Parent, *,
        on_two_morphism: Callable[[Morphism], Morphism] | None = None,
    ):
        r"""Lift this functor to one Mor category with the specified 2-arrow action.

        A discrete source Mor forces that action. On a non-discrete Mor,
        supply the local action on 2-arrows, preserving identities and vertical
        composition; the identity functor has its canonical identity lift.
        This datum does not assert a globally coherent 2-functor structure.
        """
        from sage_extensions.categories.functors.mor_packets import _InducedMorFunctor

        return _InducedMorFunctor(
            self, domain_object, codomain_object, on_two_morphism=on_two_morphism,
        )

    def induced_end_functor(
        self, obj: Parent, *,
        on_two_morphism: Callable[[Morphism], Morphism] | None = None,
    ):
        r"""Lift to ``End(obj)`` with the same 2-arrow datum as ``induced_mor_functor``."""
        from sage_extensions.categories.functors.mor_packets import _InducedEndFunctor

        return _InducedEndFunctor(self, obj, on_two_morphism=on_two_morphism)

    def induced_aut_functor(
        self, obj: Parent, *,
        on_two_morphism: Callable[[Morphism], Morphism] | None = None,
    ):
        r"""Lift to ``Aut(obj)`` with the same 2-arrow datum as ``induced_mor_functor``."""
        from sage_extensions.categories.functors.mor_packets import _InducedAutFunctor

        return _InducedAutFunctor(self, obj, on_two_morphism=on_two_morphism)

    def factors(self):
        return _functor_factor_family((self,))

    def is_faithful(self) -> bool | Predicate:
        r"""Return the declared faithfulness decision.

        A functor class that declares none answers the proposition that the
        functor is faithful.
        """
        if self._faithful is None:
            from sage_extensions.logic import AtomicProposition

            return AtomicProposition("is_faithful", self)
        return self._faithful

    def _repr_(self) -> str:
        r"""The functor's standard name; a functor with none is named only by its endpoints."""
        return "Functor"

    def __repr__(self) -> str:
        r"""Display the mathematical arrow together with any standard operation name."""
        label = self._repr_()
        endpoints = f"{self.domain()} -> {self.codomain()}"
        return label if endpoints in label else f"{label}: {endpoints}"


class IdentityFunctor(Functor):
    def __init__(self, category: Category) -> None:
        super().__init__(category, category)

    def _apply_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        return obj

    def _apply_morphism(self, morphism: Map) -> Map:
        return morphism

    def factors(self):
        return _functor_factor_family(())

    def is_faithful(self) -> bool:
        return True

    def _repr_(self):
        return f"Identity functor of {self.domain()}"


class _CategoryInclusionFunctor(Functor):
    r"""The canonical functor along a declared subcategory inclusion.

    If ``C`` is a subcategory of ``D``, every object and morphism of ``C`` is
    already an object and morphism of ``D``.  The functor therefore changes
    only the category in which the same mathematical data is read.
    """

    _faithful = True

    def __init__(self, subcategory: Category, supercategory: Category) -> None:
        if not subcategory.is_subcategory(supercategory):
            raise ValueError(f"{subcategory} is not a subcategory of {supercategory}")
        super().__init__(subcategory, supercategory)

    def _apply_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        return obj

    def _apply_morphism(self, morphism: Map) -> Map:
        return morphism

    def _repr_(self):
        return f"Inclusion {self.domain()} -> {self.codomain()}"



class _CompositeFunctor(Functor):
    r"""The composite ``second ∘ first`` with the ordinary cached forward action."""

    def __init__(self, first: Functor, second: Functor) -> None:
        if first.codomain() != second.domain():
            raise ValueError(
                f"cannot compose {second} after {first}: {first} ends at {first.codomain()}, but {second} starts "
                f"at {second.domain()}"
            )
        self._first = first
        self._second = second
        super().__init__(first.domain(), second.codomain())

    def _apply_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        return self._second(self._first(obj))

    def _apply_morphism(self, morphism: Map) -> Map:
        return self._second(self._first(morphism))

    def adopt_object_image(
        self,
        preimage: ObjectOfCategory,
        image: ObjectOfCategory,
    ) -> ObjectOfCategory:
        if preimage not in self.domain() or image not in self.codomain():
            raise TypeError(
                f"cannot set F({preimage}) = {image} for the composite F = {self}: F is a functor "
                f"{self.domain()} -> {self.codomain()}, and {preimage} or {image} is not in the right category"
            )
        chosen = self._cached_object_image(preimage)
        if chosen is not None:
            if chosen is not image:
                raise ValueError(
                    f"the composite functor {self} already sends {preimage} to {chosen}, so it cannot also send it "
                    f"to {image}"
                )
            return chosen
        middle = self._first(preimage)
        target = self._second(middle)
        if target is not image:
            raise ValueError(
                f"the composite functor {self} sends {preimage} to {target}, not to {image}"
            )
        return super().adopt_object_image(preimage, image)

    def factors(self):
        factors = tuple(self._first.factors()) + tuple(self._second.factors())
        return _functor_factor_family(factors)

    def is_faithful(self) -> bool | Predicate:
        r"""Return what the factors' declarations prove about faithfulness of the composite."""
        first = self._first.is_faithful()
        second = self._second.is_faithful()
        if first is False:
            # Equal arrows already identified by the first factor remain
            # identified after applying the second factor.
            return False
        if first is True and second is True:
            return True
        # Nonfaithfulness of the second factor need not occur on the image of
        # the first, and an undeclared factor supplies no missing theorem.
        from sage_extensions.logic import AtomicProposition

        return AtomicProposition("is_faithful", self)

    def _repr_(self):
        return f"{self._second} ∘ {self._first}"


class NaturalTransformation:
    r"""Construction data for a natural transformation ``source => target``.

    The datum is the family of components ``eta_X: F(X) -> G(X)`` indexed by
    the objects of the common domain.  Naturality is the equation
    ``G(f) eta_A = eta_B F(f)`` for every ``f: A -> B``; it is a property of
    the family that its constructor states, not a check performed per arrow.
    """

    def __init__(
        self,
        source: Functor,
        target: Functor,
        component: Callable[[Parent], Morphism],
    ) -> None:
        if source.domain() != target.domain() or source.codomain() != target.codomain():
            raise ValueError(
                f"a natural transformation {source} => {target} needs parallel functors, but {source} is "
                f"{source.domain()} -> {source.codomain()} and {target} is {target.domain()} -> {target.codomain()}"
            )
        if not callable(component):
            raise TypeError(
                f"a natural transformation {source} => {target} needs a component at each object, but "
                f"{component!r} is not callable"
            )
        self._source = source
        self._target = target
        self._component = component

    def source(self) -> Functor:
        return self._source

    def target(self) -> Functor:
        return self._target

    @cached_method(key=lambda self, obj: id(obj))
    def component(self, obj: Parent) -> Morphism:
        r"""The component ``eta_X``, an arrow of ``Hom_D(F(X), G(X))``.

        That Mor owner's admission decides both that the component is an
        arrow of the common codomain category and that its endpoints are
        ``F(X)`` and ``G(X)``. The raw component need not itself be an object
        placed in the fixed Mor category.
        """
        from sage_extensions.categories.abstract_categories.mor_categories import (
            _category_accepts_morphism,
        )

        domain, codomain = self.source()(obj), self.target()(obj)
        arrow = self._component(obj)
        if not _category_accepts_morphism(self.source().codomain(), domain, codomain, arrow):
            raise TypeError(
                f"the component of {self} at {obj} must be a morphism {domain} -> {codomain} of "
                f"{self.source().codomain()}, but it is {arrow}"
            )
        return arrow

    def __call__(self, *args, **kwargs):
        return self.component(*args, **kwargs)

    def naturality_target_composite(self, morphism: Map) -> Morphism:
        r"""Return ``G(f) o eta_A`` for this transformation ``eta:F=>G``."""
        return self.target()(morphism) * self.component(morphism.domain())

    def naturality_source_composite(self, morphism: Map) -> Morphism:
        r"""Return ``eta_B o F(f)`` for this transformation ``eta:F=>G``."""
        return self.component(morphism.codomain()) * self.source()(morphism)

    def naturality_square(self, morphism: Map):
        r"""Return the two paths of the naturality square at ``f: A -> B``.

        The square has two paths ``F(A) -> G(B)``, indexed by the two-element
        set ``Sets.Δ[1]``: ``0`` is ``G(f) o eta_A`` and ``1`` is
        ``eta_B o F(f)``.  Its value is one element of the product of the
        family of the Mor objects holding those two composites over that index
        set (`CON-15`); projecting at an index recovers that path in its own
        Mor object.  Naturality is the statement that the two components agree.
        """
        from sage_extensions.categories.sets.indexed_families import indexed_family
        from sage_extensions.categories.sets.set_categories import Sets

        paths = Sets.Δ[1]
        target_composite = self.naturality_target_composite(morphism)
        source_composite = self.naturality_source_composite(morphism)

        def path(index):
            return target_composite if int(index) == 0 else source_composite

        product = Sets().product(indexed_family(paths, lambda index: path(index).parent()))
        return product(path)

    def _repr_(self) -> str:
        return f"{self.source()} => {self.target()}"

    def __repr__(self) -> str:
        return self._repr_()

    def morphism(self):
        r"""Return this datum as the arrow ``F => G`` of the functor category."""
        return self.source().functor_category().Mor(self.source(), self.target())(self)


class _UnitCounitPresentation:
    r"""One fixed unit-counit presentation of an adjunction.

    This is the complete defining datum consumed by :class:`Adjunction`: the
    two adjoint functors and the two component families.  It validates the
    actual component endpoints once at their shared owner.  Mor transposes,
    natural transformations and the public component accessors are derived
    from this presentation rather than supplied as parallel interfaces.
    """

    def __init__(
        self,
        left_adjoint: Functor,
        right_adjoint: Functor,
        unit_component: Callable[[Parent], Morphism],
        counit_component: Callable[[Parent], Morphism],
    ) -> None:
        match (
            left_adjoint.domain() == right_adjoint.codomain(),
            left_adjoint.codomain() == right_adjoint.domain(),
        ):
            case (True, True):
                pass
            case (False, _):
                raise ValueError(
                    f"an adjunction F -| G needs G to end where F starts, but F = {left_adjoint} starts at "
                    f"{left_adjoint.domain()} and G = {right_adjoint} ends at {right_adjoint.codomain()}"
                )
            case (_, False):
                raise ValueError(
                    f"an adjunction F -| G needs G to start where F ends, but F = {left_adjoint} ends at "
                    f"{left_adjoint.codomain()} and G = {right_adjoint} starts at {right_adjoint.domain()}"
                )
        self._left_adjoint = left_adjoint
        self._right_adjoint = right_adjoint
        self._unit_component = unit_component
        self._counit_component = counit_component

    def left_adjoint(self) -> Functor:
        return self._left_adjoint

    def right_adjoint(self) -> Functor:
        return self._right_adjoint

    def unit(self, obj: Parent) -> Morphism:
        from sage_extensions.categories.abstract_categories.mor_categories import (
            _category_accepts_morphism,
        )

        category = self.left_adjoint().domain()
        match obj in category:
            case True:
                pass
            case False:
                raise TypeError(
                    f"the unit X -> GF(X) of {self} is defined at objects of {category}, but {obj} is not one"
                )
        target = self.right_adjoint()(self.left_adjoint()(obj))
        arrow = self._unit_component(obj)
        match _category_accepts_morphism(category, obj, target, arrow):
            case True:
                pass
            case False:
                raise TypeError(
                    f"the unit of {self} at {obj} must be a morphism {obj} -> {target} of {category}, but it is {arrow}"
                )
        return arrow

    def counit(self, obj: Parent) -> Morphism:
        from sage_extensions.categories.abstract_categories.mor_categories import (
            _category_accepts_morphism,
        )

        category = self.right_adjoint().domain()
        match obj in category:
            case True:
                pass
            case False:
                raise TypeError(
                    f"the counit FG(Y) -> Y of {self} is defined at objects of {category}, but {obj} is not one"
                )
        source = self.left_adjoint()(self.right_adjoint()(obj))
        arrow = self._counit_component(obj)
        match _category_accepts_morphism(category, source, obj, arrow):
            case True:
                pass
            case False:
                raise TypeError(
                    f"the counit of {self} at {obj} must be a morphism {source} -> {obj} of {category}, but it is {arrow}"
                )
        return arrow


class Adjunction:
    r"""Construction/proof data for an adjunction ``F ⊣ U``.

    Unlike a functor or a natural transformation, the current category tree
    has no category whose objects are adjunction presentations.  This retained
    record therefore does not pretend to be a Sage mathematical object: its
    constituent functors and its unit/counit are placed at their actual owners.

    The defining datum is the unit-counit presentation (Mathlib,
    ``CategoryTheory.Adjunction.CoreUnitCounit``): functors
    ``F: C -> D`` and ``U: D -> C`` with natural transformations
    ``eta: 1_C => UF`` and ``epsilon: FU => 1_D`` satisfying the triangle
    identities ``U(epsilon) o eta_U = 1_U`` and ``epsilon_F o F(eta) = 1_F``.
    A subclass supplies exactly this datum through the private component
    formulas :meth:`_unit_component` and :meth:`_counit_component`.  Construction
    fixes those formulas in one :class:`_UnitCounitPresentation`; subclasses
    cannot replace any of the public equivalent-data interfaces independently.

    Everything else is derived from it and is not supplied again: the natural
    Mor object bijection ``Phi: Hom_D(F(A), B) -> Hom_C(A, U(B))``, with
    ``Phi(f) = U(f) o eta_A`` and ``Phi^{-1}(g) = epsilon_B o F(g)``, and the
    unit and counit as natural transformations.  The triangle identities are
    theorems about the supplied datum, established where it is constructed,
    not re-checked here.
    """

    _DERIVED_PUBLIC_INTERFACES = frozenset((
        "unit",
        "counit",
        "mor_set_isomorphism_forward",
        "mor_set_isomorphism_inverse",
        "unit_transformation",
        "counit_transformation",
    ))

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        independently_supplied = cls._DERIVED_PUBLIC_INTERFACES.intersection(cls.__dict__)
        match len(independently_supplied):
            case 0:
                pass
            case _:
                names = ", ".join(sorted(independently_supplied))
                raise TypeError(
                    f"the adjunction {cls.__name__} defines {names}, but an adjunction is given "
                    "only by its unit and counit components; the unit, counit and hom-set "
                    "bijections are derived from them"
                )

    def __init__(self, left_adjoint: Functor, right_adjoint: Functor) -> None:
        self._presentation = _UnitCounitPresentation(
            left_adjoint,
            right_adjoint,
            self._unit_component,
            self._counit_component,
        )

    def _unit_counit_presentation(self) -> _UnitCounitPresentation:
        r"""Return this adjunction's one selected complete defining datum."""
        return self._presentation

    def left_adjoint(self) -> Functor:
        return self._unit_counit_presentation().left_adjoint()

    def right_adjoint(self) -> Functor:
        return self._unit_counit_presentation().right_adjoint()

    def then(self, second: "Adjunction") -> "Adjunction":
        r"""Compose this adjunction with ``second``."""
        return _CompositeAdjunction(self, second)

    def _repr_(self) -> str:
        r"""The adjunction's standard name; one with none is named only by its categories."""
        return "Adjunction"

    def __repr__(self) -> str:
        label = self._repr_()
        left = self.left_adjoint()
        endpoints = f"{left.domain()} <-> {left.codomain()}"
        return label if endpoints in label else f"{label}: {endpoints}"

    @abstract_method
    def _unit_component(self, obj: Parent) -> Morphism:
        r"""Construct the selected unit component before shared endpoint admission."""

    @abstract_method
    def _counit_component(self, obj: Parent) -> Morphism:
        r"""Construct the selected counit component before shared endpoint admission."""

    @final
    def unit(self, obj: Parent) -> Morphism:
        r"""Return the unit component ``eta_A: A -> U(F(A))`` from the selected presentation."""
        return self._unit_counit_presentation().unit(obj)

    @final
    def counit(self, obj: Parent) -> Morphism:
        r"""Return the counit component ``epsilon_B: F(U(B)) -> B`` from the selected presentation."""
        return self._unit_counit_presentation().counit(obj)

    @final
    def mor_set_isomorphism_forward(
        self,
        morphism: Morphism,
        source: Parent,
    ) -> Morphism:
        r"""Transpose ``f:F(A)->B`` to ``U(f) after eta_A`` for the stated ``A``.

        Derived from the unit; a subclass never supplies it.  ``A`` is stated
        because a left-adjoint image ``F(A)`` need not determine ``A``.
        """
        if source not in self.left_adjoint().domain():
            raise TypeError(
                f"the bijection Mor(F(A), B) = Mor(A, G(B)) of {self} needs A in {self.left_adjoint().domain()}, "
                f"but {source} is not in it"
            )
        if self.left_adjoint()(source) is not morphism.domain():
            raise ValueError(
                f"the bijection Mor(F(A), B) = Mor(A, G(B)) of {self} needs a morphism starting at "
                f"F(A) = {self.left_adjoint()(source)}, but {morphism} starts at {morphism.domain()}"
            )
        return self.right_adjoint()(morphism) * self.unit(source)

    @final
    def mor_set_isomorphism_inverse(
        self,
        morphism: Morphism,
        codomain: Parent,
    ) -> Morphism:
        r"""Transpose ``g:A->U(B)`` to ``epsilon_B after F(g)`` for the stated ``B``.

        Derived from the counit; a subclass never supplies it.
        """
        if codomain not in self.right_adjoint().domain():
            raise TypeError(
                f"the bijection Mor(A, G(B)) = Mor(F(A), B) of {self} needs B in {self.right_adjoint().domain()}, "
                f"but {codomain} is not in it"
            )
        if self.right_adjoint()(codomain) is not morphism.codomain():
            raise ValueError(
                f"the bijection Mor(A, G(B)) = Mor(F(A), B) of {self} needs a morphism ending at "
                f"G(B) = {self.right_adjoint()(codomain)}, but {morphism} ends at {morphism.codomain()}"
            )
        return self.counit(codomain) * self.left_adjoint()(morphism)

    @final
    def unit_transformation(self):
        r"""The unit ``eta: 1_C => UF`` as a natural transformation, from :meth:`unit`."""
        return NaturalTransformation(
            IdentityFunctor(self.left_adjoint().domain()),
            _CompositeFunctor(self.left_adjoint(), self.right_adjoint()),
            self.unit,
        ).morphism()

    @final
    def counit_transformation(self):
        r"""The counit ``epsilon: FU => 1_D`` as a natural transformation, from :meth:`counit`."""
        return NaturalTransformation(
            _CompositeFunctor(self.right_adjoint(), self.left_adjoint()),
            IdentityFunctor(self.left_adjoint().codomain()),
            self.counit,
        ).morphism()


class _CompositeAdjunction(Adjunction):
    r"""The composite of ``F ⊣ U`` and ``G ⊣ V`` as ``GF ⊣ UV``.

    Its unit and counit are the standard composites (Mathlib,
    ``Adjunction.comp_unit_app`` and ``comp_counit_app``): ``eta = U(eta') o eta`` and ``epsilon = epsilon' o G(epsilon)``.
    """

    def __init__(self, first: Adjunction, second: Adjunction) -> None:
        if first.left_adjoint().codomain() != second.left_adjoint().domain():
            raise ValueError(
                f"cannot compose the adjunctions {first} and {second}: the left adjoint of the first ends at "
                f"{first.left_adjoint().codomain()}, but that of the second starts at {second.left_adjoint().domain()}"
            )
        self._first = first
        self._second = second
        super().__init__(
            _CompositeFunctor(first.left_adjoint(), second.left_adjoint()),
            _CompositeFunctor(second.right_adjoint(), first.right_adjoint()),
        )

    def first(self) -> Adjunction:
        return self._first

    def second(self) -> Adjunction:
        return self._second

    def _unit_component(self, obj: Parent) -> Morphism:
        first_unit = self.first().unit(obj)
        second_unit = self.second().unit(self.first().left_adjoint()(obj))
        return self.first().right_adjoint()(second_unit) * first_unit

    def _counit_component(self, obj: Parent) -> Morphism:
        first_counit = self.first().counit(self.second().right_adjoint()(obj))
        return self.second().counit(obj) * self.second().left_adjoint()(first_counit)
