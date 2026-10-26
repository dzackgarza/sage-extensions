r"""The category of elements of a set-valued functor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage.categories.category import Category
from sage.categories.map import Map
from sage.misc.cachefunc import cached_method
from sage.structure.element import Element
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.lexicon.category_theory import ObjectOfCategory

if TYPE_CHECKING:
    from sage_extensions.owned_category import ConstructionData

type ElementLevel = dict[Category, tuple[ObjectOfCategory, Element]]


class _CategoryOfElements(OwnedCategory):
    r"""The category of elements ``int F`` of a functor ``F`` to ``Sets``.

    For a covariant ``F: C -> Sets`` an object is a pair ``(X, x)`` with ``X``
    an object of ``C`` and ``x`` an element of ``F(X)``; a morphism
    ``(X, x) -> (Y, y)`` is a morphism ``f: X -> Y`` of ``C`` with
    ``F(f)(x) = y``.  For a presheaf ``F: C^op -> Sets`` an object is again a
    pair ``(X, x)`` with ``x`` in ``F(X)``, and a morphism ``(X, x) -> (Y, y)``
    is ``f: X -> Y`` with ``F(f)(y) = x``.  Forgetting ``x`` is the projection
    functor ``int F -> C``, a discrete fibration (discrete opfibration in the
    covariant case); see Mac Lane, *Categories for the Working Mathematician*,
    II.6, and Riehl, *Category Theory in Context*, Definition 2.4.1.

    In the covariant case ``int F`` is the comma category ``(* | F)`` of the
    point ``* -> Sets`` and ``F``.  For a representable ``F = Mor(*, -)`` it is
    isomorphic to the coslice ``*/C``.  A functor ``F`` to groups or modules
    is read through the forgetful functor ``U`` to ``Sets``: ``int F`` means
    ``int (U F)``, whose objects are the pairs with ``x`` an element of the
    underlying set of ``F(X)``.

    ``base_category`` is the category ``C`` of the projection: the domain of
    ``F`` for a covariant functor, and the category whose opposite is the
    domain of ``F`` for a presheaf.
    """

    def __init__(self, functor: Functor, base_category: Category) -> None:
        assert functor.domain() is base_category or functor.domain() is base_category.opposite(), (
            f"the category of elements of {functor} projects to the domain C of F, or to C for a "
            f"presheaf F on C, but {base_category} is neither {functor.domain()} nor its opposite"
        )
        self._functor = functor
        self._base_category = base_category
        super().__init__()

    def _make_named_class_key(self, name):
        return self._functor

    def _repr_object_names(self) -> str:
        return f"elements of {self._functor}"

    def functor(self) -> Functor:
        r"""The functor ``F`` whose elements are the objects."""
        return self._functor

    def super_categories(self):
        r"""An object ``(X, x)`` of ``int F`` is an object ``X`` of ``C`` with the chosen element ``x`` of ``F(X)``.

        The projection ``int F -> C`` forgets ``x``; it is a functor, the
        image of this declaration, not a further entry (``CAT-16``,
        ``CAT-20``).  For a representable ``F`` this is the declaration of
        the coslice ``*/C``, whose objects are objects of ``C`` with a
        chosen arrow.
        """
        return [self._base_category]

    def functor_value(self, obj: ObjectOfCategory) -> Parent:
        r"""``F(X)`` for an object ``X`` of ``C``, read in ``C^op`` when ``F`` is a presheaf."""
        assert obj in self._base_category, (
            f"{obj} is not an object of {self._base_category}, so F = {self._functor} has no value at it"
        )
        domain = self._functor.domain()
        match domain:
            case _ if domain is self._base_category:
                return self._functor(obj)
            case _:
                return self._functor(domain(obj))

    def object(self, underlying_object: ObjectOfCategory, element: Element) -> ObjectOfCategory:
        r"""The pair ``(X, x)`` of an object ``X`` of ``C`` and an element ``x`` of ``F(X)``.

        The owner of ``X`` constructs it on the data of ``X`` (``OWN-16``):
        the result is an object of ``int F``, which adds only ``x``, and of
        ``C``, which ``int F`` declares.
        """
        return _object_of_elements(self, self, underlying_object, element)

    __call__ = object

    def underlying_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        r"""The object ``X`` of ``C`` of an object ``(X, x)`` of this ``int F``, its image under the projection."""
        assert obj in self, f"{obj} is not an object of {self}, so it has no pair (X, x) in it"
        return obj._functor_element_in(self)[0]

    def element(self, obj: ObjectOfCategory) -> Element:
        r"""The element ``x`` of ``F(X)`` of an object ``(X, x)`` of this ``int F``."""
        assert obj in self, f"{obj} is not an object of {self}, so it has no pair (X, x) in it"
        return obj._functor_element_in(self)[1]

    @cached_method
    def projection_functor(self) -> Functor:
        r"""The projection ``int F -> C``, ``(X, x) |-> X`` and ``f |-> f``."""
        return _CategoryOfElementsProjection(self, self._base_category)

    class ParentMethods:
        r"""An object ``X`` of ``C`` with its chosen element ``x`` of ``F(X)``."""

        def __init__(self, functor_elements: ElementLevel, **rest) -> None:
            self._functor_elements = functor_elements
            super().__init__(**rest)

        def underlying_object(self) -> ObjectOfCategory:
            r"""The object ``X`` of ``(X, x)``, when this object was constructed in one category of elements."""
            return self._chosen_pair()[0]

        def element(self) -> Element:
            r"""The element ``x`` of ``F(X)`` of ``(X, x)``, when this object was constructed in one category of elements."""
            return self._chosen_pair()[1]

        def _repr_(self) -> str:
            underlying_object, element = self._chosen_pair()
            return f"({underlying_object}, {element})"

        def _chosen_pair(self) -> tuple[ObjectOfCategory, Element]:
            match tuple(self._functor_elements.values()):
                case (pair,):
                    return pair
                case found:
                    assert False, (
                        f"{self} is an object of the categories of elements {tuple(self._functor_elements)}, "
                        f"with {len(found)} pairs (X, x), so it has no single one: ask the category, "
                        "category.element(obj)"
                    )

        def _functor_element_in(self, category: Category) -> tuple[ObjectOfCategory, Element]:
            r"""The pair ``(X, x)`` of this object as an object of the category of elements ``category``.

            Protected contract (``OWN-05``).  Owner: ``_CategoryOfElements``,
            whose level stores the pairs.  Callers: its dispatchers
            ``underlying_object`` and ``element``, after they have established
            that this object is an object of ``category``.  The pair is
            recorded with ``category`` or with a full subcategory of it cut
            out by a property of the element, such as an ample class in
            ``int Pic``.
            """
            match tuple(
                pair for level, pair in self._functor_elements.items() if level.is_subcategory(category)
            ):
                case (pair,):
                    return pair
                case found:
                    assert False, (
                        f"{self} is an object of {category}, but it has {len(found)} pairs (X, x) recorded in "
                        f"it or in a subcategory of it, not one: it was constructed in {tuple(self._functor_elements)}"
                    )

        def _added_structure(
            self,
            construction_data: dict[str, ConstructionData],
        ) -> tuple[tuple[Category, ...], dict[str, ConstructionData]]:
            r"""The categories of elements of this object and their pairs, with those in ``construction_data``.

            Kept when this object is constructed again (``OWN-05``; see
            ``Objects``).
            """
            further = dict(construction_data)
            pairs = {**self._functor_elements, **further.pop("functor_elements", {})}
            categories, data = super()._added_structure(further)
            return (*categories, *pairs), {**data, "functor_elements": pairs}


def _object_of_elements(
    category: Category,
    elements: _CategoryOfElements,
    underlying_object: ObjectOfCategory,
    element: Element,
) -> ObjectOfCategory:
    r"""The pair ``(X, x)`` as an object of ``category``, the category of elements ``elements`` or a full subcategory of it."""
    assert element in elements.functor_value(underlying_object), (
        f"cannot form the pair ({underlying_object}, {element}) in {category}: {element} is not an element "
        f"of {elements.functor()} at {underlying_object}"
    )
    return underlying_object._with_structure(
        (category,),
        {"functor_elements": {category: (underlying_object, element)}},
    )


class _CategoryOfElementsProjection(Functor):
    r"""The projection ``int F -> C`` of a category of elements, forgetting the element."""

    def __init__(self, elements: _CategoryOfElements, base_category: Category) -> None:
        self._elements = elements
        super().__init__(elements, base_category)

    def _apply_object(self, obj: ObjectOfCategory) -> ObjectOfCategory:
        return self._elements.underlying_object(obj)

    def _apply_morphism(self, morphism: Map) -> Map:
        r"""The arrow ``f: X -> Y`` of ``C`` underlying ``f: (X, x) -> (Y, y)`` in ``int F``."""
        assert False, "projection_functor on CategoryOfElements: morphism action not implemented"

    def _repr_(self) -> str:
        return "projection"
