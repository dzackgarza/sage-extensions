"""Owned category refinement for parents already owned by the preamble.

Sage's ``_refine_category_`` joins categories but leaves the concrete class
before category methods in the MRO.  For an owned parent, this helper rebuilds
its dispatch class so owned category methods win; an abstract contract or a
realization hook of the category is fulfilled by the implementation the object
already has.  Adoption of Sage parents is
not performed here: free modules, groups, rings and other adopted objects enter
through owned facades that hold the Sage parent as a private engine.
"""

import inspect
from _abc import _abc_init
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from functools import update_wrapper

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.abstract_method import AbstractMethod
from sage.misc.cachefunc import cached_function
from sage.structure.category_object import CategoryObject
from sage.structure.dynamic_class import dynamic_class
from sage.structure.element import Element
from sage.structure.parent import Parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoricalArrow,
    OwnedMor,
)

_PREAMBLE_PACKAGE = __name__.rpartition(".")[0] + "."


# A methods class naming one of these among its bases is an implementation
# class, not a mixin: it is the class an owned category is tied to.
_IMPLEMENTATION_BASES = (Parent, Element, Morphism)


@cached_function
def _owned_mixins(category: Category, attr: str) -> tuple[type, ...]:
    """Return owned nested method classes in category order.

    A function of the category alone, which is a unique representation, so it
    is computed once per category rather than once per object built in it.
    """
    providers: list[type] = []
    for cat in category.all_super_categories(proper=False):
        for category_type in type(cat).__mro__:
            if not category_type.__module__.startswith(_PREAMBLE_PACKAGE):
                continue
            provider = vars(category_type).get(attr)
            if not isinstance(provider, type) or provider in providers:
                continue
            if issubclass(provider, _IMPLEMENTATION_BASES):
                # The root of an owned construction chain declares its methods
                # class over the host runtime base, so that class *is* the
                # implementation rather than a mixin over one.  An adopted Sage
                # parent already has its own, and hoisting this one would
                # shadow it.
                continue
            providers.append(provider)
    return tuple(providers)


class RealizationHook:
    r"""A protected decision procedure that a realization of the category may supply.

    The owner is the category whose ``ParentMethods`` declares the hook; the
    hook's body there is the answer when no participant decides, and the
    public operation of that category is its only caller.  For a predicate
    hook that answer is the proposition the public predicate states
    (``DEF-06``); for a value hook it is ``None``, which states that no value
    was supplied and leaves the public operation to its own cases or to its
    assertion frontier (``CAT-01``).  A realization whose
    construction determines the answer (``Mor(G, H)`` of finite groups counts
    its homomorphisms) supplies the hook on its own class; a more specific
    category supplies it on its ``ParentMethods``.  The public operation
    cannot be overridden for this, because it also owns every standard case
    the realization does not decide.

    :func:`_rebuild_parent_class` puts the category's method classes before
    the realization, so the undecided default would shadow the realization's
    answer.  A hook declared with this marker is therefore resolved like an
    abstract contract (:func:`_supply_participant_implementations`): the
    implementation the realization already has wins over the default.
    """

    def __init__(self, default: Callable) -> None:
        self._default = default
        update_wrapper(self, default)

    def __get__(self, instance, owner=None):
        return self._default.__get__(instance, owner)


def _supply_participant_implementations(new_class: type, mixins: tuple[type, ...], inherited: type) -> None:
    """Let an implementation the object already has fulfil each contract and hook it reaches.

    The rebuilt class puts the owned methods of the category before the
    class they refine, so a category operation wins over a class method of
    the same name.  An ``abstract_method`` is not an operation: it states that
    a participant of the category supplies one (``STY-48``).  A
    :class:`RealizationHook` is not one either: its body is the answer when
    no participant decides.  When the winner for a name is such a contract
    or hook and ``inherited`` already resolves that name to a preamble
    implementation, that implementation is the participant's answer, and it
    is aliased onto ``new_class`` ahead of the contract.  An implementation
    defined outside the preamble, by a Sage host class, does not fulfil an
    owned contract.
    """
    declarations = (AbstractMethod, RealizationHook)
    contracts = {
        name
        for provider in mixins
        for name, value in vars(provider).items()
        if isinstance(value, declarations)
    }
    for name in contracts:
        if not isinstance(inspect.getattr_static(new_class, name), declarations):
            continue
        definer = next(
            (klass for klass in inherited.__mro__ if name in vars(klass)),
            None,
        )
        if definer is None or not definer.__module__.startswith(_PREAMBLE_PACKAGE):
            continue
        supplied = vars(definer)[name]
        if isinstance(supplied, declarations):
            continue
        setattr(new_class, name, supplied)


@cached_function
def _owned_dynamic_class(name: str, bases: tuple[type, ...], doccls: type) -> type:
    r"""``dynamic_class(name, bases, doccls=doccls)`` built with the owned metaclass.

    Mirrors ``dynamic_class_internal`` (``sage/structure/dynamic_class.py``)
    and its ``_reduction`` / ``_doccls`` / ``__doc__`` / ``__module__``
    bookkeeping, as ``owned_category`` does for its generated classes.  Sage
    chooses ``DynamicClasscallMetaclass`` for a classcall implementation
    whose category is not yet recorded, and that metaclass and the owned one
    of a category's ``subcategory_class`` have no common subclass; a Mor
    object built from this class records its category by joining the two.
    """
    from sage_extensions.owned_category import _abc_metaclass_for

    result = _abc_metaclass_for(bases)(
        name,
        bases,
        {
            "_reduction": (_owned_dynamic_class, (name, bases, doccls)),
            "_doccls": (doccls,),
            "__doc__": doccls.__doc__,
            "__module__": doccls.__module__,
        },
    )
    _abc_init(result)
    return result


def owned_parent_class(implementation: type, category: Category) -> type:
    r"""The class of a parent of ``implementation`` whose owned methods are those of ``category``.

    The owned ``ParentMethods`` of ``category`` that ``implementation`` does
    not already carry come first, so a category operation wins over a class
    method of the same name; ``implementation`` is returned unchanged when
    there are none.  A construction that knows its category before the object
    exists instantiates this class, so the ``__init__`` of every level runs in
    one cooperative chain; ``_rebuild_parent_class`` gives an existing object
    the same class.
    """
    providers = _owned_mixins(category, "ParentMethods")
    if not providers:
        return implementation
    inherited = implementation.__dict__.get("_preamble_inherited", implementation)
    carried = frozenset(inherited.__mro__)
    mixins = tuple(provider for provider in providers if provider is not object and provider not in carried)
    if not mixins:
        # Sage's category-backed dynamic class can carry an AbstractMethod in
        # its own dictionary even though the selected category MRO has a
        # concrete owner for that operation. Such a local descriptor shadows
        # every category provider. Install the existing owner descriptor on a
        # thin runtime class; do not duplicate the method implementation.
        def is_abstract(value):
            return isinstance(value, AbstractMethod) or getattr(
                value, "__isabstractmethod__", False
            )

        overrides = {}
        for name, value in implementation.__dict__.items():
            if not is_abstract(value):
                continue
            for provider in providers:
                candidate = vars(provider).get(name)
                if candidate is None or is_abstract(candidate):
                    continue
                overrides[name] = candidate
                break
        if not overrides:
            return implementation
        new_class = _owned_dynamic_class(
            f"Owned{implementation.__name__}ConcreteProviders",
            (implementation,),
            implementation,
        )
        for name, value in overrides.items():
            setattr(new_class, name, value)
        new_class._preamble_concrete = implementation.__dict__.get(
            "_preamble_concrete", inherited
        )
        new_class._preamble_inherited = inherited
        return new_class

    # ``inherited`` already contains the method providers reached by earlier
    # construction steps.  A later refinement prepends only newly reached
    # providers, which can otherwise let a *supercategory* method shadow the
    # more specific operation already selected by the final category.  Keep
    # the final category order authoritative for colliding public operations.
    # The alias is the original provider's descriptor, not a second
    # implementation.  Private construction hooks stay on their provider so
    # ``run_construction_hooks`` still executes each level exactly once.
    new_names = {
        name
        for provider in mixins
        for name in vars(provider)
        if not name.startswith("_")
    }
    preferred = {}
    seen = set()
    for provider in providers:
        for name, value in vars(provider).items():
            if name.startswith("_") or name in seen:
                continue
            seen.add(name)
            if provider in carried and name in new_names:
                preferred[name] = value

    concrete = implementation.__dict__.get("_preamble_concrete", inherited)
    new_class = _owned_dynamic_class(f"Owned{concrete.__name__}", (*mixins, inherited), concrete)
    for name, value in preferred.items():
        setattr(new_class, name, value)
    _supply_participant_implementations(new_class, mixins, inherited)
    new_class._preamble_concrete = concrete
    new_class._preamble_inherited = inherited
    return new_class


def _rebuild_parent_class(parent: Parent, category: Category) -> None:
    parent.__class__ = owned_parent_class(type(parent), category)



def _rebuild_element_class(parent: Parent, category: Category) -> None:
    from sage.categories.sets_cat import Sets as SageSets

    # A facade's elements belong to the parents it stands for; it has no
    # element class of its own to rebuild.
    if category.is_subcategory(SageSets().Facade()):
        return
    mixins = _owned_mixins(category, "ElementMethods")
    if not mixins:
        return
    native = parent.element_class
    carried = frozenset(native.__mro__)
    mixins = tuple(m for m in mixins if m is not object and m not in carried)
    if not mixins:
        return
    parent.__dict__.pop("_abstract_element_class", None)
    element_class = dynamic_class(
        f"{type(parent).__name__}.element_class",
        (*mixins, native),
        doccls=native,
    )
    _supply_participant_implementations(element_class, mixins, native)
    parent.element_class = element_class


def _rebuild_morphism_class(morphism: Morphism, category: Category) -> None:
    mixins = _owned_mixins(category, "MorphismMethods")
    if not mixins:
        return
    inherited = type(morphism).__dict__.get("_preamble_inherited", type(morphism))
    carried = frozenset(inherited.__mro__)
    mixins = tuple(m for m in mixins if m is not object and m not in carried)
    if not mixins:
        return
    concrete = type(morphism).__dict__.get("_preamble_concrete", inherited)
    new_class = dynamic_class(
        f"Owned{concrete.__name__}",
        (*mixins, inherited),
        doccls=concrete,
    )
    _supply_participant_implementations(new_class, mixins, inherited)
    new_class._preamble_concrete = concrete
    new_class._preamble_inherited = inherited
    morphism.__class__ = new_class


def check_certifying_predicates(obj: SageObject, category: Category, held: Category) -> None:
    """Raise ``ValueError`` unless ``obj`` has each property ``category`` certifies beyond ``held``.

    A category states the property that admits an object as the sequence of
    public operations that reads it off, left to right: ``"is_even"`` asks the
    lattice, ``"module_rank.is_finite"`` asks the lattice for its rank and the
    rank for its finiteness.  The last operation answers ``True`` or the
    object does not belong.  A category ``held`` already contains is not asked
    again.
    """
    for certified in category.all_super_categories(proper=False):
        category_type = type(certified)
        if not category_type.__module__.startswith(_PREAMBLE_PACKAGE):
            continue
        statement = getattr(category_type, "_certifying_predicate", None)
        if statement is None or held.is_subcategory(certified):
            continue
        answer = obj
        for operation in statement.split("."):
            answer = getattr(answer, operation)()
        if answer is not True:
            raise ValueError(
                f"{obj} is not an object of {certified}: {statement}() answers {answer}"
            )


def realize_owned_category[SageObjectT: SageObject](obj: SageObjectT) -> SageObjectT:
    r"""Realize the owned methods of the category already chosen at construction.

    This is runtime plumbing, not mathematical refinement.  In particular it
    never changes ``obj.category()`` and therefore cannot be used to add
    construction data or category membership after instantiation.
    """
    category = obj.category()
    if isinstance(obj, (Morphism, CategoricalArrow)):
        _rebuild_morphism_class(obj, category)
        return obj
    if isinstance(obj, Parent):
        _rebuild_parent_class(obj, category)
        if not isinstance(obj, OwnedMor):
            _rebuild_element_class(obj, category)
    return obj


@contextmanager
def construction_scope(obj: SageObject) -> Iterator[set[type]]:
    r"""Share Sage's construction-hook traversal with nested refinements.

    ``Parent.__init__`` calls the hooks in its initial MRO itself.  Reserve
    those providers while it runs; refinements add their new providers to the
    same traversal.  The set lasts only for the active construction call.
    """
    reached = obj.__dict__.get("_preamble_construction_hooks")
    if reached is not None:
        yield reached
        return
    reached = set(type(obj).__mro__)
    obj._preamble_construction_hooks = reached
    try:
        yield reached
    finally:
        del obj._preamble_construction_hooks


def run_construction_hooks(obj: SageObject, reached: set[type]) -> None:
    r"""Run the construction step of every level ``obj`` has newly reached.

    A category level states what it establishes on its objects in
    ``__init_extra__``, and the host runs those hooks in one pass over the MRO
    from ``Parent.__init__`` (``sage/structure/parent.pyx``).  Neither
    ``CategoryObject._refine_category_`` nor ``Parent._refine_category_`` runs
    them.  ``reached`` is shared by the enclosing construction and any
    refinement a hook requests.  Enter a provider before invoking it so a
    nested refinement preserves the enclosing traversal.
    """
    for provider in type(obj).__mro__:
        if provider in reached:
            continue
        reached.add(provider)
        if "__init_extra__" in vars(provider):
            provider.__init_extra__(obj)


def refine[SageObjectT: SageObject](
    obj: SageObjectT,
    category: Category | Iterable[Category],
) -> SageObjectT:
    r"""Add a verified property/axiom category to an already constructed object."""
    from sage_extensions.owned_category import owned_category_join

    target = category if isinstance(category, Category) else owned_category_join(tuple(category))
    check_certifying_predicates(obj, target, obj.category())
    if isinstance(obj, (Morphism, CategoricalArrow)):
        # A morphism's mathematical membership is determined by its Mor
        # parent.  There is no independent Sage category slot to mutate here;
        # the target only supplies the owned morphism-method surface selected
        # by that already-constructed Mor theory.
        _rebuild_morphism_class(obj, target)
        return obj
    with construction_scope(obj) as reached:
        current = obj.category()
        if current is not target:
            CategoryObject._init_category_(obj, owned_category_join((current, target)))
        realized = realize_owned_category(obj)
        run_construction_hooks(obj, reached)
        return realized
