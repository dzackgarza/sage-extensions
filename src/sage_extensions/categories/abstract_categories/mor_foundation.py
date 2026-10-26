"""Dependency-light runtime foundation for owned Mor object parents."""

from __future__ import annotations

from functools import update_wrapper
from typing import TYPE_CHECKING

from sage.categories.category import Category
from sage.categories.homset import Homset as SageHomset
from sage.categories.map import Map
from sage.categories.morphism import Morphism, SetMorphism
from sage.categories.sets_cat import Sets as SageSets
from sage.misc.cachefunc import cached_method
from sage.structure.element import Element
from sage.structure.parent import Parent

if TYPE_CHECKING:
    from sage_extensions.lexicon.category_theory import (
        ElementOfCategoryObject,
        ObjectOfCategory,
    )


class OwnedMor(SageHomset):
    r"""A Mor object whose elements enter through its owned constructor directly.

    Sage's ``Mor`` remains the runtime parent required by ``Morphism``.
    Mathematical inputs are not sent through Sage coercion discovery: each
    concrete Mor object owns the interpretation implemented by
    ``_element_constructor_``.
    """

    @cached_method
    def _selected_data_registry(self):
        r"""The chosen resolutions of this Mor object, by ambient category.

        A Mor object fixes such data before its category is set, so the
        ``Objects`` registry cannot reach it yet; this is the same registry
        at the Mor objects' own host root.
        """
        return {}

    # A Mor object fixes its chosen presentation, like its framing, before
    # its category is set; the presented-modules slot starts empty here too.
    _selected_module_presentation = None

    def _already_parented_arrow(self, arrow: Morphism) -> bool:
        return arrow.parent() is self

    def __call__(self, *args, **kwargs) -> Morphism:
        if len(args) == 1 and isinstance(args[0], (Map, CategoricalArrow)):
            arrow = args[0]
            if self._already_parented_arrow(arrow):
                if not kwargs:
                    return arrow
            elif arrow.domain() is self.domain() and arrow.codomain() is self.codomain():
                raise TypeError(
                    f"{arrow} belongs to {arrow.parent()}, not to {self}; apply the functor between "
                    "the categories instead of constructing an arrow from another arrow (CON-17)"
                )
        return self._element_constructor_(*args, **kwargs)

    def identity_at(self, obj: Parent) -> Morphism:
        if obj is not self.domain() or obj is not self.codomain():
            raise ValueError(
                f"the identity of {obj} is not in Mor({self.domain()}, {self.codomain()})"
            )
        return self.identity()


class CategoricalArrow:
    r"""An arrow with its actual categorical endpoints.

    Sage's ``Map`` stores endpoints as ``Parent`` instances. Objects of a
    category need not be parents: in particular an arrow is an object of a
    Mor category. This realization stores only the Mor parent and reads its
    endpoints without replacing them by auxiliary objects.
    """

    def __init__(self, parent: Parent) -> None:
        Element.__init__(self, parent)

    def domain(self):
        return self.parent().domain()

    def codomain(self):
        return self.parent().codomain()

    def Mor(self, codomain):
        return self.parent().two_mor(self, codomain)

    def __call__(self, value):
        return self._call_(value)

    def _repr_(self):
        return f"Morphism from {self.domain()} to {self.codomain()}"


def _refuse_foreign_arrow(mor: Parent, arrow: Morphism, functor: str) -> None:
    r"""Refuse ``arrow``, an arrow of another Mor, at the element constructor of ``mor``.

    ``CON-17``, owner ruling 2026-10-16: the element constructor of
    ``Mor_C(A, B)`` admits an arrow already in it and the defining data of a
    new arrow.  An arrow of a different Mor -- another category, or other
    structure on the same endpoints -- reaches it only as the image under a
    functor, never by reading its formula, matrix or callable to rebuild it:
    almost no arrow of a weaker category lifts, and admitting it unchecked is
    a backdoor to an ill-defined arrow.  ``functor`` names the route the
    caller takes instead.
    """
    raise TypeError(
        f"{arrow} is an arrow of {arrow.parent()}, not of {mor}: an element of {mor} is constructed from "
        f"its defining data (a function on elements, generator images, a matrix of a framed map), and an "
        f"arrow of another category reaches it only as the image under a functor (CON-17); {functor}"
    )


__all__ = [
    "CategoryPacketMethods",
    "ObjectLevelOperation",
    "OwnedMor",
    "UnderlyingSetMor",
    "object_level",
]

class UnderlyingSetMor(OwnedMor):
    r"""Plain-function Mor used only when an owned category declares no stronger arrows."""

    Element = SetMorphism

    def __init__(self, domain: Parent, codomain: Parent) -> None:
        SageHomset.__init__(self, domain, codomain, category=SageSets())

    def _element_constructor_(self, datum):
        if isinstance(datum, (Map, CategoricalArrow)):
            if datum.domain() is not self.domain() or datum.codomain() is not self.codomain():
                raise ValueError(
                    f"cannot view {datum} as a map {self.domain()} -> {self.codomain()}: it is a map "
                    f"{datum.domain()} -> {datum.codomain()}"
                )
            if datum.parent() is self:
                return datum
        if isinstance(datum, (Map, CategoricalArrow)):
            _refuse_foreign_arrow(
                self, datum, "the underlying map of an arrow of a structured category is its image under that "
                "category's forgetful functor to sets"
            )
        if not callable(datum):
            raise TypeError(
                f"a map {self.domain()} -> {self.codomain()} needs a function on points, but {datum!r} is not callable"
            )
        return self.element_class(self, datum)

    def identity(self) -> SetMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity map exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self.element_class(self, lambda element: element)


_underlying_set_mors = {}

def _underlying_set_mor(domain: Parent, codomain: Parent) -> UnderlyingSetMor:
    r"""Return the identity-cached plain-function Mor on these endpoints."""
    key = (id(domain), id(codomain))
    cached = _underlying_set_mors.get(key)
    if cached is not None and cached.domain() is domain and cached.codomain() is codomain:
        return cached
    result = UnderlyingSetMor(domain, codomain)
    _underlying_set_mors[key] = result
    return result


def _has_category_packet_surface(category: Category) -> bool:
    r"""Whether ``category``'s Mor construction is the owned packet or Sage's ``Hom``.

    ``OWN-06`` adapter.  Every category is an object of ``Cat``; what differs
    is the runtime that realizes its Mors.  The owned packet reaches a
    category in exactly two ways, both fixed by the runtime root: an owned
    category, and every join or axiom category Sage assembles from owned
    members, carries ``Cat.ParentMethods`` through its ``subcategory_class``
    (``CatConstructionsMixin`` in ``owned_category.py``); ``Cat`` itself and
    the Mor categories realized on Sage's ``Mor`` carry
    :class:`CategoryPacketMethods` as a declared base.  A category carrying
    neither is Sage's own and keeps Sage's ``Hom`` ingress.  This reads which
    of the two realizations is present and decides nothing else; it is not
    membership in ``Cat``, which a Sage-native category also has
    mathematically and a join of owned categories has without its placement
    being recorded.
    """
    from sage_extensions.categories.abstract_categories.cat import Cat

    match category:
        case CategoryPacketMethods() | Cat.ParentMethods():
            return True
        case _:
            return False


class _CategoryPacketOperations:
    r"""The coordinated ``C/Hom_C/End_C/Iso_C/Aut_C`` construction surface.

    Sited here, below the packet itself, so that the owned category bases can
    carry it: an axiom category is built from those bases, states no morphisms
    of its own, and must still be askable for the Mor of the category it
    refines.

    The packet assembles into two categories of its own: the arrow category
    ``Ar(C) = [[1], C]``, whose objects are all the arrows the Mor families
    classify, and the core, whose arrows are the isomorphisms the Iso family
    classifies.  Both are stated here once, so a Mor category realized on
    Sage's ``Mor`` reaches them by the same construction as every other
    category; ``Cat.ParentMethods`` names these same functions.
    """

    @property
    def ObjectType(self) -> type[ObjectOfCategory]:
        r"""The implementation type for objects of this category."""
        return self.parent_class

    @property
    def ElementType(self) -> type[ElementOfCategoryObject]:
        r"""The implementation type for elements of those objects."""
        return self.element_class

    def ArrowCategory(self) -> Category:
        r"""Return \(\mathrm{Ar}(C) = [[1], C]\), the functor category out of the walking arrow."""
        from sage_extensions.categories.abstract_categories.cat import Cat
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        return Cat().Mor(FiniteOrdinalCategory(2), self)

    def Core(self) -> Category:
        r"""Return the core of this category: its objects and its isomorphisms."""
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            _CoreCategory,
        )

        return _CoreCategory(self)

    def _mor_endpoint(
        self,
        obj: Parent | Category,
    ) -> ObjectOfCategory | Category:
        r"""Represent an endpoint in this category's Mor construction.

        Ordinary categories already receive their objects. ``Cat`` overrides
        this at its own boundary because Sage morphisms use parent objects
        representing categories as their endpoints.

        Protected construction protocol: Mor-family entries and categories
        with the same objects may delegate to this method. Such a category
        retains the base's endpoint representation, not its Mor family or
        its arrow admission. The method does not establish membership;
        the receiving Mor-family entry checks placement after normalization.
        """
        return obj

    def _mor_endpoints_in_supercategory(
        self,
        supercategory: Category,
        domain: Parent | Category,
        codomain: Parent | Category,
    ):
        r"""Forget this category's endpoints into one declared supercategory.

        The default inclusion keeps the mathematical objects and lets the
        supercategory apply its ordinary endpoint normalization.  A category
        whose declared supercategory is reached by a genuine forgetful functor
        overrides this one construction hook and returns the functor images.
        """
        return (
            supercategory._mor_endpoint(domain),
            supercategory._mor_endpoint(codomain),
        )

    def category_packet(self):
        r"""Return the Mor/End/Mono/Epi/Iso/Aut packet owned by this category."""
        from sage_extensions.categories.abstract_categories.mor_categories import (
            _category_packet,
        )

        return _category_packet(self)

    def MorCategory(self) -> Category:
        return self.category_packet().Mors()

    def EndCategory(self) -> Category:
        return self.category_packet().Ends()

    def MonoCategory(self) -> Category:
        return self.category_packet().Monos()

    def EpiCategory(self) -> Category:
        return self.category_packet().Epis()

    def IsoCategory(self) -> Category:
        return self.category_packet().Isos()

    def AutCategory(self) -> Category:
        return self.category_packet().Auts()

    def Mor(self, source: Parent, target: Parent) -> Category:
        return self.MorCategory().Of(source, target)

    def End(self, obj: Parent) -> Category:
        return self.EndCategory().Of(obj)

    def Mono(self, source: Parent, target: Parent) -> Category:
        return self.MonoCategory().Of(source, target)

    def Epi(self, source: Parent, target: Parent) -> Category:
        return self.EpiCategory().Of(source, target)

    def Iso(self, source: Parent, target: Parent) -> Category:
        return self.IsoCategory().Of(source, target)

    def Aut(self, obj: Parent) -> Category:
        return self.AutCategory().Of(obj)


def _identity_of_object(category: Category, obj: Parent) -> Morphism:
    r"""``C.identity(X)``: the identity arrow of the object ``X`` of ``C``, read in ``Mor_C(X, X)``."""
    return category.MorCategory().Of(obj, obj).identity()


def _asked_of_the_category(owner: Parent, objects: tuple) -> bool:
    r"""Whether a name of the Mor packet is asked of ``owner`` as a category.

    Owner ruling 2026-10-16 (``ARC-07``): an object that is also a category,
    such as a Mor category that is a monoid (``End(X)``) or a group
    (``O(L) = Aut(L)``), answers ``Mor``, ``End``, ``Aut``, ``Mono`` and
    ``identity`` in two readings.  Asked of it as an object, they are the
    operations of its nearest ambient category (``O(L).Mor(H)`` is the group
    homomorphisms).  Asked of it as a category, they take its own objects as
    arguments (``End(X).Mor(f, g)`` is the 2-arrows from ``f`` to ``g``).
    The reading is decided by what is asked: the category reading exactly
    when ``owner`` is a category and every argument is one of its objects.
    """
    from sage_extensions.categories.abstract_categories.cat import Cat

    match objects:
        case ():
            return False
        case _ if owner in Cat():
            return all(obj in owner for obj in objects)
        case _:
            return False


def _category_level_operations() -> dict:
    r"""The category-level operation of each name of the Mor packet, at its one owner."""
    packet = _CategoryPacketOperations.__dict__
    return {
        "Mor": packet["Mor"],
        "End": packet["End"],
        "Aut": packet["Aut"],
        "Mono": packet["Mono"],
        "Epi": packet["Epi"],
        "Iso": packet["Iso"],
        "identity": _identity_of_object,
    }


class ObjectLevelOperation:
    r"""The object-level reading of a name of the Mor packet (``ARC-07``).

    Declared at each owner of the object-level operation, as
    :class:`~sage_extensions.refine.RealizationHook` is declared at
    each hook.  A call is routed by what it asks of whom
    (:func:`_asked_of_the_category`): arguments that are objects of the
    receiver regarded as a category go to the category-level operation
    (:func:`_category_level_operations`); every other call is the declared
    object-level body.  The category's method classes precede a realization
    in the owned runtime (``refine._rebuild_parent_class``), so on an object
    that is also a category the object-level owner is the one Python finds;
    this descriptor is where both readings meet, without reordering that
    resolution and without a convention per class.

    A data descriptor: Sage's ``cached_method`` stores its caller on the
    instance by the method's name when it can, which would bypass the
    routing, and falls back to its private cache when that store is refused.
    """

    def __init__(self, reading) -> None:
        self._reading = reading
        update_wrapper(self, reading)
        self._category_reading = _category_level_operations()[self.__name__]
        self._category_arity = self._category_reading.__code__.co_argcount - 1

    def __get__(self, instance, owner=None):
        if instance is None:
            return self._reading.__get__(None, owner)
        reading = self._reading.__get__(instance, owner)
        category_level = self._category_reading

        def operation(*objects, **options):
            if not options and len(objects) == self._category_arity and _asked_of_the_category(instance, objects):
                return category_level(instance, *objects)
            return reading(*objects, **options)

        update_wrapper(operation, reading)
        return operation

    def __set__(self, instance, value) -> None:
        raise AttributeError(
            f"{self.__name__} is an operation of the Mor packet, not a field of {instance}"
        )


object_level = ObjectLevelOperation


class CategoryPacketMethods(_CategoryPacketOperations):
    r"""The category packet, with both readings on categories that are objects of Cat."""

    @object_level
    def Mor(self, codomain):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().functor_mor(self, codomain)

    @object_level
    def End(self):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().End(self)

    @object_level
    def Mono(self, codomain):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().Mono(self, codomain)

    @object_level
    def Epi(self, codomain):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().Epi(self, codomain)

    @object_level
    def Iso(self, codomain):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().Iso(self, codomain)

    @object_level
    def Aut(self):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().Aut(self)
