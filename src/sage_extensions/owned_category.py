r"""Category-owned implementation types.

The public protocol is ``ObjectType`` and ``ElementType``.  A category's
``ObjectType`` is its complete object implementation, and that type's
``ElementType`` is the complete implementation of its elements.  The same
protocol applied to the Mor, End, and Aut categories gives the arrow types.

Sage's ``ParentMethods`` / ``ElementMethods`` / ``MorphismMethods`` names are
an internal input format for its named-class builder.  The adapter in this
module consumes that format.  No preamble constructor or mathematical surface
needs to expose it.

Sage builds a whole method MRO out of ``super_categories()`` and then throws
away the one thing that would make those method classes implementation
classes: ``Category._make_named_class`` passes ``prepend_cls_bases=False`` to
:func:`~sage.structure.dynamic_class.dynamic_class`, so the ``ParentMethods``
class itself never enters the MRO -- only a copy of its ``__dict__`` does.  A
copied ``__dict__`` carries no bases, so it cannot carry ``Parent``, so it
cannot carry fields.  That, and nothing else, is why every level of the
preamble needs a hand-written parent class beside its category, and why the
data those categories' methods need has to be installed by a separate step
after construction.

:class:`OwnedCategoryMixin` puts ``ParentMethods`` / ``ElementMethods`` /
``MorphismMethods`` *into the bases* of the named class instead.  Then:

* the named class inherits ``Parent`` (or ``Element``) through the root
  level's ``ParentMethods``, so ``SomeCategory().parent_class`` is directly
  instantiable and its instances hold data;
* zero-argument ``super()`` inside those methods resolves along the category
  graph, so construction threads exactly the way method lookup already
  threads, and a level supplies only the datum it declares;
* every method a mathematician reaches is in the source class it was written
  in, because that class is in the MRO.  Nothing is copied, generated or
  synthesized.

Two measurements fixed this shape:

* ``prepend_cls_bases=True`` -- splicing ``ParentMethods.__bases__`` in while
  still copying its dict -- does not work.  The ``__class__`` cell of every
  method still points at the provider class, which is not in the MRO, so
  zero-argument ``super()`` raises ``TypeError: obj is not an instance or
  subtype of type``.  Since cooperative ``super()`` is the whole mechanism,
  that variant is unusable.
* The root of an owned chain must have Sage's ``Sets()`` among its super
  categories.  ``Parent._init_category_`` re-wraps ``type(self)`` into
  ``dynamic_class(name, (type(self), category.parent_class))`` unless the
  parent is already an instance of ``Sets().parent_class``; under the flip
  those two are the same class, and the re-wrap raises ``TypeError:
  duplicate base class``.  The owned ``Sets`` root already declares Sage's
  ``Sets()``, which is what makes this work.

.. SEEALSO:: :mod:`sage_extensions.refine`, which hoists owned
   ``ParentMethods`` ahead of a *Sage-native* concrete class.  That remains
   the route for parents the preamble adopts rather than constructs; a parent
   built through an owned chain already has its methods in the right order
   and needs no rebuild.
"""

from __future__ import annotations

import copyreg
import hashlib
from _abc import _abc_init
from abc import ABCMeta
from collections import Counter
from collections.abc import Hashable
from dataclasses import dataclass
from functools import cache, wraps
from inspect import Parameter, isclass, ismethod, signature
from typing import TYPE_CHECKING

from sage.categories.category import Category, CategoryWithParameters, JoinCategory
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.misc.constant_function import ConstantFunction
from sage.misc.lazy_attribute import lazy_attribute
from sage.structure.category_object import CategoryObject
from sage.structure.dynamic_class import (
    DynamicInheritComparisonClasscallMetaclass,
    dynamic_class,
)
from sage.structure.parent import Parent as SageParent

if TYPE_CHECKING:
    from typing import Any

    from sage.structure.parent import Parent
    from sage_extensions.lexicon.category_theory import ObjectOfCategory

    # The construction data one level of an owned chain hands to the levels
    # above it.  Genuinely open: each level consumes the datum it declares and
    # passes the rest on, and the union closes only at the root, in Sage's
    # ``Parent.__init__`` keywords.  Named and aliased exactly once, here, so
    # that every ``**rest`` in every chain says what it carries and no site
    # writes the bare escape.
    type ConstructionData = Any


def _c3_merge(sequences: list[list[type]]) -> list[type]:
    r"""The C3 merge of linearizations, as Python computes an MRO.

    Reference: M. Simionato, *The Python 2.3 Method Resolution Order*
    (https://docs.python.org/3/howto/mro.html), the algorithm CPython's
    ``type.mro`` implements.
    """
    sequences = [list(sequence) for sequence in sequences if sequence]
    tail_occurrences = Counter(
        entry for sequence in sequences for entry in sequence[1:]
    )
    merged: list[type] = []
    while sequences:
        for sequence in sequences:
            head = sequence[0]
            if tail_occurrences[head] == 0:
                break
        else:
            raise TypeError(
                "Cannot create a consistent method resolution order (MRO) for the category graph: "
                + ", ".join(sequence[0].__name__ for sequence in sequences)
            )
        merged.append(head)
        for sequence in sequences:
            if sequence[0] is not head:
                continue
            sequence.pop(0)
            if sequence:
                tail_occurrences[sequence[0]] -= 1
        sequences = [sequence for sequence in sequences if sequence]
    return merged


@cache
def _owned_providers(cls: type) -> tuple[type, ...]:
    r"""The authored method classes a generated category class declares as its own bases."""
    return vars(cls).get("_owned_providers", ())


class _OwnedOrderMetaclass(type):
    def mro(cls) -> list[type]:
        r"""Order classes as the category graph orders the categories.

        A generated category class has the authored ``ParentMethods`` (or
        ``ElementMethods``, ``MorphismMethods``, ``SubcategoryMethods``) of its
        level among its bases, so every category contributes two classes.
        Plain C3 treats them as unrelated and may interleave other levels
        between them, and two branches can then interleave them in orders no
        single linearization satisfies, although the categories themselves
        linearize.  Here each level is one node: the merge runs over the
        generated classes, and each level's authored classes follow its
        generated class immediately.  This is the order Sage's own
        ``parent_class`` has, where each category is a single class.
        ``type.mro`` is Python's documented hook for a metaclass to supply it.

        Python stores the result as ``cls.__mro__`` when the class is created,
        and ``type.__mro__`` answers ``None`` only before then.  Sage's
        ``Parent.__init__`` calls ``self.__class__.mro()`` on every parent it
        initializes (``sage/structure/parent.pyx``), so a created class answers
        with its stored linearization instead of merging it again.
        """
        stored = type.__dict__["__mro__"].__get__(cls)
        if stored is not None:
            return list(stored)
        own = _owned_providers(cls)
        others = [base for base in cls.__bases__ if base not in own]
        glued = {
            provider
            for ancestor in (
                cls,
                *(entry for base in cls.__bases__ for entry in base.__mro__),
            )
            for provider in _owned_providers(ancestor)
        }

        def level_nodes(sequence) -> list[type]:
            return [entry for entry in sequence if entry not in glued]

        merged = _c3_merge(
            [level_nodes(base.__mro__) for base in others]
            + [level_nodes(provider.__mro__[1:]) for provider in own]
            + [level_nodes(others)]
        )
        # One authored class can serve several generated classes: a
        # parameterized category's instances share it.  It then follows the
        # last level that uses it, which every one of them precedes.
        levels = [cls, *merged]
        last_owner = {}
        for index, entry in enumerate(levels):
            for provider in own if entry is cls else _owned_providers(entry):
                last_owner[provider] = index
        order = []
        for index, entry in enumerate(levels):
            order.append(entry)
            order.extend(
                provider for provider, owner in last_owner.items() if owner == index
            )
        return order


# One ordered metaclass over Sage's most derived dynamic metaclass, so it
# dominates every mixture of Sage's four: Sage re-wraps an adopted parent's
# class with the category's ``parent_class`` choosing among its own four, and
# only a common subclass lets Python resolve that class.  ``ABCMeta`` comes
# first in the crossed one so its ``__new__`` runs ahead of the Cython
# metaclasses and records the abstract methods.
class _OwnedDynamicMetaclass(
    _OwnedOrderMetaclass, DynamicInheritComparisonClasscallMetaclass
):
    pass


class _DynamicABCMetaclass(ABCMeta, _OwnedDynamicMetaclass):
    pass


for _owned_metaclass in (_OwnedDynamicMetaclass, _DynamicABCMetaclass):
    # Pickle dispatches a *class* on its metaclass, and Sage registers its four
    # dynamic metaclasses this way; without the same registration for the
    # owned ones, pickling a parent_class falls through to a by-name lookup
    # that cannot resolve a dynamic class.
    copyreg.pickle(_owned_metaclass, _owned_metaclass.__reduce__)


def _abc_metaclass_for(bases: tuple[type, ...]) -> type:
    r"""Sage's dynamic metaclass for ``bases``, crossed with :class:`ABCMeta`.

    Enforcement of an obligation is ``ABCMeta`` refusing to instantiate a class
    that still has an unimplemented ``abstractmethod``.  Getting that on a
    ``parent_class`` needs both halves and neither is optional:

    * the provider declares ``metaclass=ABCMeta``, because ``ABCMeta.__new__``
      collects abstract names from the new class's own namespace and from each
      base's ``__abstractmethods__`` -- and a *plain* class has no
      ``__abstractmethods__``, so with the provider merely in the bases nothing
      is collected and nothing is enforced;
    * and the generated class's metaclass must be a subclass of both Sage's
      dynamic metaclass and ``ABCMeta``, or Python refuses the class outright
      with ``TypeError: metaclass conflict``.

    This is why the prior art's ``prepend_cls_bases=False`` was not arbitrary:
    copying the provider's dict put the abstract methods into the namespace,
    which is the other place ``ABCMeta`` looks.  Putting the provider in the
    bases instead is what makes cooperative ``super()`` work, so the collection
    has to come from the provider being an ABC in its own right.

    Both owned metaclasses derive from Sage's most derived dynamic metaclass,
    so either dominates every Sage metaclass a base can carry; the crossed one
    is chosen exactly when a base declares obligations.
    """
    match any(isinstance(base, ABCMeta) for base in bases):
        case True:
            metaclass = _DynamicABCMetaclass
        case False:
            metaclass = _OwnedDynamicMetaclass
    assert all(issubclass(metaclass, type(base)) for base in bases), (
        f"no owned metaclass dominates the bases of {bases}"
    )
    return metaclass


def _subcategory_class_of(category: Category) -> type:
    return category.subcategory_class


def _parent_class_of(category: Category) -> type:
    return category.parent_class


def _element_class_of(category: Category) -> type:
    return category.element_class


def _morphism_class_of(category: Category) -> type:
    return category.morphism_class


def _declared_category_class(category: Category) -> type:
    r"""Return the source class declaring ``category``, not Sage's dynamic wrapper."""
    category_type = type(category)
    if category_type.__name__.endswith("_with_category"):
        return category_type.__base__
    return category_type


def _category_graph_signature(category: Category, memo=None):
    r"""Return a session-independent signature of one category graph node.

    Comparison ordering is an implementation concern of the category graph, so
    the signature records exactly that graph: the declaring category class and
    the immediate supercategories.  It deliberately does *not* use ``repr`` or
    Sage's ``_cmp_key``.  Parameter values that induce the same category graph
    therefore share a signature, matching ``CategoryWithParameters``' named-
    class optimization; parameter regimes with different supercategory graphs
    do not. Once this signature has been incorporated into the category's
    persistent comparison key, that same signature is retained on the category
    for the overlapping supergraphs of later comparison keys. Before then only
    the call-local ``memo`` is used.
    """
    persistent = category.__dict__.get("_owned_graph_signature")
    if persistent is not None:
        return persistent
    if memo is None:
        memo = {}
    identity = id(category)
    cached = memo.get(identity)
    if cached is not None:
        return cached
    declaring = _declared_category_class(category)
    # Install a temporary acyclic marker only to make an accidental category
    # graph cycle fail here rather than recurse indefinitely.  Sage category
    # graphs are DAGs, so encountering it is a structural defect.
    marker = ("<category-cycle>", declaring.__module__, declaring.__qualname__)
    memo[identity] = marker
    supers = tuple(
        sorted(
            (
                _category_graph_signature(super_category, memo)
                for super_category in category._super_categories
            ),
            key=repr,
        )
    )
    signature = (declaring.__module__, declaring.__qualname__, supers)
    memo[identity] = signature
    return signature


def _category_graph_depth(category: Category, memo=None) -> int:
    r"""Return the depth of ``category`` in the immediate-supercategory DAG.

    As for the graph signature, a depth already fixed into the persistent
    comparison key is reusable by later keys; an unfixed graph stays local to
    this traversal.
    """
    persistent = category.__dict__.get("_owned_graph_depth")
    if persistent is not None:
        return persistent
    if memo is None:
        memo = {}
    identity = id(category)
    cached = memo.get(identity)
    if cached is not None:
        return cached
    supers = tuple(category._super_categories)
    if not supers:
        memo[identity] = 0
        return 0
    depth = 1 + max(
        _category_graph_depth(super_category, memo) for super_category in supers
    )
    memo[identity] = depth
    return depth


def _category_parameter_signature(category: Category):
    r"""Return structural parameter data needed to order category instances.

    Named implementation classes may legitimately be shared by categories with
    the same method graph, but C3 category merging still needs a strict order
    on distinct semantic parameters.  Mor families are parameterized by their
    base category, while fixed Mor categories are additionally parameterized by
    the owning Mor family: ``Mono_C(A,B)`` and ``Epi_C(A,B)`` can have the same
    runtime class and base category without being the same category.  Categories
    over scalars expose ``base``.  Record those parameters structurally without
    using object identity or ``repr``.
    Once this signature is stored in the category's persistent comparison key,
    later parameter chains reuse that same value.
    """
    persistent = category.__dict__.get("_owned_parameter_signature")
    if persistent is not None:
        return persistent
    mor_family = getattr(category, "mor_family", None)
    if callable(mor_family):
        try:
            family = mor_family()
        except (AttributeError, TypeError, ValueError):
            family = None
        if isinstance(family, Category):
            return (
                "mor_family",
                _category_graph_signature(family),
                _category_parameter_signature(family),
            )
    for accessor in ("base_category", "base"):
        method = getattr(category, accessor, None)
        if not callable(method):
            continue
        try:
            parameter = method()
        except (AttributeError, TypeError, ValueError):
            continue
        if parameter is category:
            continue
        parameter_type = type(parameter)
        signature = (accessor, parameter_type.__module__, parameter_type.__qualname__)
        # A fixed Mor is both a Category and a Sage Parent.  As a parameter it
        # is the parent object, just like any other ambient group or module;
        # its runtime type supplies the structural part and Sage's retained
        # session counter separates distinct instances.  Traversing its whole
        # semantic Mor graph here would compute derived arrow structure merely
        # to construct a category parameterized by that parent.
        if isinstance(parameter, Category) and not isinstance(parameter, SageParent):
            return (accessor, _category_graph_signature(parameter))
        engine = getattr(parameter, "_engine", None)
        if engine is not None:
            engine_type = type(engine)
            signature += ("engine", engine_type.__module__, engine_type.__qualname__)
        return signature
    return ()


def _stable_signature_integer(signature) -> int:
    r"""Encode a structural category signature as a deterministic positive integer."""
    digest = hashlib.blake2b(repr(signature).encode("utf-8"), digest_size=16).digest()
    return int.from_bytes(digest, "big")


class _OwnedCategoryComparisonKey:
    r"""Deterministic ``_cmp_key`` for owned categories.

    Sage's native comparison key is ``(flags, creation_counter)``.  The flags
    carry semantic ordering conventions, but the counter makes sibling order a
    function of which category a session happened to touch first.  Owned
    categories retain Sage's flags and replace only that counter by a structural
    integer.  Graph depth occupies the high bits, so a strict owned subcategory
    always compares below its owned supercategory; a digest of the category
    graph resolves siblings reproducibly.

    The structural integer does not separate two categories of one family whose
    parameter is an object rather than a category: ``C/X`` and ``C/Y`` have the
    same declaring class, the same supercategory ``C`` and the same base
    category.  Sage's C3 merge (``C3_sorted_merge`` in
    ``sage/misc/c3_controlled.pyx``) keys its tails by ``_cmp_key``, so two such
    categories in one join -- an object of ``C/X`` and of ``C/Y`` at once --
    need distinct keys.  Sage's session counter is kept as the last component;
    it orders only categories whose structural keys agree.

    This is a non-data descriptor.  Its first use writes the resulting tuple to
    the category instance, exactly as Sage's Cython descriptor does, after which
    normal instance lookup is the fast path.
    """

    _DEPTH_SHIFT = 160
    _OWNED_FLOOR = 1 << 240

    def __get__(self, category: Category | None, owner=None):
        if category is None:
            return self
        # Ask Sage's original descriptor for the flags and its session counter.
        # It temporarily stores them on the instance; the assignment below
        # immediately replaces that value with the owned structural key.
        native_descriptor = Category.__dict__["_cmp_key"]
        flags, session_counter = native_descriptor.__get__(category, type(category))
        # The comparison key is stored permanently on this category below.
        # Retain the graph inputs at exactly that boundary: caching them before
        # the key is fixed would freeze a category whose construction has not
        # yet finished, while recomputing them afterward cannot change the key.
        depth = _category_graph_depth(category)
        graph_signature = _category_graph_signature(category)
        category._owned_graph_depth = depth
        category._owned_graph_signature = graph_signature
        direct_graph = getattr(category, "_owned_direct_supercategories", None)
        category._owned_graph_supercategories = (
            tuple(category.super_categories())
            if direct_graph is None
            else direct_graph()
        )
        parameter_signature = _category_parameter_signature(category)
        category._owned_parameter_signature = parameter_signature
        signature = (
            graph_signature,
            parameter_signature,
        )
        structural = (
            self._OWNED_FLOOR
            + (depth << self._DEPTH_SHIFT)
            + _stable_signature_integer(signature)
        )
        result = (flags, structural, session_counter)
        category._cmp_key = result
        return result


class CatConstructionsMixin:
    r"""Carry what ``Cat`` declares a category can do, and nothing else.

    An owned **root** -- a category whose super categories are all Sage's --
    takes this one.  Everything below it inherits the constructions through
    ``subcategory_class`` and needs no declaration of its own.

    **Keep this separate from** :class:`OwnedCategoryMixin`.  The two do
    different jobs.  This one routes ``subcategory_class``, which is a *view*
    on a category, and no category competes for it.  The flip rebuilds
    ``parent_class`` / ``element_class`` / ``morphism_class``, which changes
    what a category's **objects** are.

    Giving a family the flip together makes MRO conflicts appear.  One example
    is ``OwnedCategoryOverBaseRing`` and the categories over it:
    ``TypeError: Cannot create a consistent method resolution order (MRO) for
    bases Modules.parent_class, FreeModules.ParentMethods``.

    A conflict of that kind is the design's own tripwire.  Its cause is a
    non-root methods class that names a base, which states the class graph by
    hand in place of the category graph.  Remove that base.  Do not avoid the
    flip, and do not apply the flip in stages: the migration is one sweep, and
    the conflicts it shows are the sites to repair.
    """

    def _make_named_class(
        self,
        name: str,
        method_provider: str,
        cache: bool = False,
        picklable: bool = True,
    ) -> type:
        if name == "subcategory_class":
            return self._subcategory_class_with_cat_constructions(
                method_provider, cache=cache, picklable=picklable
            )
        return super()._make_named_class(  # type: ignore[misc]
            name, method_provider, cache=cache, picklable=picklable
        )

    def _subcategory_class_with_cat_constructions(
        self,
        method_provider: str,
        cache: bool = False,
        picklable: bool = True,
    ) -> type:
        r"""``subcategory_class``, carrying what ``Cat`` declares a category can do.

        This is how the constructions reach a category, and it has to be this
        rather than the Cat-object attribute fallback, because **most owned
        categories are not objects the preamble builds**.  Measured on the real
        tree: of nine representative owned categories exactly one -- the bare
        root -- is a ``Parent``.  Every axiom category, every functorial
        construction and every join is a class Sage constructs, including
        ``Lattices.U.category()``, which is a ``JoinCategory``.  No change to
        the preamble's own class declarations reaches those, because
        ``Category.join`` builds them inside Sage.

        ``subcategory_class`` does reach all of them: Sage's
        ``Category.__init__`` sets a category's own class to
        ``dynamic_class(name, (cls, self.subcategory_class))``, and builds that
        from the super categories' ``subcategory_class``es.  So tying it once,
        at the owned root, propagates down the whole owned tree and through
        joins -- no per-category declaration, and nothing written on a Sage
        class.  ``Cat.ParentMethods`` enters as a **base**, never as a copied
        dict, so each construction keeps its source where it is declared.

        Cat is excluded: it is not an object of itself, so its own
        subcategories must not be handed the constructions.
        """
        category = self
        assert isinstance(category, Category), (
            f"{category!r} is not a category, so it has no subcategory class"
        )
        cat_constructions = _cat_constructions()
        provider, inherited = declared_implementation_types(
            type(category), (method_provider,)
        )
        assert not inherited, (
            f"the category {category} declares its subcategory methods ({method_provider}) "
            f"in more than one class: {inherited}; they must be declared once"
        )
        if provider is cat_constructions:
            return super()._make_named_class(  # type: ignore[misc]
                "subcategory_class",
                method_provider,
                cache=cache,
                picklable=picklable,
            )
        bases = tuple(
            super_category.subcategory_class
            for super_category in category._super_categories_for_classes
        )
        carried = any(cat_constructions in base.mro() for base in bases)
        if provider is not None and not any(provider in base.mro() for base in bases):
            bases = (provider,) + bases
        if not carried:
            # Last, never first.  A base that already carries the
            # constructions has them at the end of its own linearization, so
            # asking for them first here contradicts that base's order and C3
            # refuses the class: ``TypeError: Cannot create a consistent method
            # resolution order (MRO) for bases Rngs.subcategory_class,
            # Cat.ParentMethods, ...``.  Most general goes last, and nothing
            # here competes for a name anyway.
            bases = bases + (cat_constructions,)
        declaring_class = type(category)
        if declaring_class.__name__.endswith("_with_category"):
            declaring_class = declaring_class.__base__
        doccls = provider or declaring_class
        # A base reached twice -- a join whose members share a super
        # category -- is one base, in the position it was first required.
        seen: dict[type, None] = {}
        for base in bases:
            seen.setdefault(base, None)
        bases = tuple(seen)

        reduction = (_subcategory_class_of, (category,)) if picklable else None
        owned_providers = () if provider is None else (provider,)
        metaclass = _abc_metaclass_for(bases)
        result = metaclass(
            f"{declaring_class.__name__}.subcategory_class",
            bases,
            {
                "_owned_providers": owned_providers,
                "_reduction": reduction,
                "_doccls": (doccls,),
                "__doc__": doccls.__doc__,
                "__module__": doccls.__module__,
            },
        )
        _abc_init(result)
        return result


@cache
def declared_implementation_types(
    declaring_class: type,
    provider_names: tuple[str, ...],
) -> tuple[type | None, tuple[type, ...]]:
    r"""The implementation declarations made by the category's class graph.

    Returns the most derived one, which Sage would have taken alone, and the
    ones its declaration hides.

    Sage's dynamic lookup returns the most derived declaration and nothing
    else.  A category class that both derives
    from an owned construction base -- :class:`SubobjectsCategory`, say -- and
    declares its own ``ParentMethods`` therefore *replaces* the base's rather
    than extending it, so the base can only reach categories with nothing of
    their own to add.  That inverts what a base is for.

    Nothing is spliced in to repair it: the relation is already stated, by the
    class graph the category declarations write down, and this reads it.  Each
    ancestor's own declaration becomes a base, most derived first, exactly as
    Python would resolve them if the nested classes were the outer ones.  A
    declaration an earlier one already derives from is left out; naming it
    twice is not a stronger statement and C3 refuses the class.

    Order is not new authority.  A name a derived level defines still wins over
    the base's, which is what makes an override an override; what changes is
    that a name the derived level is silent about now falls through to the base
    instead of vanishing.
    """
    if declaring_class.__name__.endswith("_with_category"):
        # Sage's per-category dynamic class, whose second base is the
        # ``subcategory_class``.  What a category declares is on the class it
        # was written as, so that is the graph read here.
        declaring_class = declaring_class.__base__
    declared: list[type] = []
    for ancestor in declaring_class.__mro__:
        for provider_name in provider_names:
            inherited = ancestor.__dict__.get(provider_name)
            if inherited is None:
                continue
            assert isinstance(inherited, type), (
                f"{ancestor.__name__}.{provider_name} must be a type"
            )
            if any(issubclass(seen, inherited) for seen in declared):
                continue
            declared.append(inherited)
    if not declared:
        return None, ()
    return declared[0], tuple(declared[1:])


def _owned_implementation_bases(
    category: Category,
    provider_names: tuple[str, ...],
) -> tuple[type, ...]:
    r"""Return one cooperative implementation MRO for an owned category.

    Sage flattens join-valued supercategories when it computes a category's
    immediate supercategories.  Consequently the same C3 conflict that occurs
    on an explicit join also occurs on an ordinary category such as
    ``RootLattices`` whose one declared supercategory is a join.  Inheriting
    already-composed ``parent_class`` objects can make individually valid MROs
    impose a precedence cycle on shared providers.  The category linearization
    already fixes the mathematical order, so every owned category composes the
    declared providers from that linearization directly instead of nesting
    dynamic implementation classes.
    """
    bases: list[type] = []
    for level in category._all_super_categories:
        provider, inherited = declared_implementation_types(type(level), provider_names)
        candidates = (() if provider is None else (provider,)) + inherited
        for candidate in candidates:
            if any(
                candidate is known or issubclass(known, candidate) for known in bases
            ):
                continue
            bases = [known for known in bases if not issubclass(candidate, known)]
            bases.append(candidate)

    # A stronger construction can consume one datum and derive a lower-level
    # constructor parameter before cooperative ``super()`` reaches that owner.
    # Flattening branch implementation classes must retain that dependency,
    # not merely the category comparison order.  ``BiproductModules`` is the
    # canonical example: it consumes ``biproduct_factors`` and derives the
    # ``summands`` parameter of ``DirectSumObjects``.  Put every such producer
    # before the providers that explicitly consume its derived names, keeping
    # the category-linearized order as the stable tie-breaker.
    explicit_parameters: dict[type, frozenset[str]] = {}
    for provider in bases:
        initializer = provider.__dict__.get("__init__")
        if initializer is None:
            explicit_parameters[provider] = frozenset()
            continue
        parameters = signature(initializer).parameters.values()
        explicit_parameters[provider] = frozenset(
            parameter.name
            for parameter in parameters
            if parameter.name != "self"
            and parameter.kind not in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)
        )

    predecessors = {provider: set() for provider in bases}
    # Objects owns the terminal Sage Parent initialization. Every other
    # cooperative provider must consume its construction data before that
    # boundary, including providers from a different branch of a join.
    from sage_extensions.categories.abstract_categories.objects import Objects

    if Objects.ParentMethods in predecessors:
        predecessors[Objects.ParentMethods].update(
            provider for provider in bases if provider is not Objects.ParentMethods
        )
    for producer in bases:
        derived = frozenset(getattr(producer, "_derived_construction_parameters", ()))
        if not derived:
            continue
        for consumer in bases:
            if producer is consumer:
                continue
            if derived.intersection(explicit_parameters[consumer]):
                predecessors[consumer].add(producer)

    pending = set(bases)
    ordered: list[type] = []
    while pending:
        ready = tuple(
            provider
            for provider in bases
            if provider in pending and not predecessors[provider].intersection(pending)
        )
        assert ready, (
            "constructor-data dependencies among implementation providers are acyclic"
        )
        selected = ready[0]
        ordered.append(selected)
        pending.remove(selected)
    return tuple(ordered) or (object,)


class OwnedCategoryMixin(CatConstructionsMixin):
    r"""Tie a category to its implementation classes.

    A mixin rather than a ``Category`` subclass because
    ``CategoryWithParameters._make_named_class`` -- inherited by
    ``Category_over_base``, ``JoinCategory``, ``CategoryWithAxiom`` and the
    Sage functorial-construction categories
    -- calls ``Category._make_named_class`` *by name*, so an override placed
    further down the ``Category`` hierarchy is bypassed.  Placed first in the
    bases it handles the tied names itself and delegates the rest along the
    MRO, which composes with every one of those.

    Intercepting ``CategoryWithParameters`` costs something, and the decision
    is to pay it back rather than accept it.  That override exists to share one
    named class between categories differing only in a parameter -- its own
    doctest asserts ``Algebras(GF(7)).parent_class is
    Algebras(GF(5)).parent_class`` -- and taking the tied names before it runs
    would silently make that ``False``.  Sharing is still right under the flip,
    because the flip puts construction on the class but never the parameter:
    two such categories have the same provider and the same super-category
    named classes, so literally the same bases, and each object holds its own
    parameter as instance data.  So the cache is honoured below, and measured
    to track Sage: same key shares, different key does not, and a shared class
    still enforces its obligations.
    """

    _TIED_NAMED_CLASSES = frozenset(("parent_class", "element_class", "morphism_class"))

    # Sage's default key ends in a global creation counter.  Owned categories
    # instead derive that ordering component from their declared graph, so class
    # construction is independent of which branch a session happened to touch
    # first.  The descriptor is inherited by every owned category shape in
    # ``owned_category_bases.py`` and intentionally does not affect Sage-native
    # categories.
    _cmp_key = _OwnedCategoryComparisonKey()

    def __init_subclass__(cls, **options) -> None:
        r"""Retain the defining call of each owned category constructor.

        A category can itself receive chosen structure: an object of
        ``Cat/C`` is a category together with a selected functor to ``C``.
        Reconstructing that structured object must therefore use the same
        category constructor and its exact defining arguments.  The outermost
        constructor records those arguments after its cooperative chain has
        completed; inherited constructors record the concrete runtime
        declaration, so axiom and parameterized category subclasses retain
        their own category kind rather than the base implementation class.

        This is construction data of the category owner (``OWN-16``), not a
        public serialization format.  It is consumed only by
        :class:`OwnedCategoryObject` when another category level is added.
        """
        super().__init_subclass__(**options)
        initializer = vars(cls).get("__init__")
        if initializer is None or getattr(
            initializer, "_retains_owned_category_call", False
        ):
            return

        @wraps(initializer)
        def retaining_initializer(self, *args, **keywords):
            initializer(self, *args, **keywords)
            declared = _declared_category_class(self)
            self._owned_category_construction = (
                declared,
                tuple(args),
                dict(keywords),
            )

        retaining_initializer._retains_owned_category_call = True
        cls.__init__ = retaining_initializer

    def is_subcategory(self, category):
        r"""Compare owned categories through their declared mathematical graph.

        Owned implementation classes are provider-linearized rather than
        nested along the category graph, because the latter need not admit a
        common Python C3 MRO.  They are therefore implementation vehicles, not
        subcategory witnesses.  Category inclusion is the declared forgetful
        graph itself, with the intersection rules handled by
        :func:`_declared_category_is_subcategory`.
        """
        return _declared_category_is_subcategory(self, category)

    def _subcategory_hook_(self, category):
        r"""Answer incoming subcategory queries from the owned graph as well.

        Sage calls the *target* category's hook before the source category's
        ``is_subcategory`` implementation.  This matters for mixed host joins
        such as the category of ``Sets.Δ[n]``: one branch is the owned finite
        ordinal category and the other branches are Sage's finite/facade
        implementation categories.  The intersection is still an owned set
        because its owned branch forgets to :class:`Sets`; Python inheritance
        between the mixed join's ``parent_class`` and the owned target is not
        that mathematical statement.  Use the same declared join law for this
        target-side query.
        """
        return _declared_category_is_subcategory(category, self)

    _IMPLEMENTATION_PROVIDER_NAMES = {
        "ParentMethods": ("ParentMethods",),
        "ElementMethods": ("ElementMethods",),
        "MorphismMethods": ("MorphismMethods",),
    }

    def _object_type_of_object_type(self) -> type | None:
        r"""Return the object type carried by this category's object type.

        Most objects are not categories, so the default has no second object
        type.  Categories of Mor categories override this: a Mor category is
        itself a category, and its objects are the arrows.
        """
        return None

    @cached_method
    def _with_axiom_as_tuple(self, axiom):
        r"""Return structural branches whose meet adds ``axiom``.

        This follows Sage's ``Category._with_axiom_as_tuple`` construction,
        but its final redundancy elimination is read from the declared
        supercategory ancestry rather than ``is_subcategory``.  The latter
        synthesizes ``parent_class`` objects and is therefore circular while
        owned category implementation classes are still being assembled.
        """
        if axiom in self.axioms():
            return (self,)
        if axiom in self.__class__.__base__.__dict__:
            from sage.categories.category_with_axiom import CategoryWithAxiom

            axiom_attribute = getattr(self.__class__.__base__, axiom)
            if isclass(axiom_attribute) and issubclass(
                axiom_attribute, CategoryWithAxiom
            ):
                return (axiom_attribute(self),)
            return (self,)
        if not any(axiom in base.__dict__ for base in self.__class__.__mro__):
            return (self,)

        result = (self,) + tuple(
            branch
            for category in self._super_categories
            for branch in category._with_axiom_as_tuple(axiom)
        )
        hook = getattr(self, axiom + "_extra_super_categories", None)
        if hook is not None:
            assert ismethod(hook)
            result += tuple(hook())

        reduced = []
        for member in result:
            if any(
                other is not member
                and member in other._set_of_super_categories
                and other not in member._set_of_super_categories
                for other in result
            ):
                continue
            if all(member is not known for known in reduced):
                reduced.append(member)
        return tuple(reduced)

    @cached_method
    def _with_axiom(self, axiom):
        r"""Return this owned category with ``axiom`` through the owned meet.

        Sage's axiom closure still computes the mathematical branches through
        :meth:`Category._with_axiom_as_tuple`.  Only their runtime join is
        owned: its implementation types inherit the immediate branch types,
        which already carry every indirect owned implementation.
        """
        return owned_category_join(self._with_axiom_as_tuple(axiom))

    def _make_named_class(
        self,
        name: str,
        method_provider: str,
        cache: bool = False,
        picklable: bool = True,
    ) -> type:
        if name not in self._TIED_NAMED_CLASSES:
            return super()._make_named_class(  # type: ignore[misc]
                name, method_provider, cache=cache, picklable=picklable
            )
        assert cache is False, (
            f"building {name} of the category {self} was asked to cache the class, "
            f"but {name} is built without a cache; add a cache here rather than "
            f"dropping the request"
        )
        category = self
        declaring_class = type(category)
        if declaring_class.__name__.endswith("_with_category"):
            declaring_class = declaring_class.__base__
        provider_names = self._IMPLEMENTATION_PROVIDER_NAMES[method_provider]
        match name:
            case "parent_class":
                bases = _owned_implementation_bases(category, provider_names)
                reduction_function = _parent_class_of
            case "element_class":
                bases = _owned_implementation_bases(category, provider_names)
                reduction_function = _element_class_of
            case "morphism_class":
                bases = _owned_implementation_bases(category, provider_names)
                reduction_function = _morphism_class_of
            case _:
                raise AssertionError(f"unsupported implementation type {name}")
        provider, _inherited = declared_implementation_types(
            declaring_class, provider_names
        )
        doccls = provider or declaring_class
        class_name = f"{declaring_class.__name__}.{name}"
        reduction = (reduction_function, (category,)) if picklable else None

        # Sharing the named class between categories that differ only in a
        # parameter is ``CategoryWithParameters``' whole reason to exist, and
        # its own doctest asserts ``Algebras(GF(7)).parent_class is
        # Algebras(GF(5)).parent_class``.  Intercepting the tied names ahead of
        # that override would drop it, so the cache is honoured here instead.
        # It stays sound under the flip because the parameter is never on the
        # class: two such categories have the same ``ParentMethods`` and the
        # same super-category named classes, hence literally the same bases,
        # and each object carries its own parameter as instance data.
        key: tuple[type, str, Hashable] | None = None
        if isinstance(category, CategoryWithParameters):
            key = (declaring_class, name, bases)
            shared = category._make_named_class_cache.get(key)
            if shared is not None:
                return shared

        def build() -> type:
            # Built with the owned crossed metaclass, whose ``mro`` keeps each
            # level's authored classes next to its generated class, and which
            # carries any obligations a level declared.  Built by hand because
            # :func:`dynamic_class` takes no metaclass, so the crossed
            # dynamic/ABCMeta one cannot be requested from it; this mirrors
            # ``dynamic_class_internal`` in
            # ``sage/structure/dynamic_class.py`` and reproduces exactly its
            # ``_reduction`` / ``_doccls`` / ``__doc__`` / ``__module__``
            # bookkeeping.  Two things there are deliberately not mirrored: its
            # ``weak_cached_function`` cache, which the assertion above shows is
            # never asked for on this path, and its ``__slots__`` suppression,
            # which cannot fire because a provider is a plain Python class and
            # so always contributes a ``__dictoffset__``.
            result = _abc_metaclass_for(bases)(
                class_name,
                bases,
                {
                    "_reduction": reduction,
                    "_doccls": (doccls,),
                    "__doc__": doccls.__doc__,
                    "__module__": doccls.__module__,
                },
            )
            # Sage's dynamic/Classcall/InheritComparison metaclasses perform
            # their required initialization when called above, but their type
            # construction path precedes ``ABCMeta.__new__`` in the metaclass
            # MRO.  Initialize CPython's ABC state explicitly after preserving
            # that Sage lifecycle; otherwise ``isinstance`` reaches
            # ``ABCMeta.__instancecheck__`` with no ``_abc_impl``.
            _abc_init(result)
            return result

        result = build()
        if key is not None:
            current_bases = _owned_implementation_bases(category, provider_names)
            if key[2] != current_bases:
                # The parameter's category was refined while we built, so the
                # key we would store is stale.  Sage's own override handles
                # this the same way: discard and recompute.
                return self._make_named_class(
                    name, method_provider, cache=cache, picklable=picklable
                )
            category._make_named_class_cache[key] = result
        if name == "parent_class":
            result.ElementType = category.element_class
            arrow_type = category._object_type_of_object_type()
            if arrow_type is not None:
                result.ObjectType = arrow_type
        return result


class OwnedJoinCategory(OwnedCategoryMixin, JoinCategory):
    r"""The computed intersection of owned categories.

    This is Sage's join mathematically.  The separate runtime class is needed
    because owned implementation providers are bases rather than copied method
    dictionaries; :class:`OwnedCategoryMixin` therefore linearizes the
    immediate branch implementations directly.
    """

    def category(self) -> Category:
        r"""The category constructed as this intersection is an object of Cat."""
        return _cat()

    def __contains__(self, value) -> bool:
        r"""Decide an intersection of declared property categories by its branches."""
        branches = self._super_categories
        if all(
            any(
                "_certifying_predicate" in vars(level) for level in type(branch).__mro__
            )
            for branch in branches
        ):
            return all(value in branch for branch in branches)
        return super().__contains__(value)

    def _call_(self, data, *args, **options):
        r"""Construct through a unique most-specific branch and check the join.

        An intersection of an object category with an axiom category retains
        the object's constructor. The constructor establishes its own data and
        property placement; the join admits the result only when all its
        required properties were established.
        """
        constructors = tuple(
            branch
            for branch in self._super_categories
            if type(branch)._call_ is not Category._call_
        )
        selected = tuple(
            branch
            for branch in constructors
            if not any(
                other is not branch and other.is_subcategory(branch)
                for other in constructors
            )
        )
        if len(selected) != 1:
            raise NotImplementedError(
                f"{self} has no unique constructor among its declared branches"
            )
        result = selected[0](data, *args, **options)
        if result not in self:
            raise ValueError(f"{result!r} does not satisfy {self}")
        return result

    def is_subcategory(self, category):
        r"""Compare this intersection through its mathematical branches.

        Sage's generic join implementation first asks the target category's
        ``_subcategory_hook_`` about the join.  The default hook compares
        ``parent_class`` objects.  Owned joins deliberately flatten their
        implementation providers because the complete branch classes can have
        no common C3 linearization, so that implementation-class comparison is
        no longer a semantic test.  The declared category graph already
        records the forgetful maps, including their concrete parameters, and
        the join law supplies the intersection cases.  Use that graph only;
        falling back to a branch's generic ``is_subcategory`` would simply
        re-enter the same ``parent_class`` proxy through the target hook.
        """
        return _declared_category_is_subcategory(self, category)


@cached_function
def _declared_category_is_subcategory(category: Category, target: Category) -> bool:
    r"""Read category inclusion from the declared graph, without class synthesis.

    This is the comparison used while an owned join is being normalized.  At
    that point ``parent_class`` may not exist yet, so Sage's default
    ``is_subcategory`` fallback to ``issubclass(parent_class, ...)`` is a
    circular implementation test.  A join is an intersection: it lies below a
    target when one branch does, and a category lies below a join when it lies
    below every branch.  For ordinary nodes, the transitive declared
    supercategory set is the forgetful-functor relation available before any
    implementation classes are built.
    """
    if category is target:
        return True
    if isinstance(target, JoinCategory):
        return all(
            _declared_category_is_subcategory(category, branch)
            for branch in target._super_categories
        )
    if isinstance(category, JoinCategory):
        return any(
            _declared_category_is_subcategory(branch, target)
            for branch in category._super_categories
        )

    # Some parameterized families carry mathematically canonical change-of-
    # parameter inclusions which are not inheritance edges.  The distinction is
    # essential when only part of the source refinement survives the parameter
    # change: declaring a raw supercategory edge would make Sage propagate every
    # axiom through it.  When ordinary graph ancestry does not already decide
    # it, ask each declared ancestor directly for such a relation:
    # the unaxiomatized owner is already among those ancestors, while forcing
    # _without_axioms here can recursively normalize unrelated categories.
    if target in category._set_of_super_categories:
        return True
    sources = (category, *category._set_of_super_categories)
    for source in sources:
        relation = getattr(
            type(source),
            "_declared_parameter_subcategory_relation",
            None,
        )
        if relation is not None and relation(source, source, target) is True:
            return True
    return False


def _owned_flatten_categories(categories) -> tuple[Category, ...]:
    r"""Flatten join branches without invoking Sage's subcategory sorter."""
    flattened = []
    for category in categories:
        if isinstance(category, JoinCategory):
            flattened.extend(category._super_categories)
        else:
            flattened.append(category)
    return tuple(flattened)


def _owned_sort_uniq(categories) -> tuple[Category, ...]:
    r"""Return the declared-antichain normalization of ``categories``."""
    ordered = tuple(
        sorted(
            _owned_flatten_categories(categories),
            key=lambda category: category._cmp_key,
            reverse=True,
        )
    )
    result = []
    for category in ordered:
        if any(_declared_category_is_subcategory(known, category) for known in result):
            continue
        result.append(category)
    return tuple(result)


def _owned_join_as_tuple(categories) -> tuple[Category, ...]:
    r"""Canonicalize an owned intersection while propagating its axioms.

    This is Sage's ``join_as_tuple`` algorithm with exactly one substitution:
    every redundancy comparison uses the declared category graph above rather
    than ``is_subcategory``.  The axiom propagation itself is unchanged in
    substance; in particular an intersection of a free-form category with a
    finite-generation refinement still produces the corresponding
    ``FreeFormModules.FinitelyGenerated`` category and retains its methods.
    """
    categories = _owned_sort_uniq(categories)
    axioms = set()
    for category in categories:
        axioms.update(category.axioms())

    done = {category: category.axioms() for category in categories}
    todo = {
        (category, axiom)
        for category, known_axioms in done.items()
        for axiom in axioms.difference(known_axioms)
    }
    while todo:
        category, axiom = todo.pop()
        if category not in done:
            continue
        new_categories = tuple(
            new_category
            for new_category in _owned_flatten_categories(
                category._with_axiom_as_tuple(axiom)
            )
            if not any(
                _declared_category_is_subcategory(known, new_category) for known in done
            )
        )
        for known in tuple(done):
            if any(
                _declared_category_is_subcategory(new_category, known)
                for new_category in new_categories
            ):
                del done[known]

        new_axioms = {
            new_axiom
            for new_category in new_categories
            for new_axiom in new_category.axioms()
            if new_axiom not in axioms
        }
        axioms.update(new_axioms)
        for known in done:
            for new_axiom in new_axioms:
                todo.add((known, new_axiom))
        for new_category in new_categories:
            known_axioms = new_category.axioms()
            done[new_category] = known_axioms
            for missing in axioms.difference(known_axioms):
                todo.add((new_category, missing))
    return _owned_sort_uniq(done)


def owned_category_join(categories) -> Category:
    r"""Return Sage's axiom-closed join realized as an owned join category."""
    branches = _owned_join_as_tuple(tuple(categories))
    assert branches, "the join of no owned categories is not represented"
    if len(branches) == 1:
        return branches[0]
    return OwnedJoinCategory(branches)


@dataclass(frozen=True)
class ConstructionParameter:
    r"""One named datum consumed by one level of an owned constructor chain."""

    name: str
    provider: type
    kind: str
    required: bool
    default: object | None
    annotation: object | None


@dataclass(frozen=True)
class ConstructionContract:
    r"""The discoverable constructor contract of one owned category.

    Cooperative constructors intentionally pass unknown data onward through
    ``**rest``.  The contract therefore records both the named parameters each
    preamble provider consumes and the providers that still leave an open
    variadic boundary.  Duplicate parameter names are retained when two
    mathematical levels independently consume the same spelling.
    """

    owner: object
    parameters: tuple[ConstructionParameter, ...]
    variadic_providers: tuple[type, ...]
    opaque_providers: tuple[type, ...]
    hook_providers: tuple[type, ...]

    def named(self, name: str) -> tuple[ConstructionParameter, ...]:
        return tuple(
            parameter for parameter in self.parameters if parameter.name == name
        )

    def derived_names(self) -> frozenset[str]:
        r"""Return lower-level constructor data supplied by a stronger provider.

        A specialization may take one mathematical datum and compute the data
        consumed by its immediate general construction before calling
        ``super().__init__``.  Those lower-level names remain visible in the
        full contract, but they are not additional obligations on the public
        caller.
        """
        names = set()
        for provider in {parameter.provider for parameter in self.parameters}:
            names.update(getattr(provider, "_derived_construction_parameters", ()))
        return frozenset(names)

    def required_names(self) -> frozenset[str]:
        required = frozenset(
            parameter.name for parameter in self.parameters if parameter.required
        )
        return required - self.derived_names()

    def optional_names(self) -> frozenset[str]:
        return frozenset(
            parameter.name for parameter in self.parameters if not parameter.required
        )

    def is_open(self) -> bool:
        return bool(self.variadic_providers or self.opaque_providers)

    def has_refinement_hooks(self) -> bool:
        return bool(self.hook_providers)

    def validate(self, data) -> None:
        r"""Validate one supplied construction datum against this contract.

        Every named required parameter discovered from an owned constructor
        level must be supplied before the host runtime is entered.  Unknown
        names are rejected only when the contract is closed: a provider with
        ``**rest`` or an opaque signature deliberately keeps an open boundary
        for data consumed by a higher runtime level.
        """
        supplied = frozenset(data)
        missing = self.required_names() - supplied
        if missing:
            missing_names = ", ".join(sorted(missing))
            raise TypeError(
                f"{self.owner} construction is missing required data: {missing_names}"
            )
        if self.is_open():
            return
        declared = self.required_names() | self.optional_names()
        unexpected = supplied - declared
        if unexpected:
            unexpected_names = ", ".join(sorted(unexpected))
            raise TypeError(
                f"{self.owner} construction received undeclared data: {unexpected_names}"
            )


@cached_function
def _construction_contract_from_type(
    owner,
    implementation_type: type,
    *,
    owned_object_chain: bool = False,
) -> ConstructionContract:
    r"""Discover named constructor data contributed by one implementation MRO.

    Object construction is delimited structurally: every implementation level
    before :class:`OwnedParent` belongs to the owned category chain, regardless
    of the Python module where a concrete owned category is declared.  This is
    what makes the contract a property of the mathematical owner rather than a
    package-layout convention.  Other callers retain the narrower preamble
    module boundary used for fixed Mor parents.
    """
    parameters: list[ConstructionParameter] = []
    variadic: list[type] = []
    opaque: list[type] = []
    hooks: list[type] = []
    for provider in implementation_type.__mro__:
        if owned_object_chain:
            if provider is OwnedParent:
                break
        elif not provider.__module__.startswith("sage_extensions"):
            continue
        if "__init_extra__" in provider.__dict__:
            hooks.append(provider)
        initializer = provider.__dict__.get("__init__")
        if initializer is None:
            continue
        try:
            provider_signature = signature(initializer)
        except (TypeError, ValueError):
            opaque.append(provider)
            continue
        for parameter in provider_signature.parameters.values():
            if parameter.name == "self":
                continue
            if parameter.kind is Parameter.VAR_KEYWORD:
                if provider is OwnedParent:
                    # ``OwnedParent`` is the terminal host-runtime sink of the
                    # cooperative chain, not a mathematical constructor level.
                    # Counting its ``**rest`` would make every owned contract
                    # permanently open and would prevent _object_of from ever
                    # detecting undeclared public construction data.
                    continue
                variadic.append(provider)
                continue
            if parameter.kind is Parameter.VAR_POSITIONAL:
                opaque.append(provider)
                continue
            if parameter.name == "category":
                continue
            has_default = parameter.default is not Parameter.empty
            annotation = (
                None
                if parameter.annotation is Parameter.empty
                else parameter.annotation
            )
            default = parameter.default if has_default else None
            parameters.append(
                ConstructionParameter(
                    name=parameter.name,
                    provider=provider,
                    kind=parameter.kind.name,
                    required=not has_default,
                    default=default,
                    annotation=annotation,
                )
            )
    return ConstructionContract(
        owner=owner,
        parameters=tuple(parameters),
        variadic_providers=tuple(dict.fromkeys(variadic)),
        opaque_providers=tuple(dict.fromkeys(opaque)),
        hook_providers=tuple(dict.fromkeys(hooks)),
    )


def _construction_contract(category: Category) -> ConstructionContract:
    r"""Discover the defining data contributed by ``category.ObjectType``'s MRO.

    Only constructors declared in the preamble are part of this mathematical
    contract.  Sage runtime bases remain implementation substrate.  A provider
    whose signature cannot be inspected is retained explicitly as opaque; a
    provider with ``**rest`` is retained as variadic.  Discovery never changes
    construction behavior and never interprets an omitted name as optional.
    """
    return _construction_contract_from_type(
        category,
        category.ObjectType,
        owned_object_chain=True,
    )


def _mor_construction_contract(
    category: Category,
    domain: Parent,
    codomain: Parent,
) -> ConstructionContract:
    r"""Discover how the fixed Mor parent ``Hom_category(domain,codomain)`` is built.

    This is the contract of the selected Mor object itself: its Mor family and
    endpoints.  It is deliberately distinct from :func:`_construction_contract`
    on the fixed Mor category, which describes construction of an arrow *in*
    that Mor.
    """
    mor = category.Mor(domain, codomain)
    return _construction_contract_from_type(mor, type(mor))


@cached_function
def _implementation_with_engine(
    implementation: type, owner: type, engine: type
) -> type:
    r"""Insert a private engine immediately before its owner's implementation.

    This is the same native implementation-class mechanism as
    ``OwnedCategoryMixin._make_named_class``, not a category declaration.
    The bases ``(implementation, (engine, owner))`` force every stronger
    provider already preceding ``owner`` to remain before the engine, while
    the engine precedes the owner's defaults.  In particular an algebra's
    multiplication cannot be shadowed by its sparse-module realization.

    Types, not category parameters or object identities, index the cache:
    parameterized categories may share an implementation type.  Defining
    data are passed to the resulting object, never stored on this type.
    """
    if not issubclass(implementation, owner):
        # An owned join linearizes the declared method providers directly, so
        # its implementation type need not (and in the interesting C3 cases
        # cannot) subclass the already-composed dynamic class of each branch.
        # The owner's providers are nevertheless present among the join's
        # direct bases.  Insert the private engine immediately before the first
        # such base, preserving the same semantic precedence as the ordinary
        # subclass path below: stronger providers first, engine computation,
        # then the owner's defaults and the weaker structure underneath it.
        # The owner of a category that Sage builds (``Cat``) copies each
        # method provider into its own class rather than inheriting it, and
        # records the provider as ``_doccls`` (``dynamic_class_internal``,
        # sage/structure/dynamic_class.py).  An owned join lists the provider
        # class itself among its bases, so both name the owner's providers.
        # The engine also precedes every base it specializes: a join may
        # place the root ``Objects.ParentMethods``, which an engine of a
        # Sage-built owner names as its base, before that owner's providers.
        owner_mro = frozenset(owner.__mro__) | frozenset(
            provider.__dict__["_doccls"][0]
            for provider in owner.__mro__
            if "_doccls" in provider.__dict__
        )
        anchors = tuple(
            index
            for index, base in enumerate(implementation.__bases__)
            if base in owner_mro or issubclass(engine, base)
        )
        assert anchors, (
            f"cannot insert the computation class {engine.__name__} for objects of type "
            f"{implementation.__name__}: none of its bases descends from "
            f"{owner.__name__}, the object type of the category the computation serves"
        )
        anchor = anchors[0]
        bases = (
            implementation.__bases__[:anchor]
            + (engine,)
            + implementation.__bases__[anchor:]
        )
        reduction = (_implementation_with_engine, (implementation, owner, engine))
        if not any(isinstance(base, ABCMeta) for base in bases):
            return dynamic_class(
                f"{implementation.__name__}[{engine.__name__}]",
                bases,
                implementation,
                reduction=reduction,
                doccls=engine,
                prepend_cls_bases=False,
                cache=False,
            )
        methods = dict(implementation.__dict__)
        for key in ("__dict__", "__weakref__", "__slots__"):
            methods.pop(key, None)
        methods.update(
            _reduction=reduction,
            _doccls=(engine,),
            __doc__=engine.__doc__,
            __module__=engine.__module__,
        )
        result = _abc_metaclass_for(bases)(
            f"{implementation.__name__}[{engine.__name__}]",
            bases,
            methods,
        )
        _abc_init(result)
        return result
    match implementation is owner:
        case True:
            bases = (engine, owner)
        case False:
            bases = (implementation, _implementation_with_engine(owner, owner, engine))
    result = _abc_metaclass_for(bases)(
        f"{implementation.__name__}[{engine.__name__}]",
        bases,
        {
            "_reduction": (
                _implementation_with_engine,
                (implementation, owner, engine),
            ),
            "_doccls": (engine,),
            "__doc__": engine.__doc__,
            "__module__": engine.__module__,
        },
    )
    _abc_init(result)
    return result


@cached_function
def _engine_object_type(
    object_type,
    owner_object_type,
    object_engine,
    element_type,
    owner_element_type,
    element_engine,
):
    r"""The native parent/element realization, without a second category node."""
    realized = _implementation_with_engine(
        object_type, owner_object_type, object_engine
    )
    namespace = {
        "_reduction": (
            _engine_object_type,
            (
                object_type,
                owner_object_type,
                object_engine,
                element_type,
                owner_element_type,
                element_engine,
            ),
        ),
        "_doccls": (object_engine,),
        "__doc__": object_engine.__doc__,
        "__module__": object_engine.__module__,
    }
    match element_engine:
        case None:
            # The category's element type is the implementation, which
            # OwnedParent.element_class returns for a parent declaring no
            # Element; declaring it would make Sage compose it with itself.
            pass
        case _:
            # Sage Parent.element_class consumes Element; the owned public
            # type protocol already has the complete implementation.  Expose
            # it directly so Sage does not wrap it in a second dynamic class
            # carrying the same category element base.
            elements = _implementation_with_engine(
                element_type, owner_element_type, element_engine
            )
            namespace["Element"] = elements
            namespace["ElementType"] = elements
            namespace["element_class"] = elements
    result = type(realized)(f"{realized.__name__}.ObjectType", (realized,), namespace)
    if isinstance(type(result), type) and issubclass(type(result), ABCMeta):
        _abc_init(result)
    return result


def _owned_realization_of_join(category: Category) -> Category:
    r"""A Sage join of owned categories, as the owned join of the same branches; any other category unchanged."""
    match category:
        case OwnedJoinCategory():
            return category
        case JoinCategory():
            return owned_category_join(category.super_categories())
        case _:
            return category


def _object_of(
    category: Category,
    *,
    _engine: tuple[Category, type, type | None] | None = None,
    _ambient: Category | None = None,
    **data: ConstructionData,
) -> ObjectOfCategory:
    r"""The object of ``category`` built from the data its levels declare.

    The instantiable class is ``category.parent_class``; this is the one line
    that spells that, so a construction's public name stays one thin function
    with the signature its callers already write.

    A free function rather than a method on :class:`OwnedCategoryMixin`
    because the category an object is built in is routinely a
    ``JoinCategory`` -- construction images joined with set axioms are --
    and a join is Sage's class, which the preamble consumes and does not
    extend.  The join's ``parent_class`` has the owned levels among its bases,
    so it constructs exactly the same way.

    The base ring is not supplied here.  A level that sits over a ring states
    its own ``base`` when it calls ``super().__init__``, the way the module
    Mor does, because a level may name a base its category does not -- and
    injecting one here would arrive twice at the levels that already do.

    A join reaching here from ``Category.join`` is realized as the owned join
    of the same branches: its implementation type then composes the branches'
    declared providers directly, which is what inserting a computation class
    before its owner's providers requires.
    """
    category = _owned_realization_of_join(category)
    match _engine:
        case None:
            implementation = category.ObjectType
        case (declared_owner, object_engine, element_engine):
            owner = _owned_realization_of_join(declared_owner)
            assert category.is_subcategory(owner), (
                f"cannot construct an object of {category} with the computation class "
                f"{object_engine.__name__}: that class serves {owner}, and {category} is "
                f"not a subcategory of {owner}"
            )
            implementation = _engine_object_type(
                category.ObjectType,
                owner.ObjectType,
                object_engine,
                category.ElementType,
                owner.ElementType,
                element_engine,
            )
    # The ambient category (ARC-07) is the placement category unless the
    # construction names the category of whose objects this is one, either
    # here or, for a route that reaches this entry through
    # ``_with_structure``, as the construction datum ``_constructing_category``.
    ambient = data.pop("_constructing_category", _ambient)
    _construction_contract_from_type(
        category, implementation, owned_object_chain=True
    ).validate(data)
    return implementation(
        category=category,
        _defining_construction=(category, _engine, data),
        _constructing_category=category if ambient is None else ambient,
        **data,
    )


def _cat() -> Category:
    r"""``Cat()``, resolved late: the constructions it declares import this module."""
    from sage_extensions.categories.abstract_categories.cat import Cat

    return Cat()


def _cat_constructions() -> type:
    r"""``Cat.ObjectType``: what a category can do as an object of Cat."""
    from sage_extensions.categories.abstract_categories.cat import Cat

    return Cat.ParentMethods


class OwnedParent:
    r"""Base of the root ``ParentMethods`` of an owned chain: elements come
    from the category.

    Sage's :meth:`Parent.element_class` composes the parent's own ``Element``
    attribute with the category's ``element_class``, and returns
    ``NotImplemented`` when the parent declares no ``Element``.  A chain-built
    parent declares none: the category's ``ElementMethods`` *is* the element
    implementation class, for exactly the reason ``ParentMethods`` is the
    parent one.  This says so.

    Reaches only objects built through the chain.  An *adopted* Sage parent
    keeps its own ``Element`` -- ``refine`` does not hoist a methods class that
    declares ``Parent`` (see ``refine._IMPLEMENTATION_BASES``), so this never
    enters such a parent's MRO and cannot shadow it.
    """

    def __init__(
        self,
        category=None,
        _defining_construction=None,
        _constructing_category=None,
        **rest,
    ) -> None:
        r"""Initialize the host shell without a second class rewrite.

        ``_defining_construction`` is the category, private computation class
        and data that :func:`_object_of` constructed this object from.  The
        root retains it, so the owner can construct an object with added
        structure on the data of this exact object (``OWN-16``,
        ``Objects.ParentMethods._with_structure``).  It is ``None`` for an
        object that its category's constructor did not build.

        ``_constructing_category`` is the category of whose objects this is
        one, the ambient category of ``ARC-07``.  It is the placement
        category unless the construction places the object further, as a
        subobject placed in ``Subgroups(G)`` is an object of the groups with
        an inclusion as additional data.

        A chain-built parent already *is* ``category.ObjectType``, which is the
        category's ``parent_class``.  ``Parent.__init__`` would rewrite
        ``__class__`` into ``dynamic_class(cls, category.parent_class)`` and so
        name that class twice.  ``CategoryObject._init_category_`` records the
        category and rewrites nothing, which is all a chain-built parent wants;
        this is the same technique ``OwnedCategoryObject`` uses one level up.

        Sage records the complete category, including its facade category,
        before invoking construction hooks.  Cooperative category
        constructors establish their defining data before reaching this root.
        """
        from sage_extensions.refine import (
            construction_scope,
            realize_owned_category,
            run_construction_hooks,
        )

        self._defining_construction = _defining_construction
        self._constructing_category = _constructing_category
        with construction_scope(self) as reached:
            SageParent.__init__(self, category=category, **rest)
            realize_owned_category(self)
            run_construction_hooks(self, reached)

    def _init_category_(self, category: Category) -> None:
        r"""Record the category on a parent built from its owned method chain.

        This is the native ``CategoryObject.__init__`` interception point
        used by ``Parent.__init__`` in ``sage/structure/parent.pyx``.
        The chain already supplies ``category.parent_class``.
        """
        CategoryObject._init_category_(self, category)

    @lazy_attribute
    def element_class(self) -> type:
        # A chain-built parent declares no ``Element``: the category's
        # ``ElementMethods`` is the element implementation, for the same reason
        # ``ParentMethods`` is the parent one.  A parent still declaring its own
        # -- one not yet migrated onto the chain -- keeps it, which is Sage's
        # own rule and what lets the two coexist while the migration runs.
        declared = getattr(type(self), "Element", None)
        if declared is None:
            return self.category().ElementType
        return SageParent.element_class.f(self)


class _BaseRingOfACategoryOverABase:
    r"""``base_ring`` on an owned category, present exactly when there is a base.

    Making a category a ``Parent`` (:class:`OwnedCategoryObject`) hands it
    ``CategoryObject.base_ring``, which answers ``self._base`` -- and that is
    ``None`` for every category which is not over a base.  Sage's own comment
    on that method calls it a pollution of the namespace of all category
    objects, and here it is one: ``Modules.SubcategoryMethods.base_ring``
    finds the ring of a join by returning ``C.base_ring()`` for the first
    super category carrying a ``base_ring`` **attribute**, so a single owned
    category over no base -- an owned ``Sets()``, an owned additive group, a
    slice category -- makes the whole join answer ``None``, and then a module
    built in that join is a module over no ring.

    A category over no base does not have a base ring, so it does not have the
    attribute.  ``hasattr`` is then false for exactly the categories that
    search means to skip, the join answers the ring of the member which has
    one, and nothing is written on a Sage class.
    """

    def __get__(
        self, category: Category | None, owner: type | None = None
    ) -> ConstantFunction | _BaseRingOfACategoryOverABase:
        if category is None:
            return self
        base = category.base()
        if base is None:
            raise AttributeError(
                f"{type(category).__name__} is over no base, so it has no base ring"
            )
        return ConstantFunction(base)


class OwnedCategoryObject:
    r"""A Sage category that is additionally an **object of** :math:`\mathbf{Cat}`.

    Sage's ``Category`` is not a ``CategoryObject``: ``Category.category()``
    answers ``Objects()`` and there is no attribute fallback, so the only way to
    give every category the constructions declared in ``Cat.ParentMethods`` was
    to write them onto Sage's own ``Category`` class.  Being a ``Parent`` whose
    ``_category`` is ``Cat()`` replaces that: ``CategoryObject.__getattr__``
    falls through to ``self._category.parent_class``, so a category reaches
    ``Cat``'s constructions the ordinary Sage way and nothing is installed on a
    class the preamble does not own.

    **What this currently buys, stated so it is not re-derived.**  It buys no
    computation.  Two justifications for it have been measured and falsified:
    the \(\mathbf{Cat}\) constructions do *not* reach a category this way --
    they arrive through ``subcategory_class``, which is what covers the joins
    and axiom categories most owned categories actually are -- and ``Mor(C, D)``
    does *not* route to the functor space by parenthood either; that follows
    the domain being an owned category, again through ``subcategory_class``.
    It is kept because a category **is** an object of \(\mathbf{Cat}\), which
    is what ``Cat.super_categories() == [Objects()]`` says, and the code should
    say it too: foundational structure is not discarded for having no callers.
    Its one near-use so far: had Sage's ``Morphism`` been available as a base
    for functors, it would have *required* the boundary categories to be
    parents -- see ``abstract_categories/functors.sage``, which explains why
    that route is closed.

    The base order below every subclass must keep is
    ``OwnedCategoryMixin, OwnedCategoryObject, <Sage category base>, Parent``:

    * the flip first, so its ``_make_named_class`` wins;
    * ``OwnedCategoryObject`` before the Sage base, because that is the one
      semantic change -- ``category()`` answers ``Cat()`` rather than
      ``Objects()``;
    * the Sage base before ``Parent``, or ``__contains__``, ``__call__``,
      ``base``/``base_ring`` and ``element_class`` resolve to parent
      element-construction logic, which is wrong for a category;
    * ``Parent`` last, present only so the object really is one.
    """

    base_ring = _BaseRingOfACategoryOverABase()

    def _with_structure(
        self,
        categories: tuple[Category, ...],
        construction_data: dict[str, ConstructionData],
        *,
        engine: type | None = None,
    ) -> Category:
        r"""Construct this actual category with further chosen structure.

        Protected construction contract (``OWN-05``, ``OWN-16``), parallel
        to ``Objects.ParentMethods._with_structure`` for ordinary objects.
        The category owner reconstructs its exact declaration from the
        defining constructor call retained at initialization.  The added
        category levels consume their own data cooperatively; the resulting
        object remains an actual instance of the original category class, so
        its objects, arrows, identity and composition are those of that
        category rather than operations on a category wrapper.
        """
        construction = getattr(self, "_owned_category_construction", None)
        assert construction is not None, (
            f"cannot construct the category {self} with the further structure of {categories}: "
            "its owner did not retain the category's defining constructor call"
        )
        added_categories, added_data = self._added_structure(construction_data)
        target = owned_category_join((*added_categories, *categories))
        declared, _, _ = construction
        realization = _category_structure_realization(declared, engine)

        from sage_extensions.refine import owned_parent_class

        implementation = owned_parent_class(realization, target)
        return typecall(
            implementation,
            _received_category=self,
            _structured_category=target,
            **added_data,
        )

    def _added_structure(
        self,
        construction_data: dict[str, ConstructionData],
    ) -> tuple[tuple[Category, ...], dict[str, ConstructionData]]:
        r"""Return category levels already added above this category owner."""
        return (), dict(construction_data)

    def _init_cat_object(self) -> None:
        r"""Initialize the parent shell without a second class rewrite.

        Not ``Parent.__init__(category=Cat())``: that runs
        ``Parent._init_category_``, which rewrites ``__class__`` into a dynamic
        class -- and Sage's ``Category.__init__`` already made one
        ``*_with_category``.  Two rewrites give ``Sets_with_category_with_category``,
        and ``CategoryWithAxiom.__classget__`` strips exactly one layer before
        checking that a nested axiom class belongs to its base category, so
        ``Sets().Finite()`` fails.  ``CategoryObject._init_category_`` records
        the category and rewrites nothing, which is all that is wanted here.
        """
        SageParent.__init__(self, category=None)
        CategoryObject._init_category_(self, _cat())

    def category(self) -> Category:
        return getattr(
            self,
            "_structured_category",
            getattr(self, "_category", _cat()),
        )


@cached_function
def _category_structure_realization(
    declared: type,
    engine: type | None,
) -> type:
    r"""The private realization of ``declared`` with added category levels.

    Added ``ParentMethods`` precede this boundary and consume their own
    construction data.  The boundary then invokes the original category
    declaration with the exact call retained by the received category.  It
    finally records the structured placement selected before construction.
    No public category or functor wrapper is introduced: instances remain
    instances of ``declared``.
    """

    def initialize(
        structured,
        *,
        _received_category: Category,
        _structured_category: Category,
        **remaining,
    ) -> None:
        assert not remaining, (
            f"the category levels added to {_received_category} did not consume "
            f"their construction data {sorted(remaining)}"
        )
        constructor, args, keywords = _received_category._owned_category_construction
        assert constructor is declared, (
            f"the retained constructor of {_received_category} changed from "
            f"{declared.__name__} to {constructor.__name__} during reconstruction"
        )
        constructor.__init__(structured, *args, **keywords)
        structured._owned_category_construction = (
            constructor,
            args,
            dict(keywords),
        )
        structured._structured_category = _structured_category
        CategoryObject._init_category_(structured, _structured_category)

    initialize._retains_owned_category_call = True

    boundary_bases = (declared,)
    name = f"{declared.__name__}WithChosenStructure"
    boundary = _abc_metaclass_for(boundary_bases)(
        f"{name}OwnerBoundary",
        boundary_bases,
        {
            "__init__": initialize,
            "__module__": declared.__module__,
            "__doc__": declared.__doc__,
        },
    )
    _abc_init(boundary)
    if engine is None:
        return boundary

    # The private engine owns construction data at this realization level.
    # Put it before the owner boundary so its cooperative initializer consumes
    # that datum, then let the boundary reconstruct the original category from
    # the retained defining call.
    bases = (engine, boundary)
    realization = _abc_metaclass_for(bases)(
        name,
        bases,
        {
            "__module__": declared.__module__,
            "__doc__": declared.__doc__,
        },
    )
    _abc_init(realization)
    return realization
