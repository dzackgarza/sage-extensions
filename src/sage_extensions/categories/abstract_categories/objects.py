"""Dependency-light bases for the owned mathematical category graph."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sage.categories.category import Category
from sage.categories.map import Map
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.structure.element import Element
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
# The marker every owned category base carries, axiom categories included.
# Re-exported so the Mor packet can recognize one without reaching past this
# module into the bases it is built from.
from sage_extensions.owned_category import (  # noqa: F401
    OwnedCategoryMixin,
    OwnedParent,
    _object_of,
    owned_category_join,
)
from sage_extensions.owned_category_bases import (
    Category as OwnedCategoryBase,
    CategoryWithAxiom,
)
from sage_extensions.lexicon.category_theory import ObjectOfCategory

if TYPE_CHECKING:
    from sage_extensions.owned_category import ConstructionData

# The private realization of an object: its owner category, its object class
# and its element class, as ``_object_of`` receives it (``OWN-06``).
type Realization = tuple[Category, type, type | None]


def _realization_with_caller_engine(
    target: Category,
    received_type: type,
    received_element_type: type,
    engine: type | None,
) -> Realization:
    r"""The computation of an object constructed again in ``target``.

    Engine adapter (``OWN-06``) of ``Objects.ParentMethods._with_structure``,
    and called by nothing else.  ``received_type`` and
    ``received_element_type`` realize the received object and its elements;
    they consume its defining data and compute on it, and they serve
    ``target``, which places the result.  ``engine`` is the class of the
    caller's added level, and it precedes the received realization.  The
    inputs and the result are engine classes, which no public operation
    exchanges, so this stays inside the construction contract.
    """
    from sage.structure.dynamic_class import dynamic_class

    root = Objects()
    # A newly constructed subobject takes its operations from its selected
    # category; its received representation supplies computation beneath those
    # methods, rather than overriding them. Not every Sage-backed target has
    # the owned root among its declared ancestors.
    owner = root if root in target._set_of_super_categories else target
    match engine:
        case None:
            return (owner, received_type, received_element_type)
        case _:
            return (
                owner,
                dynamic_class(engine.__name__, (engine, received_type)),
                received_element_type,
            )


class _PendingResolution:
    r"""A lazily realized chosen resolution fixed during target construction.

    A target can receive its resolution datum before its parent chain has
    finished constructing. The registry therefore holds this zero-argument
    construction until the first read; after realization the actual resolution
    object replaces it. The mathematical datum stored by the target is the
    object of the resolution category, not a second framing record.
    """

    def __init__(self, resolution_factory, generating_set=None, generator_function=None) -> None:
        match callable(resolution_factory):
            case True:
                pass
            case False:
                raise TypeError(
                    f"a selected resolution must be supplied by a zero-argument construction, "
                    f"but {resolution_factory!r} is not callable"
                )
        self._resolution_factory = resolution_factory
        self._generating_set = generating_set
        self._generator_function = generator_function

    def generating_set(self):
        r"""The set ``S`` of the degree-zero free object ``F(S)``, when the registration states it.

        ``S`` is defining data of the resolution, known when it is fixed, so
        reading it does not realize the resolution: realizing builds the
        augmentation ``F(S) ->> X``, whose Mor object reads ``S``.
        """
        return self._generating_set

    def generator(self, label):
        r"""Return the registered degree-zero generator without realizing the resolution."""
        if self._generator_function is None:
            raise ValueError("this pending resolution did not register its generator function")
        return self._generator_function(label)

    def has_generator_function(self) -> bool:
        return self._generator_function is not None

    def realize(self):
        return self._resolution_factory()


def _fix_selected_resolution(
    target,
    owner,
    resolution_factory,
    *,
    replace=False,
    generating_set=None,
    generator_function=None,
):
    r"""Fix one chosen resolution of target relative to owner."""
    selected_by_owner = target._selected_data_registry()
    match owner in selected_by_owner, replace:
        case (True, False):
            raise ValueError(
                f"{target} already has a chosen resolution relative to {owner}; "
                "it cannot be given a second one"
            )
        case _:
            pass
    selected_by_owner[owner] = _PendingResolution(
        resolution_factory,
        generating_set,
        generator_function,
    )


class OwnedCategory(OwnedCategoryBase):
    r"""Base class for categories belonging to the owned mathematical graph.

    Over :class:`owned_category_bases.Category`, which ties this category's
    ``ParentMethods`` / ``ElementMethods`` / ``MorphismMethods`` into the
    named classes as real bases.  Sage's own builder passes
    ``prepend_cls_bases=False``, so only a copy of the container's
    ``__dict__`` reaches the MRO -- a copy carries no bases, so it cannot
    carry ``Parent``, so it cannot carry fields or a constructor.  That, and
    nothing else, is why a level would otherwise need a hand-written parent
    class beside its category.
    """

    def __contains__(self, value: Any) -> bool:
        r"""Whether ``value`` is an object of this category.

        Sage decides membership by ``value.category()``, and a Sage morphism
        answers that with the category of its Mor object: every endomorphism
        of a module would then be a module, and ``C(f)`` would return ``f``
        itself as its own cokernel.  A morphism is an element of its Mor
        object, not an object of the category that Mor object lies in.  A
        category whose objects are arrows states its own membership.
        """
        match value:
            case Map() | CategoricalArrow():
                return False
            case _:
                return super().__contains__(value)

    @abstract_method
    def an_object(self) -> ObjectOfCategory:
        r"""Return one object of this category.

        A witness that the category is inhabited, and the datum every construction
        parameterized by a category needs: where ``C`` takes an object of ``D``,
        ``C(D.an_object())`` builds one without the caller knowing anything else
        about ``D``.

        Distinct from ``an_element``, which every parent carries and which produces
        an element *of that object*.  This produces an object *of this category*.

        Sage's ``Category.example`` is not this operation: it looks for a template
        module under ``sage.categories.examples`` and returns the ``NotImplemented``
        singleton when it finds none, so it answers for Sage's graph and is silent
        where it should be loud.

        A contract on every owned category, not a default: exhibiting an inhabitant
        is per-category mathematics, and a category that cannot is a gap in that
        category.
        """

class OwnedParameterizedCategory(OwnedCategory):
    r"""An owned category parameterized by one object of a stated category.

    ``parameter_category`` is the statement.  ``Subgroups`` is parameterized
    by a group, ``GObjects(G, Sets())`` by a group, ``DifferentialGradedModules`` by a
    differential graded algebra, ``GradedAlgebraModules`` by a graded algebra,
    ``PredicateSubgroups`` by a whole category.  Each of those is a different
    structure, and a family that does not say which one it wants can only
    report a wrong argument from wherever inside the first operation happened
    to need it -- ``this API expects a preamble group``, ``no attribute
    'grading_monoid'`` -- naming nothing about what was wanted.

    Stating it does two things.  A wrong parameter is refused at the boundary,
    against the category it should have been in, and a member of the family
    becomes constructible without knowing anything else about it: it is
    ``type(C)(C.parameter_category().an_object())``, which is what lets a
    survey of the owned graph reach a parameterized family at all instead of
    carrying a hand-written table of specimens.

    A family that has not stated it says so by name, through Sage's optional
    abstract-method protocol, and construction proceeds unchecked until it
    does.
    """

    @abstract_method(optional=True)
    def parameter_category(self) -> Category:
        r"""Return the category this family's parameter ranges over."""

    def __init__(self, parameter: Parent) -> None:
        # Stored before it is checked: a family over a base-relative category
        # (Cox rings over the toric schemes of the scheme's own base) states
        # its parameter category in terms of the parameter.
        self._owned_parameter = parameter
        declared = self.parameter_category
        if declared is not NotImplemented:
            ranges_over = declared()
            assert parameter in ranges_over, (
                f"{type(self).__name__} is parameterized by an object of "
                f"{ranges_over}, and {parameter} is not one"
            )
        super().__init__()

    def parameter(self) -> ObjectOfCategory:
        return self._owned_parameter

    def base(self) -> ObjectOfCategory:
        return self.parameter()


class Objects(OwnedCategory):
    r"""The root of the owned mathematical category graph.

    This category carries no mathematical supercategory. Sage's own
    ``Objects``/``Sets`` categories remain runtime substrate only and are not
    semantic ancestors of owned categories.
    """

    def __contains__(self, value: Any) -> bool:
        match value:
            case Map() | CategoricalArrow():
                from sage_extensions.categories.abstract_categories.mor_categories import MorCategories

                return value.parent() in MorCategories()
            case _:
                return super().__contains__(value)

    def an_object(self) -> ObjectOfCategory:
        r"""The set 2, which is an object like any other.

        The root has no structure to exhibit, so its witness is whatever the
        first level above it builds: two distinct elements, so that a map out
        of the witness is not forced.
        """
        from sage_extensions.categories.sets.set_categories import Sets

        return Sets().an_object()


    class ParentMethods(OwnedParent, Parent):
        r"""The owned root of every object chain.

        Every owned object is an object, so the host runtime initialization
        belongs here and nowhere above.  A level declares its own datum and
        threads into this one with a cooperative ``super().__init__(**rest)``.
        """

        def _with_structure(
            self,
            categories: tuple[Category, ...],
            construction_data: dict[str, ConstructionData],
            *,
            engine: type | None = None,
        ) -> ObjectOfCategory:
            r"""Construct, on the data of this exact object, an object of further categories.

            Protected construction contract (``OWN-05``, ``OWN-16``).  Owner:
            the category whose constructor builds this object.  Permitted
            callers: a level that adds chosen structure to a received object,
            as the slice ``C/X`` adds ``p: A -> X`` to an object ``A`` of
            ``C``.  ``categories`` are the categories of the added levels, the
            first of them the level that ``engine`` serves; ``construction_data``
            is their data, and ``engine`` an optional private computation class
            (``OWN-06``).  The result is a new object of the join of
            ``categories`` and of their supercategories, and of nothing else:
            placement follows construction (``ARC-08``, ``CON-07``), and the
            categories finer than ``C`` that hold this object are facts about
            this object, not about the result.  ``C/X`` declares ``C``, so the
            result has the operations of ``C``.

            No public operation can do this: the caller holds only the
            received object, and the data that construct it again (its
            owner's constructor, its defining data, its realization) belong to
            its owner.  A public constructor of the meet would make the caller
            restate that data, which is the parallel construction ``OWN-16``
            forbids.

            Here the result is constructed in the join of ``categories`` on
            the defining data of this object and the data of ``categories``.
            The class that realizes this object and its elements is the
            private computation of the result (``OWN-06``): it consumes the
            defining data and computes on them, and ``engine`` precedes it.
            An owner whose objects are built otherwise
            (an algebra on its engine ring, a module on its presentation)
            supplies its own construction.
            """
            construction = self._defining_construction
            assert construction is not None, (
                f"cannot construct {self} with the further structure of {categories}: it was not built by its "
                "category's constructor, so no owner constructs it again on its data"
            )
            _, _, data = construction
            _, level_data = self._added_structure({})
            owner_data = {name: datum for name, datum in data.items() if name not in level_data}
            added_categories, added_data = self._added_structure(construction_data)
            assert owner_data.keys().isdisjoint(added_data), (
                f"cannot add the data {sorted(construction_data)} to {self}: it already has "
                f"the data {sorted(owner_data)} of the same names"
            )
            target = owned_category_join((*added_categories, *categories))
            return _object_of(
                target,
                _engine=_realization_with_caller_engine(
                    target, type(self), self.element_class, engine
                ),
                **owner_data,
                **added_data,
            )

        def _added_structure(
            self,
            construction_data: dict[str, ConstructionData],
        ) -> tuple[tuple[Category, ...], dict[str, ConstructionData]]:
            r"""The categories and data that levels above this object's owner add to it, with ``construction_data``.

            Protected companion of :meth:`_with_structure` (``OWN-05``).
            Implementing roles: a level that adds structure on a received
            object extends this cooperatively.  It returns its categories and
            its data merged with the data of the same level in
            ``construction_data``, so constructing the object again with
            further structure keeps the structure it has: an object of
            ``C/X`` constructed in ``C/Y`` is an object of both slices, with
            one arrow in each.  Calling roles: an owner's
            :meth:`_with_structure`, and the arrow levels' ``arrow()``, which
            read the categories of the levels.  The root adds nothing and
            passes ``construction_data`` on.  The result is construction
            data, which no public operation returns.
            """
            return (), dict(construction_data)

        @cached_method
        def _selected_data_registry(self):
            return {}

        def has_selected_resolution(self, owner) -> bool:
            r"""Whether a chosen resolution relative to owner is stored."""
            return owner in self._selected_data_registry()

        def selected_resolution(self, owner):
            r"""Return the chosen resolution relative to owner."""
            registry = self._selected_data_registry()
            selected = registry.get(owner)
            match selected:
                case None:
                    raise ValueError(
                        f"{self} has no chosen resolution relative to {owner}"
                    )
                case _PendingResolution():
                    resolution = selected.realize()
                    registry[owner] = resolution
                    return resolution
                case _:
                    return selected

        def selected_resolution_generating_set(self, owner):
            r"""The set ``S`` of the chosen resolution relative to owner, realizing it only when unstated."""
            selected = self._selected_data_registry().get(owner)
            match selected:
                case _PendingResolution() if selected.generating_set() is not None:
                    return selected.generating_set()
                case _:
                    return self.selected_resolution(owner).generating_set()

        def selected_resolution_generator(self, owner, label):
            r"""Return a retained degree-zero generator, realizing only when it was not registered."""
            selected = self._selected_data_registry().get(owner)
            match selected:
                case _PendingResolution() if selected.has_generator_function():
                    return selected.generator(label)
                case _:
                    return self.selected_resolution(owner).generator(label)

        def __call__(self, *arguments, **options):
            r"""Construct an element of this object, without coercion discovery.

            The values an owned object accepts are themselves owned, and Sage's
            coercion graph has never heard of them: asked for a conversion map
            it tries to build a Mor in its own ``Sets``, finds the domain absent
            and raises, before this object's own constructor is ever reached.
            The crossing into owned data happens in ``_element_constructor_``,
            which is the one boundary that admits foreign values.
            """
            return self._element_constructor_(*arguments, **options)

    class ElementMethods(Element):
        r"""The owned root of every element chain: the host element runtime."""

    def super_categories(self):
        return []

    @classmethod
    def _repr_object_names(cls):
        return "represented mathematical objects"


__all__ = [
    "Objects",
    "OwnedCategory",
    "OwnedParameterizedCategory",
    "_fix_selected_resolution",
]
