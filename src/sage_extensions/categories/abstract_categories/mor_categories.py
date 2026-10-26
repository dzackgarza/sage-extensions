r"""Mor/End/Mono/Epi/Iso/Aut category packets.

For every category ``C`` and objects ``A,B`` in ``C`` we represent
``Hom_C(A,B)`` itself as a category.  Its objects are the actual arrows
``A -> B``.  In the absence of represented 2-morphisms this category is
discrete.  An inclusion ``C <= D`` can include these fixed categories' arrows
without identifying ``Hom_C(A,B)`` with ``Hom_D(A,B)``.  The families classify
the selected category objects, not their individual arrows: their inclusions
must preserve those category objects.  In particular ``Ends(C) <= Mors(C)``
and ``Auts(C) <= Isos(C)`` reuse the same diagonal categories.  A functor
changing the fixed category acts through ``induced_mor_functor``,
``induced_end_functor`` or ``induced_aut_functor``.

This is intentionally distinct from the *underlying Mor object parent*.  The
latter may carry additional enrichment -- for example ``Hom_R(M,N)`` is an
``R``-module -- while there remains exactly one categorical Mor object for the
chosen category and endpoints.

An arrow ``f: A -> B`` regarded as an object is an object of the arrow
category ``Ar(C)``, built through that category's entry; ``Hom_C(A,B)`` read
as a category is the fibre of ``(dom, cod): Ar(C) -> C x C`` at ``(A, B)``.
In a 1-category its morphisms are squares whose two endpoint maps are
identities: commutativity then says that their two arrows are equal.  It is
therefore discrete, not the full arrow subcategory on these objects (which
also has squares with nonidentity endpoint endomorphisms).  A Mor category
reuses the arrow objects without inheriting all the squares between them.
"""

from __future__ import annotations

from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoricalArrow,
    object_level,
)


def _compose_operation_preserving_mor(left, right, fallback):
    """Compose arrows in their selected Mor family, or use the weaker Mor."""
    if right.codomain() is not left.domain():
        return NotImplemented
    category = left.parent().mor_family().base_category()
    if (
        right.parent() not in MorCategories()
        or right.domain() not in category
        or not right.parent().mor_family().base_category().is_subcategory(category)
    ):
        return fallback(right)
    return (
        left.parent()
        .mor_family()
        .Of(right.domain(), left.codomain())(lambda element: left(right(element)))
    )


from types import NotImplementedType
from typing import TYPE_CHECKING, Any

from sage.categories.category import Category
from sage.categories.category import JoinCategory as SageJoinCategory
from sage.categories.category_with_axiom import (
    CategoryWithAxiom as SageCategoryWithAxiom,
)
from sage.categories.homset import Hom as SageHom
from sage.categories.homset import Homset as SageHomset
from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.categories.objects import Objects as SageObjects
from sage.categories.sets_cat import Sets as SageSets
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.misc.lazy_attribute import lazy_attribute
from sage.structure.category_object import CategoryObject as SageCategoryObject
from sage.structure.dynamic_class import DynamicMetaclass, dynamic_class
from sage.structure.element import Element, parent
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoryPacketMethods,
    OwnedMor,
    _has_category_packet_surface,
    _underlying_set_mor,
)
from sage_extensions.categories.abstract_categories.objects import Objects
from sage_extensions.owned_category import (
    OwnedCategoryMixin,
    owned_category_join,
)
from sage_extensions.owned_category_bases import Category as OwnedCategoryBase
from sage_extensions.refine import (
    check_certifying_predicates,
    construction_scope,
    owned_parent_class,
    realize_owned_category,
    run_construction_hooks,
)
from sage_extensions.validation import validator

if TYPE_CHECKING:
    from collections.abc import Callable

    from sage_extensions.categories.sets.indexed_families import IndexedFamily
    from sage_extensions.lexicon.category_theory import ObjectOfCategory
    from sage_extensions.lexicon.set_theory import SetObject
    from sage_extensions.logic import Predicate


def _category_mor(
    category: Category | None,
    domain: Parent,
    codomain: Parent,
) -> FixedMorObject | SageHomset:
    r"""The complete selected Mor, including any defining arrow predicate.

    Mathematical admission uses this object's ``accepts`` operation via
    :func:`_category_accepts_morphism`. Category containment instead concerns
    its constructed arrow objects. Its private ``arrow_set`` may also
    represent maps outside a restricted Mor category, so membership in that
    parent alone is not admission to the selected category.
    """
    if _has_category_packet_surface(category):
        # Admission follows the category's public Mor selector.  Most owned
        # categories inherit the packet implementation, while constructions
        # such as G-objects and functor categories legitimately specialize
        # ``Mor`` for their represented object type.  Bypassing that selector
        # rebuilds the packet Mor against endpoints that may be wrappers for a
        # more specific representation.
        return category.Mor(domain, codomain)
    return SageHom(domain, codomain, category)


def _category_accepts_morphism(
    category: Category | None,
    domain: Parent,
    codomain: Parent,
    arrow: Morphism,
) -> bool:
    r"""Ask the selected Mor owner to admit an arrow with these endpoints.

    This is the shared admission adapter for functors and categorical
    constructions. An owned fixed Mor category distinguishes an arrow's
    defining datum from the object constructed on it: ``accepts`` admits
    that datum; ``in`` reads object placement. The native Sage-Mor boundary
    instead uses its element-membership operation. Neither route constructs
    a trial object or drops a selected restriction by asking ``arrow_set``.
    """
    selected = _category_mor(category, domain, codomain)
    match selected:
        case Category():
            return selected.accepts(arrow)
        case _:
            return arrow in selected


def _arrow_is_inherited_from_subcategory(target, arrow: Morphism) -> bool:
    r"""Return whether ``arrow`` lies in a stronger Mor category below ``target``.

    If ``D <= C``, every ``D``-morphism is definitionally a ``C``-morphism.
    A structured Mor parent may represent that stronger arrow by a different
    morphism class, so admission follows the Mor-category edge itself rather
    than reconstructing and re-verifying the same arrow in ``C``.
    """
    parent = arrow.parent()
    return (
        parent in MorCategories()
        and parent.domain_object() is target.domain_object()
        and parent.codomain_object() is target.codomain_object()
        and _declared_category_reaches(parent, target)
    )


def _category_mor_parent(
    category: Category | None,
    domain: Parent,
    codomain: Parent,
) -> SageHomset:
    r"""Return the declared Mor object for an explicitly selected category.

    Selecting ``C`` must not forget its structure: linear, algebra and equivariant maps are
    constructed by ``C``'s declared Mor family, not by the private
    function-map substrate. An enriched Mor is also a mathematical parent;
    its inherited parent-level ``Mor`` is not the Mor of that category.
    Native Sage categories retain their native Mor ingress.

    Use ``_category_mor`` for admission. This adapter provides the runtime
    parent required by Sage morphisms, and a restricted Mor need not contain
    every map represented by that parent.
    """
    selected = _category_mor(category, domain, codomain)
    match selected:
        case Category():
            return selected.arrow_set()
        case _:
            return selected


def _declared_category_reaches(category: Category, target: Category) -> bool:
    r"""Return whether ``target`` occurs in ``category``'s declared supergraph.

    Fixed Mor objects can be distinct runtime parents even when one is the
    inherited specialization of the other.  Sage's ``is_subcategory`` is not
    reliable for these mixed Category/Parent Mor objects, so selection follows
    the explicit immediate-supercategory graph by identity.
    """
    pending = [category]
    seen = set()
    while pending:
        current = pending.pop()
        if current is target:
            return True
        identity = id(current)
        if identity in seen:
            continue
        seen.add(identity)
        pending.extend(current.super_categories())
    return False


def _minimal_inherited_homs(candidates):
    r"""Discard inherited Mor objects strictly above another candidate.

    A join of object properties may reach the same arrow theory through several
    branches.  If one branch carries a genuinely stronger Mor object (for
    example commuting triangles between represented subobjects), that object is
    the Mor of the join; its ordinary underlying Mor is only a supercategory.
    Unrelated surviving candidates remain an ambiguity and are rejected by the
    caller.
    """
    return [
        candidate
        for candidate in candidates
        if not any(
            other is not candidate and _declared_category_reaches(other, candidate)
            for other in candidates
        )
    ]


def _packet_supercategories(category):
    r"""Return semantic supercategories participating in the owned packet graph.

    Sage categories in ``super_categories()`` are runtime substrates.  Their
    native Mor dispatch is endpoint-driven and can jump back into a stronger
    owned category, so transporting Mor/End/Aut packets through them creates
    cycles and, more importantly, the wrong semantic graph.

    These are *declared supercategories*.  Each supplies its own Mor family;
    an endpoint's default Mor does not choose that family.  In particular a
    subobject's inherited Mor comes from the declared category of the base
    object, not from rediscovering the subobject category through its
    inclusion.
    """
    return tuple(
        supercategory
        for supercategory in category.super_categories()
        if _has_category_packet_surface(supercategory)
    )


def _distinct_supercategories(categories) -> list:
    r"""Return ``categories`` without repeats, in order, compared by identity.

    Several packet supercategories of a base category may state no Mor theory
    of their own, and then their Mor families return the same inherited fixed
    Mor object.  Sage's ``_all_super_categories`` merges ``super_categories()``
    with ``C3_sorted_merge``, which fails on a repeated entry, so a fixed Mor
    states each supercategory once.
    """
    distinct = []
    for category in categories:
        if not any(category is seen for seen in distinct):
            distinct.append(category)
    return distinct


def _precomposable(second: Morphism, first) -> bool:
    r"""Whether ``first`` composes before ``second`` in ``second``'s Mor theory.

    The right operand of ``*`` is arbitrary, so this is the admission of the
    composition operator: ``first`` is an arrow of the same base category whose
    codomain is ``second``'s domain.  The arrow's own Mor is asked.
    """
    match first:
        case Morphism() | CategoricalArrow() if first.codomain() is second.domain():
            base = second.parent().base_category()
            return _category_accepts_morphism(
                base, first.domain(), first.codomain(), first
            )
        case _:
            return False


class MorArrowIdentity(CategoricalArrow, Element):
    r"""The identity 2-arrow on one arrow object."""

    def _call_(self, value):
        return value

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if parent(other) is self.parent():
            return True
        return NotImplemented

    def __ne__(self, other: object) -> bool | NotImplementedType:
        comparison = self.__eq__(other)
        return NotImplemented if comparison is NotImplemented else not comparison

    def __hash__(self) -> int:
        return hash(id(self.parent()))

    def __mul__(self, other):
        # The discrete 2-Mor on one arrow object holds its identity only, so
        # the composable arrows are exactly the elements of this parent.
        if other not in self.parent():
            return NotImplemented
        return self.parent().identity()


class _DiscreteTwoMorConstructions:
    r"""Universal constructions shared by fixed categories with only identity 2-morphisms."""

    def object_set(self) -> SetObject:
        r"""Return the represented arrows which are the objects of this fixed category."""
        return self.arrow_set()

    def objects(self) -> IndexedFamily:
        from sage_extensions.categories.sets.indexed_families import indexed_family

        arrows = self.object_set()
        return indexed_family(
            arrows,
            lambda arrow: arrow,
            name=f"Arrow objects of {self}",
        )

    def _require_discrete_two_morphisms(self) -> None:
        r"""State the hypothesis under which this fixed category is discrete."""
        if self._MorCategory is not _DiscreteTwoMorCategoryOf:
            raise TypeError(
                f"the fixed Mor category {self} has represented nonidentity 2-morphisms, so its universal "
                "constructions are not the discrete fixed-Mor construction"
            )

    @cached_method
    def arrows(self) -> IndexedFamily:
        r"""Return the object-indexed family of identity 2-morphisms on the discrete route."""
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.sets.indexed_families import indexed_family

        objects = self.objects()
        return indexed_family(
            self.object_set(),
            lambda arrow: self.identity_2(objects.value(arrow)),
            name=f"2-morphisms of {self}",
        )

    def product(self, factors):
        r"""Return the finite product when this fixed category has discrete 2-morphisms."""
        self._require_discrete_two_morphisms()
        return self._categorical_product_construction(factors).object()

    def coproduct(self, factors):
        r"""Return the finite coproduct when this fixed category has discrete 2-morphisms."""
        self._require_discrete_two_morphisms()
        return self._categorical_coproduct_construction(factors).object()

    def _categorical_product(self, left, right):
        return self.product((left, right))

    def _categorical_coproduct(self, left, right):
        return self.coproduct((left, right))

    def _categorical_product_construction(self, factors):
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.abstract_categories.products import (
            _discrete_product_construction,
        )

        return _discrete_product_construction(self, factors)

    def _categorical_coproduct_construction(self, factors):
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.abstract_categories.products import (
            _discrete_coproduct_construction,
        )

        return _discrete_coproduct_construction(self, factors)

    def _categorical_equalizer(self, left_morphism, right_morphism):
        return self._categorical_equalizer_construction(
            left_morphism,
            right_morphism,
        ).object()

    def _categorical_equalizer_construction(self, left_morphism, right_morphism):
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.abstract_categories.products import (
            _discrete_equalizer_construction,
        )

        return _discrete_equalizer_construction(self, left_morphism, right_morphism)

    def _categorical_coequalizer(self, left_morphism, right_morphism):
        return self._categorical_coequalizer_construction(
            left_morphism,
            right_morphism,
        ).object()

    def _categorical_coequalizer_construction(self, left_morphism, right_morphism):
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.abstract_categories.products import (
            _discrete_coequalizer_construction,
        )

        return _discrete_coequalizer_construction(self, left_morphism, right_morphism)

    def _categorical_equalizer_family(self, morphisms):
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.abstract_categories.products import (
            _nonempty_discrete_morphism_family_reference,
        )

        return _nonempty_discrete_morphism_family_reference(self, morphisms).domain()

    def _categorical_coequalizer_family(self, morphisms):
        self._require_discrete_two_morphisms()
        from sage_extensions.categories.abstract_categories.products import (
            _nonempty_discrete_morphism_family_reference,
        )

        return _nonempty_discrete_morphism_family_reference(self, morphisms).codomain()

    def _categorical_product_morphism(
        self,
        left_morphism,
        right_morphism,
        source,
        target,
    ):
        self._require_discrete_two_morphisms()
        return self.Mor(source, target).identity()

    _categorical_coproduct_morphism = _categorical_product_morphism


@cached_function(key=type)
def _mor_subcategory_class(mor: CategoricalMor | FixedMorCategory) -> type:
    r"""The subcategory class of the Mor objects of one concrete type.

    Sage's ``Category.subcategory_class`` builds it from the type's
    ``SubcategoryMethods`` and the ``subcategory_class`` of each category in
    ``_super_categories_for_classes``.  Each Mor-object class fixes that list
    by type (``CategoricalMor`` to Sage's ``Objects()``, ``FixedMorCategory``
    to the owned ``Objects()``), so the class is a function of the concrete
    type alone.
    """
    return mor._make_named_class(
        "subcategory_class", "SubcategoryMethods", cache=False, picklable=False
    )


def _init_mor_category_class(mor: CategoricalMor | FixedMorCategory) -> None:
    r"""Run the host ``Category`` initialization of a Mor object.

    The protected host-initialization protocol shared by the two roots of the
    Mor-object chains, ``CategoricalMor`` and ``FixedMorCategory``.  Each root
    calls it once from its own ``__init__``, after it has set
    ``_super_categories_for_classes``, in place of Sage's
    ``Category.__init__``; no other code calls it.

    Sage's ``Category.__init__`` (``sage/categories/category.py``) only sets
    ``__class__`` to ``dynamic_class("<type>_with_category", (type,
    subcategory_class))``, with ``subcategory_class`` built per instance and
    ``cache=False``.  A Mor object is constructed once per pair of endpoints,
    so that builds a new runtime class for every pair, and the cache of every
    class Sage and the owned realization build from it misses.  Each root
    declares ``subcategory_class`` as ``_mor_subcategory_class``, read here
    before the rewrite so the key is the root's concrete type, and Sage's
    ``dynamic_class`` cache then shares the rewritten class across the type.  The invariant: the
    runtime class of a Mor object is a function of its concrete type alone.
    """
    mor.__class__ = dynamic_class(
        f"{type(mor).__name__}_with_category",
        (type(mor), mor.subcategory_class),
        reduction=None,
        doccls=type(mor),
    )


def _attach_end_family(owner: CategoricalMor, family: _EndCategoryOf) -> None:
    if owner.domain_object() is not owner.codomain_object():
        raise ValueError(
            f"only End(X) = Mor(X, X) can be the endomorphism category of X, but {owner} has distinct objects"
        )
    category_owner = _category_packet(owner.base_category()).Ends()
    if family is not category_owner:
        represented = (
            _category_packet(family.base_category())
            .Mors()
            .Of(owner.domain_object(), owner.codomain_object())
        )
        if represented is not owner and represented.arrow_set() is not owner:
            raise ValueError(
                f"{family} already has {represented} as End({owner.domain_object()})"
            )
    if owner._end_family is not None and owner._end_family is not category_owner:
        raise ValueError(f"{owner} is already attached to another End family")
    owner._end_family = category_owner
    category_owner._remember_between(
        owner.domain_object(), owner.codomain_object(), owner
    )


def _attach_aut_family(owner: CategoricalMor, family: _AutCategoryOf) -> None:
    if owner.domain_object() is not owner.codomain_object():
        raise ValueError(
            f"only Iso(X, X) can be the automorphism category Aut(X), but {owner} has distinct objects"
        )
    category_owner = _category_packet(owner.base_category()).Auts()
    if family is not category_owner:
        represented = (
            _category_packet(family.base_category())
            .Isos()
            .Of(owner.domain_object(), owner.codomain_object())
        )
        if represented is not owner and represented.arrow_set() is not owner:
            raise ValueError(
                f"{family} already has {represented} as Aut({owner.domain_object()})"
            )
    if owner._aut_family is not None and owner._aut_family is not category_owner:
        raise ValueError(f"{owner} is already attached to another Aut family")
    owner._aut_family = category_owner
    category_owner._remember_between(
        owner.domain_object(), owner.codomain_object(), owner
    )


class _DeferredMorElementClass:
    r"""Initialization marker which carries no eager element operations."""


class CategoricalMor(
    _DiscreteTwoMorConstructions,
    OwnedCategoryMixin,
    CategoryPacketMethods,
    OwnedMor,
    Category,
):
    r"""A represented Mor object which is both a Sage Mor and a category.

    This mixed runtime parent deliberately retains Sage's raw ``Category`` base.
    Its ``Parent.category()`` records the Mor object's enrichment placement;
    replacing that parent role by ``OwnedCategoryObject`` would instead force
    ``category()`` to be ``Cat()`` and erase the represented Mor object structure.
    Pure category objects in this module use :class:`OwnedCategoryBase`; this
    one is the boundary where the two runtime roles genuinely coincide.

    This is the live counterpart of the archived owned Mor-category base.  It
    keeps Sage's hard requirement that every ``Morphism`` be parented by an
    actual ``Mor``, while also making that same parent the discrete category
    ``Hom_C(A,B)``.  Concrete categories subclass this and add enrichment to
    the *same object*.

    Host initialization protocol.  This class is the root of the Mor-object
    chain: it alone names the host bases ``Homset`` and ``Category``, so it
    alone runs their non-cooperative initialization, once, in ``__init__``.
    Subclasses construct through ``CategoricalMor.__init__`` and never call a
    host initializer themselves.

    - ``Category``: ``_init_mor_category_class`` replaces Sage's
      ``Category.__init__``.  The invariant: the runtime class is a function
      of the concrete type alone.
    - ``Homset``: Sage's ``Homset.__init__`` stores the endpoints and runs
      ``Parent.__init__`` once in ``Sets().Homsets()`` or
      ``Sets().Endsets()``.  ``_init_category_`` records the caller's
      placement, ``_mor_placement``, joined with that category.  The
      invariant: ``category()`` is the placement and ``homset_category()``
      is ``Sets()``.

    Construction calls ``validate_placement`` once with ``check=False``
    (``OWN-22``).
    """

    _mor_placement: Category

    def object_set(self):
        r"""The objects of this represented Mor are its actual elements."""
        return self

    class ElementMethods(Morphism):
        r"""Root runtime for arrows generated from the fixed-Mor category graph."""

        def Mor(self, codomain):
            return self.parent().two_mor(self, codomain)

        def arrow(self):
            return self

        def source_object(self):
            return self.domain()

        def target_object(self):
            return self.codomain()

        def arrow_category(self):
            return self.parent().base_category().ArrowCategory()

        def then(self, other):
            r"""Return ``other ∘ self`` for composable represented arrows."""
            if other.domain() is not self.codomain():
                raise ValueError(
                    f"cannot compose {self} and then {other}: the codomain {self.codomain()} of the first "
                    f"is not the domain {other.domain()} of the second"
                )
            return other * self

        def _transport_initialization_to_mor(self, mor):
            r"""Return cooperative constructor data for this arrow in ``mor``.

            The default lower-arrow representation is itself admissible as
            the datum of the same mathematical arrow with stronger structure.
            Representation owners whose constructor has a different shape
            override this protected protocol at that owner.
            """
            return (mor, self), {}

    # A Mor category compares as the category it is: by identity, through
    # Sage's ``WithEqualityById`` (``sage.misc.fast_methods``), which every
    # ``Category`` inherits.  ``OwnedMor`` precedes ``Category`` in the MRO, so
    # Sage ``Homset.__eq__`` (domain, codomain, placement) would otherwise make
    # distinct Mor categories between the same objects equal, and Sage's
    # ``C3_sorted_merge`` over ``_all_super_categories`` requires ``==`` to be
    # identity on categories.  The owning family interns each fixed Mor by
    # endpoint identity (``_MorCategoryOf._cached_between``).
    __eq__ = Category.__eq__
    __ne__ = Category.__ne__
    __hash__ = Category.__hash__

    @cached_method
    def _generated_arrow_type(self) -> type:
        r"""Return the arrow type generated from this Mor category's graph."""
        # Each level's ``__init__`` threads cooperatively to the levels it
        # declares, and only the set-map root runs Sage's non-cooperative
        # ``Morphism`` initialization.  So every Mor category precedes all of
        # its supercategories: the reverse postorder of the declared graph,
        # visited right to left so declaration order breaks ties.  A preorder
        # placed the root inside an algebra arrow, ahead of its module level,
        # whose datum then never existed.
        postorder = []
        visited = set()

        def arrow_supercategories(mor):
            fixed = mor.__dict__.get("_owned_graph_supercategories")
            return fixed if fixed is not None else mor._owned_direct_supercategories()

        def visit(mor):
            marker = id(mor)
            if marker in visited:
                return
            visited.add(marker)
            for super_category in reversed(arrow_supercategories(mor)):
                if isinstance(super_category, CategoricalMor):
                    visit(super_category)
            postorder.append(mor)

        visit(self)

        # A Mor class also supplies the arrow methods of its Python ancestors,
        # in their MRO order.  A provider precedes the next one its own class
        # lists, and every provider of a Mor category precedes each provider
        # that only a declared supercategory supplies.  Two Mor categories of
        # one class (an algebra Mor over two categories of algebras) supply
        # the same providers and add no order between them.  The providers
        # are then sorted topologically (Kahn, Comm. ACM 5 (1962) 558), ties
        # going to the first supplier in reverse postorder.
        providers_by_type = {}

        def own_providers(mor):
            mor_type = type(mor)
            known = providers_by_type.get(mor_type)
            if known is not None:
                return known
            found = []
            for ancestor in mor_type.__mro__:
                if ancestor is CategoricalMor:
                    break
                provider = ancestor.__dict__.get("ElementMethods")
                if isinstance(provider, type) and provider not in found:
                    found.append(provider)
            providers_by_type[mor_type] = tuple(found)
            return providers_by_type[mor_type]

        first_supplier = {}
        successors = {}
        for position, mor in enumerate(reversed(postorder)):
            own = own_providers(mor)
            for provider in own:
                first_supplier.setdefault(provider, position)
                successors.setdefault(provider, set())
            for earlier, later in zip(own, own[1:]):
                successors[earlier].add(later)
            for super_category in arrow_supercategories(mor):
                if not isinstance(super_category, CategoricalMor):
                    continue
                for later in own_providers(super_category):
                    if later not in own:
                        for earlier in own:
                            successors[earlier].add(later)
        predecessor_count = dict.fromkeys(successors, 0)
        for later_set in successors.values():
            for later in later_set:
                predecessor_count[later] += 1
        providers = []
        ready = [p for p, count in predecessor_count.items() if count == 0]
        while ready:
            ready.sort(key=first_supplier.__getitem__)
            provider = ready.pop(0)
            providers.append(provider)
            for later in successors[provider]:
                predecessor_count[later] -= 1
                if predecessor_count[later] == 0:
                    ready.append(later)
        assert len(providers) == len(successors), (
            f"the arrow providers of {self} have no order in which every Mor "
            "category precedes its supercategories"
        )

        bases = []
        for candidate in (
            *providers,
            self.category().element_class,
            CategoricalMor.ElementMethods,
        ):
            if any(
                candidate is known or issubclass(known, candidate) for known in bases
            ):
                continue
            bases = [known for known in bases if not issubclass(candidate, known)]
            bases.append(candidate)

        result = dynamic_class(
            f"{type(self).__name__}.ArrowType",
            tuple(bases),
            doccls=providers[0] if providers else CategoricalMor.ElementMethods,
        )
        self._configure_generated_arrow_operations(result)
        return result

    def _configure_generated_arrow_operations(self, element_class):
        r"""Apply Sage's deferred parent-operation dispatch to an arrow type."""
        previous = self.__dict__.get("element_class", None)
        self.__dict__["element_class"] = element_class
        try:
            if all(
                hasattr(self, name)
                for name in ("product", "product_from_element_class_mul")
            ) and hasattr(element_class, "_mul_parent"):
                from sage.categories.magmas import Magmas

                Magmas.ParentMethods.__init_extra__(self)
            if all(
                hasattr(self, name)
                for name in ("summation", "summation_from_element_class_add")
            ) and hasattr(element_class, "_add_parent"):
                from sage.categories.additive_magmas import AdditiveMagmas

                AdditiveMagmas.ParentMethods.__init_extra__(self)
        finally:
            if previous is None:
                self.__dict__.pop("element_class", None)
            else:
                self.__dict__["element_class"] = previous

    def _owned_direct_supercategories(self):
        r"""Retain this Mor's declared graph until an input is refined.

        A fixed Mor's graph is determined by its concrete Mor class, its
        endpoint placements, its base category, and its optional End/Aut role.
        Sage asks for that declared graph independently while initializing the
        arrow type and the category comparison graph.  Retain the first answer
        across those requests, but discard it whenever one of those defining
        runtime inputs changes.
        """
        state = self._owned_direct_supercategory_state()
        retained = self.__dict__.get("_owned_direct_supercategory_record")
        if retained is not None and retained[0] == state:
            return retained[1]
        result = tuple(self.super_categories())
        # Construction of the supergraph can refine an endpoint or attach a
        # diagonal role.  Record the post-construction state so that such a
        # change cannot validate the graph computed before it.
        self._owned_direct_supercategory_record = (
            self._owned_direct_supercategory_state(),
            result,
        )
        return result

    def _owned_direct_supercategory_state(self):
        r"""Return the mutable inputs to this fixed Mor's declared graph."""
        domain_category = self.domain_object().category()
        codomain_category = self.codomain_object().category()
        base_category = self.base_category()
        return (
            type(self),
            type(self.domain_object()),
            type(self.codomain_object()),
            domain_category,
            type(domain_category),
            codomain_category,
            type(codomain_category),
            base_category,
            type(base_category),
            base_category.__dict__.get("_set_of_super_categories"),
            self.end_family(),
            self.aut_family(),
        )

    @property
    def ObjectType(self) -> type:
        r"""Objects of this Mor category are its arrows."""
        return self.ElementType

    @property
    def ElementType(self) -> type:
        r"""The public arrow implementation type of this fixed Mor category."""
        if any(
            ancestor.__dict__.get("Element") is not None
            for ancestor in type(self).__mro__[
                : type(self).__mro__.index(CategoricalMor)
            ]
        ):
            return Parent.element_class.f(self)
        return self._generated_arrow_type()

    @lazy_attribute
    def element_class(self) -> type:
        r"""Sage's element spelling of the owned arrow type.

        A Mor class still declaring ``Element`` has not yet migrated onto the
        category-generated arrow chain and keeps Sage's legacy construction.
        Once it declares ``ElementMethods`` instead, the generated Hom element
        type is the actual runtime arrow class.  A lazy attribute, as Sage's
        ``Parent.element_class`` is: the generated arrow type includes the
        element class of the placement this Mor is constructed in.
        """
        if any(
            ancestor.__dict__.get("Element") is not None
            for ancestor in type(self).__mro__[
                : type(self).__mro__.index(CategoricalMor)
            ]
        ):
            return Parent.element_class.f(self)
        return self._generated_arrow_type()

    @staticmethod
    def __classcall__(cls, *arguments, **options):
        # ``Category`` is a UniqueRepresentation whose default classcall does
        # not include fixed Mor endpoints in the identity of this mixed
        # Mor/category object.  The owning Mor family already interns by
        # ``(domain,codomain)``, so bypass Category's cache here.  Subclasses
        # name their own construction data, so the signature stays open.
        return typecall(cls, *arguments, **options)

    def __init__(
        self,
        family: _MorCategoryOf,
        domain: Parent,
        codomain: Parent,
        *,
        category: Category | None = None,
    ) -> None:
        self._family = family
        self._end_family = None
        self._aut_family = None
        self._domain_object = domain
        self._codomain_object = codomain
        # The semantic Mor/End supertree is deliberately richer than the
        # method-provider hierarchy Sage should use to synthesize Python
        # classes for this mixed Mor/category parent.  Feeding fixed Mor
        # objects back into Sage's C3 category-class builder creates cycles as
        # soon as a super-Mor is refined (for example End_R(M) as a ring).
        # Packet/enrichment code transports the mathematical structure
        # explicitly, so the runtime method spine stays at Objects().
        self._super_categories_for_classes = [SageObjects()]
        _init_mor_category_class(self)
        # Host ``Homset`` initialization.  It stores the endpoints and runs
        # ``Parent.__init__`` once, in Sage's ``Sets`` Mor category, and
        # ``_init_category_`` records the placement over it.  A Mor object is
        # a set of arrows, so a caller that supplies no richer placement
        # places it in ``Sets()``.
        if category is None:
            from sage_extensions.categories.sets.set_categories import Sets

            category = Sets()
        self._mor_placement = category
        # Sage's additive-magma and magma initialization hooks inspect the
        # element class only to select parent-dispatched ``+`` and ``*``.  The
        # real arrow type is a derived value of the complete fixed-Mor graph;
        # expose a marker during host initialization and apply those two rules
        # when that type is first requested.
        self.__dict__["element_class"] = _DeferredMorElementClass
        try:
            SageHomset.__init__(self, domain, codomain, category=SageSets())
        finally:
            self.__dict__.pop("element_class", None)
        with construction_scope(self) as reached:
            realize_owned_category(self)
            run_construction_hooks(self, reached)
        self.validate_placement(check=False)

    @lazy_attribute
    def subcategory_class(self) -> type:
        r"""Sage's subcategory class, shared by every Mor of one concrete type."""
        return _mor_subcategory_class(self)

    def _init_category_(self, category: Category) -> None:
        r"""Record the placement over Sage's ``Sets`` Mor runtime class.

        The ``CategoryObject.__init__`` interception point that
        ``Parent.__init__`` (``sage/structure/parent.pyx``) calls with the
        category ``Homset.__init__`` passes it: ``Sets().Homsets()``, or
        ``Sets().Endsets()`` when ``A`` is ``B``.  ``Parent._init_category_``
        builds the host class from that category, so the host class is shared
        by every Mor of one concrete type; the owned methods of the placement
        are realized over it by ``realize_owned_category``.  The placement is
        recorded as the join of that category with the caller's placement.
        """
        Parent._init_category_(self, category)
        SageCategoryObject._init_category_(
            self, owned_category_join((category, self._mor_placement))
        )

    @validator
    def validate_placement(self) -> None:
        r"""Raise ``ValueError`` unless this Mor has each property its placement certifies.

        Construction places this Mor in the caller's category without asking
        whether it has the properties that category states (``OWN-22``).
        Each one is decided here from the Mor's data, through the certifying
        statement of the category that states it.
        """
        check_certifying_predicates(self, self.category(), self.homset_category())

    def _already_parented_arrow(self, candidate: Morphism) -> bool:
        r"""Whether ``candidate`` is already represented by this Mor theory."""
        return candidate.parent() is self or _arrow_is_inherited_from_subcategory(
            self, candidate
        )

    def __call__(self, *args, **kwargs):
        r"""Construct an arrow, preserving one already represented here.

        If ``D <= C``, a ``D``-arrow is already a ``C``-arrow.  Reading it in
        the weaker Mor must therefore preserve the arrow rather than
        reinterpret its object as generator images or presentation data.
        """
        return OwnedMor.__call__(self, *args, **kwargs)

    def mor_family(self) -> _MorCategoryOf:
        return self._family

    def is_endomorphism_set(self) -> bool:
        r"""Expose the MorCategories operation across the enriched-Mor runtime boundary."""
        return MorCategories.ParentMethods.is_endomorphism_set(self)

    @property
    def _MorCategory(self) -> type[_MorCategoryOf]:
        # The Mor objects and their family are mutually recursive types.
        # Resolve the family's declaration only after this module is loaded.
        return _DiscreteTwoMorCategoryOf

    def mor_category(self) -> Category:
        r"""Return the owned mathematical category whose Mor object this is.

        Sage's ``Mor`` initialization still uses ``Sets()`` only as the
        private runtime method spine.  The semantic Mor category is the base
        category of the owned Mor family.
        """
        return self.mor_family().base_category()

    def _repr_(self) -> str:
        r"""Name the category whose arrows these are, not the ``Sets`` runtime spine."""
        return (
            f"Set of Morphisms from {self.domain_object()} to {self.codomain_object()} "
            f"in {self.mor_category()}"
        )

    def identity_at(self, obj: Parent) -> Morphism:
        return self.mor_family().Of(obj, obj).arrow_set().identity()

    def attach_end_family(self, family: _EndCategoryOf) -> None:
        _attach_end_family(self, family)

    def end_family(self) -> _EndCategoryOf | None:
        return self._end_family

    def attach_aut_family(self, family: _AutCategoryOf) -> None:
        _attach_aut_family(self, family)

    def aut_family(self) -> _AutCategoryOf | None:
        return self._aut_family

    def identity_endomorphism(self) -> Morphism:
        if self.end_family() is None:
            raise ValueError(
                f"{self} is not the endomorphism category End(X) of an object, so it has no identity endomorphism"
            )
        identity = self.arrow_set().identity()
        return self(identity)

    one = identity_endomorphism

    def base_category(self) -> Category:
        return self.mor_family().base_category()

    def domain_object(self) -> ObjectOfCategory:
        return self._domain_object

    def codomain_object(self) -> ObjectOfCategory:
        return self._codomain_object

    def arrow_set(self) -> SetObject:
        return self

    underlying_mor = arrow_set

    def accepts(self, arrow: Morphism) -> bool:
        r"""Whether ``arrow`` is an arrow of this Mor category.

        An arrow placed here, or in the Mor of a subcategory with the same
        endpoints, is one.  Constructing a new arrow from its defining data
        is a separate operation: constructor failure is not a membership
        decision, and successful conversion does not place the input here.
        """
        if (
            arrow.domain() is not self.domain_object()
            or arrow.codomain() is not self.codomain_object()
        ):
            return False
        return self._already_parented_arrow(arrow)

    def _mor_endpoint(self, obj: Parent | Category | Morphism):
        return self(obj)

    def __contains__(self, candidate: Any) -> bool:
        r"""Read raw-map element membership separately from object placement.

        An enriched Mor can be a mathematical set of maps, whose owner may
        decide an exact element predicate (injectivity of a finite set map,
        for example). An arrow object is instead placed in a category; its
        underlying arrow is not reclassified by that element predicate.
        """
        match candidate:
            case Morphism() | CategoricalArrow():
                return self.accepts(candidate)
            case _:
                return Category.__contains__(self, candidate)

    def super_categories(self):
        supers = []
        base = self.base_category()
        for supercategory in _packet_supercategories(self.base_category()):
            domain, codomain = base._mor_endpoints_in_supercategory(
                supercategory,
                self.domain_object(),
                self.codomain_object(),
            )
            supers.append(
                self.mor_family().family_over(supercategory).Of(domain, codomain)
            )
            if self.end_family() is not None:
                supers.append(self.end_family().family_over(supercategory).Of(domain))
        return _distinct_supercategories(supers) or [Objects()]

    def two_mor(
        self,
        domain: Parent | Morphism,
        codomain: Parent | Morphism,
    ) -> CategoricalMor:
        return self.MorCategory().Of(domain, codomain)

    Mor = two_mor

    def identity_2(self, arrow: Morphism) -> Morphism:
        return self.two_mor(arrow, arrow).identity()


class MorArrowDiscreteMor(CategoricalMor):
    r"""The discrete 2-Mor between two arrow objects.

    The objects of a fixed Mor category are the arrows themselves, so this is
    the Mor object of that category: it is discrete because no 2-morphisms are
    represented.
    """

    Element = MorArrowIdentity

    def __init__(
        self,
        family: _DiscreteTwoMorCategoryOf,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(self, family, domain, codomain)

    def mor_category(self) -> Category:
        return self.base_category()

    def _emptiness_decision(self):
        return self.domain() is not self.codomain()

    def _cardinality_decision(self):
        from sage_extensions.categories.sets.cardinals import cardinal

        return cardinal(0 if self._emptiness_decision() else 1)

    def _element_constructor_(self, value=None):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the arrows {self.domain()} and {self.codomain()} are distinct, so there is no 2-morphism "
                "between them"
            )
        if value is not None:
            if parent(value) is not self:
                raise ValueError(
                    f"Mor({self.domain()}, {self.domain()}) contains only the identity 2-morphism, but got {value}"
                )
            return value
        return self.element_class(self)

    @object_level
    @cached_method
    def identity(self) -> MorArrowIdentity:
        return self()


class FixedMorCategory(
    _DiscreteTwoMorConstructions, CategoryPacketMethods, OwnedCategoryBase
):
    r"""The category ``Hom_C(A,B)`` of arrows with fixed endpoints.

    Its objects are the arrows ``A -> B`` themselves. Calling the category
    uses the arrow constructor; an arrow already in it is returned unchanged.

    Host initialization protocol.  This class is the root of the fixed-Mor
    category chain, and its ``__init__`` alone runs the host initialization
    of its owned category base, once.  It records the category ``Cat()``
    with ``_init_cat_object``, and ``_init_mor_category_class`` replaces
    Sage's ``Category.__init__``, so the runtime class is a function of the
    concrete type alone (``OWN-22``).  Subclasses construct through
    ``FixedMorCategory.__init__`` and never call a host initializer
    themselves.
    """

    @staticmethod
    def __classcall__(cls, family, domain, codomain):
        # The owning Mor-family already interns fixed categories by their
        # endpoint identities.  Sage ``Category``'s UniqueRepresentation cache
        # does not include those endpoints and can otherwise collapse
        # ``Hom_C(A,B)`` with a previously created ``Hom_C(A',B')``.
        return typecall(cls, family, domain, codomain)

    def __init__(
        self,
        family: _MorCategoryOf,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        self._family = family
        self._end_family = None
        self._aut_family = None
        self._domain_object = domain
        self._codomain_object = codomain
        # As for ``CategoricalMor``, semantic packet supercategories are
        # not Python implementation mixins.  In particular ``Iso_C(A,B)``
        # simultaneously lies over ``Hom_C``, ``Mono_C`` and ``Epi_C``; asking
        # Sage to synthesize one C3 class from those fixed categories creates
        # artificial MRO cycles.  Keep the runtime method spine at the owned
        # root instead, which realizes the host ``Parent`` for the objects a
        # fixed Mor category builds through its own entry (the functors of
        # ``[A, B]``), while ``super_categories`` states the mathematics.
        self._super_categories_for_classes = [Objects()]
        self._init_cat_object()
        _init_mor_category_class(self)

    @lazy_attribute
    def subcategory_class(self) -> type:
        r"""Sage's subcategory class, shared by every fixed Mor of one concrete type."""
        return _mor_subcategory_class(self)

    def category(self) -> Category:
        r"""A fixed Mor category is placed in ``MorCategories``, below ``Cat``."""
        return MorCategories()

    class ParentMethods:
        r"""An arrow, regarded as an object of one fixed Mor category."""

        def Mor(self, codomain):
            r"""Return the represented 2-Mor to ``codomain``.

            The fixed Mor itself owns which 2-morphisms are represented:
            ordinary fixed Mors are discrete, while specializations such as
            functor categories may declare genuine natural transformations.
            """
            return self.functor_category().Mor(self, codomain)

    def mor_family(self) -> _MorCategoryOf:
        return self._family

    @property
    def _MorCategory(self) -> type[_MorCategoryOf]:
        return _DiscreteTwoMorCategoryOf

    def attach_end_family(self, family: _EndCategoryOf) -> None:
        _attach_end_family(self, family)

    def end_family(self) -> _EndCategoryOf | None:
        return self._end_family

    def attach_aut_family(self, family: _AutCategoryOf) -> None:
        _attach_aut_family(self, family)

    def aut_family(self) -> _AutCategoryOf | None:
        return self._aut_family

    def identity_endomorphism(self) -> Morphism:
        if self.end_family() is None:
            raise ValueError(
                f"{self} is not the endomorphism category End(X) of an object, so it has no identity endomorphism"
            )
        return self(self.arrow_set().identity())

    one = identity_endomorphism

    def base_category(self) -> Category:
        return self.mor_family().base_category()

    def domain_object(self) -> ObjectOfCategory:
        return self._domain_object

    def codomain_object(self) -> ObjectOfCategory:
        return self._codomain_object

    def arrow_set(self) -> SetObject:
        r"""The substrate of a Mor with no more specific declared constructor.

        Only an unreduced root family constructs this class.  Re-entering the
        public category Mor here would ask that same family to construct
        itself.  Restrictions instead inherit the actual Mor object below.
        """
        if _has_category_packet_surface(self.base_category()):
            return _underlying_set_mor(self.domain_object(), self.codomain_object())
        return SageHom(
            self.domain_object(), self.codomain_object(), self.base_category()
        )

    underlying_mor = arrow_set

    def accepts(self, arrow: Morphism) -> bool:
        r"""Whether ``arrow`` is an arrow of this Mor category.

        An arrow of the selected Mor object, or of the Mor of a subcategory with
        the same endpoints, is one.  Inherited arrows retain their stronger
        mathematical parent; the category graph supplies this inclusion,
        not an attempted conversion through a possibly undecidable constructor.
        """
        if (
            arrow.domain() is not self.domain_object()
            or arrow.codomain() is not self.codomain_object()
        ):
            return False
        mor = self.arrow_set()
        return arrow.parent() is mor or _arrow_is_inherited_from_subcategory(
            self, arrow
        )

    def __call__(self, *data, **options):
        if (
            len(data) == 1
            and not options
            and isinstance(data[0], (Morphism, CategoricalArrow))
        ):
            if self.accepts(data[0]):
                return data[0]
            raise TypeError(
                f"{data[0]} is not an arrow of {self}; apply a functor between the categories"
            )
        return self.arrow_set()(*data, **options)

    def _mor_endpoint(self, obj: Parent | Category | Morphism):
        return self(obj)

    def __contains__(self, candidate: Any) -> bool:
        match candidate:
            case Morphism() | CategoricalArrow():
                return self.accepts(candidate)
            case _:
                return False

    def Mor(
        self,
        domain: Parent | Morphism,
        codomain: Parent | Morphism,
    ) -> CategoricalMor:
        return self.MorCategory().Of(domain, codomain)

    two_mor = Mor

    def identity_2(self, arrow: Parent | Morphism) -> Morphism:
        r"""The identity 2-arrow of ``arrow``, read through ``two_mor``.

        ``two_mor`` is this category's ``Mor`` between its objects.  When this
        Mor is also a group or a set, the name ``Mor`` on it resolves to the
        object-level ``X.Mor(Y)`` of that category (``ARC-07``), so the
        category-level construction is asked by ``two_mor``.
        """
        return self.two_mor(arrow, arrow).identity()

    @object_level
    def identity(self):
        if self.domain_object() is not self.codomain_object():
            raise ValueError(f"an identity needs equal endpoints, but got {self}")
        return self.arrow_set().identity()

    def super_categories(self):
        supers = []
        base = self.base_category()
        for supercategory in _packet_supercategories(self.base_category()):
            domain, codomain = base._mor_endpoints_in_supercategory(
                supercategory,
                self.domain_object(),
                self.codomain_object(),
            )
            supers.append(
                self.mor_family()
                .family_over(supercategory)
                .Of(
                    domain,
                    codomain,
                )
            )
            if self.end_family() is not None:
                supers.append(self.end_family().family_over(supercategory).Of(domain))
        return _distinct_supercategories(supers) or [Objects()]

    def _repr_(self) -> str:
        return (
            f"Mor_{self.base_category()}({self.domain_object()}, "
            f"{self.codomain_object()})"
        )


class FixedEndCategory(FixedMorCategory):
    r"""The category ``End_C(A)`` of endomorphisms of one object."""

    def _repr_(self) -> str:
        return f"End_{self.base_category()}({self.domain_object()})"


class FixedRestrictedMorCategory(FixedMorCategory):
    @cached_method
    def object_set(self) -> SetObject:
        r"""Return the subobject of the underlying Mor cut out by this restriction."""
        from sage_extensions.categories.sets.set_categories import Sets

        return Sets().condition_set(self.arrow_set(), self.accepts)

    def arrow_set(self) -> SetObject:
        r"""Return the existing ``Mor`` parent for these endpoints.

        A restricted Mor category classifies some arrows in the base
        category's already-existing Mor object.  It therefore reuses the
        endpoint Mor owned by the base category packet.
        """
        return (
            _category_packet(self.base_category())
            .Mors()
            .Of(self.domain_object(), self.codomain_object())
            .arrow_set()
        )

    underlying_mor = arrow_set

    def accepts(self, arrow: Morphism) -> bool:
        return super().accepts(arrow) and self.mor_family().accepts(arrow)

    def super_categories(self):
        base = (
            _category_packet(self.base_category())
            .Mors()
            .Of(self.domain_object(), self.codomain_object())
        )
        owner = self.base_category()
        inherited = [
            self.mor_family()
            .family_over(supercategory)
            .Of(
                *owner._mor_endpoints_in_supercategory(
                    supercategory,
                    self.domain_object(),
                    self.codomain_object(),
                )
            )
            for supercategory in _packet_supercategories(self.base_category())
        ]
        return _distinct_supercategories([base, *inherited])


class RestrictedMorCategoryParent(FixedRestrictedMorCategory):
    r"""A restricted Mor category that also carries independent enrichment.

    Its elements may be structured witnesses (for example derivations) whose
    actual categorical arrows live in :meth:`arrow_set`.  Unlike
    :class:`CategoricalMor`, this parent is therefore not itself a Mor
    and cannot become a second Mor for the same fixed endpoints.

    The owned category base already makes it a parent; what this level adds
    is the category its *elements* form (a set, a module, a group).  The
    class is fixed from that category before the object exists, so the
    owned levels of the category consume their construction data (the
    scalar ring of a module, the inclusion of a subobject) in the same
    cooperative ``__init__`` chain as this one, and the category is then
    recorded on the parent with no second class rewrite.
    """

    @staticmethod
    def __classcall__(cls, family, domain, codomain, *, category=None, **data):
        r"""Construct an object of ``category`` from the data its owned levels declare."""
        if category is None:
            from sage_extensions.categories.sets.set_categories import Sets

            category = Sets()
        return typecall(
            owned_parent_class(cls, category),
            family=family,
            domain=domain,
            codomain=codomain,
            category=category,
            **data,
        )

    def __init__(
        self,
        family: _RestrictedMorCategoryOf,
        domain: Parent,
        codomain: Parent,
        *,
        category: Category,
        base: Parent | None = None,
    ) -> None:
        # ``base`` is the scalar ring that a module level of ``category``
        # hands to the host parent.  That level already records it as its
        # own datum; as a fixed Mor category the object has no base, so the
        # chain ends here without one.
        FixedRestrictedMorCategory.__init__(self, family, domain, codomain)
        with construction_scope(self) as reached:
            SageCategoryObject._init_category_(self, category)
            realize_owned_category(self)
            run_construction_hooks(self, reached)

    def category(self) -> Category:
        r"""Return the independent enrichment carried by this parent.

        ``RestrictedMorCategoryParent`` has two roles: its restricted-Mor
        methods describe which arrows its elements represent, while as a Sage
        parent its elements may independently form a set, module, group, or
        another category selected by ``category=``.  The fixed-Mor base is an
        owned category object, whose inherited ``category()`` names its
        placement among Mor categories.  That answer would erase the
        enrichment recorded on the parent.  Read the latter here.
        """
        return Parent.category(self)

    def __call__(self, *args, **kwargs):
        r"""Construct an element through the independent Parent role.

        The fixed restricted-Mor category also has an explicit :meth:`object`
        operation for regarding an accepted underlying arrow as an object of
        the Mor category.  That categorical conversion must not replace this
        parent's ordinary element constructor: derivations, connections, and
        absolute-Galois automorphisms are structured elements specified by
        their own defining data.
        """
        return self._element_constructor_(*args, **kwargs)

    def __contains__(self, candidate: Any) -> bool:
        match candidate:
            case _ if parent(candidate) is self:
                return True
            case _:
                return Category.__contains__(self, candidate)


class CategoricalIsomorphism(CategoricalArrow, CategoricalMor.ElementMethods):
    r"""An isomorphism represented by mutually inverse arrows.

    The defining datum is the forward arrow ``f: X -> Y``; the inverse
    ``f^{-1}: Y -> X`` is determined by it.  It is supplied as a zero-argument
    computation, asked on the first request and cached (``OWN-22``): a known
    inverse is the constant computation, and a composite ``g f`` supplies
    ``f^{-1} g^{-1}`` without composing it at construction.
    """

    def __init__(
        self,
        parent: Parent,
        forward: Morphism,
        inverse_computation: Callable[[], Morphism],
        *,
        verify: bool = False,
    ) -> None:
        # The isomorphism is an arrow of the base category too: its element
        # class carries that category's arrow level after Sage's ``Map``.
        # Initialize that level from the forward arrow, by the transport
        # protocol every arrow owner supplies, so its data are established.
        args, options = forward._transport_initialization_to_mor(parent)
        super(Map, self).__init__(*args, **options)
        if (
            forward.domain() is not self.domain()
            or forward.codomain() is not self.codomain()
        ):
            raise ValueError(
                f"an isomorphism {self.domain()} -> {self.codomain()} needs a forward map "
                f"{self.domain()} -> {self.codomain()}, but {forward} is a map {forward.domain()} -> {forward.codomain()}"
            )
        self._forward = forward
        self._inverse_computation = inverse_computation
        self.validate_inverse_pair(check=verify)

    def forward(self) -> Morphism:
        return self._forward

    @cached_method
    def _inverse_morphism(self) -> Morphism:
        r"""The base inverse arrow ``Y -> X``, computed once (protected; ``OWN-05``).

        Owner: this isomorphism; callers: its own methods and those of its
        subclasses.  Any other caller asks ``inverse().forward()``.
        """
        inverse = self._inverse_computation()
        if (
            inverse.domain() is not self.codomain()
            or inverse.codomain() is not self.domain()
        ):
            raise ValueError(
                f"an isomorphism {self.domain()} -> {self.codomain()} needs an inverse map "
                f"{self.codomain()} -> {self.domain()}, but {inverse} is a map {inverse.domain()} -> {inverse.codomain()}"
            )
        return inverse

    def inverse(self) -> CategoricalIsomorphism:
        r"""The inverse isomorphism ``Y -> X``, an element of the core Mor from the codomain.

        It is one morphism: its forward arrow is the base inverse of this
        isomorphism and its inverse is this forward arrow.  On ``Aut(X)`` it
        is the group inverse.  The base arrow is ``inverse().forward()``.
        """
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            _isomorphism_from_known_inverse_pair,
        )

        return _isomorphism_from_known_inverse_pair(
            self._inverse_morphism(), self._forward
        )

    def __invert__(self) -> CategoricalIsomorphism:
        return self.inverse()

    def left_inverse_decision(self):
        composite = self._inverse_morphism() * self.forward()
        return composite == composite.parent().identity()

    def right_inverse_decision(self):
        composite = self.forward() * self._inverse_morphism()
        return composite == composite.parent().identity()

    def inverse_pair_decision(self):
        from sage_extensions.logic import conjunction

        return conjunction(
            (self.left_inverse_decision(), self.right_inverse_decision())
        )

    @validator
    def validate_inverse_pair(self):
        decision = self.inverse_pair_decision()
        if decision is False:
            raise ValueError(
                f"{self._inverse_morphism()} is not an inverse of {self.forward()}: at least one inverse equation fails"
            )
        return decision

    def __call__(self, element):
        return self.forward()(element)

    def _call_(self, element):
        return self.forward()(element)

    def __eq__(self, other: object) -> bool | Predicate:
        r"""Compare through the retained forward arrows of the core inclusion.

        An inverse is unique when it exists, so the forward arrows decide;
        neither inverse is computed.
        """
        if self is other:
            return True
        match other:
            case CategoricalIsomorphism():
                return self.forward() == other.forward()
            case Morphism() | CategoricalArrow() if other in self.forward().parent():
                return self.forward() == other
            case _:
                return False

    def __ne__(self, other: object) -> bool | Predicate:
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self) -> int:
        return hash(self.forward())

    def __mul__(self, other):
        r"""Compose with ``other``; a composite of isomorphisms is an element of the Iso Mor.

        For isomorphisms ``f: A -> B`` and ``g: B -> C`` the composite ``g f``
        has inverse ``f^{-1} g^{-1}``, so it is the isomorphism of
        ``Core(C).Mor(A, C)`` with forward arrow ``g f`` whose inverse is
        that composite, computed when it is first asked.  ``f`` may be any
        arrow of the core Mor, whatever type realizes it: its inverse is
        asked through ``f.inverse()``.  Composed with an arrow that is not an
        isomorphism, it is the composite of the forward arrow with that arrow.
        """
        if not _precomposable(self, other):
            return NotImplemented
        core = self.parent().mor_category().Core()
        if other not in core.Mor(other.domain(), self.domain()):
            return self.forward() * other
        return core.Mor(other.domain(), self.codomain())._from_inverse_computation(
            self.forward() * other.forward(),
            lambda: other.inverse().forward() * self._inverse_morphism(),
        )


class FixedIsoCategory(FixedRestrictedMorCategory):
    def accepts(self, arrow: Morphism) -> bool:
        r"""An arrow of ``Iso_C(A,B)`` is an isomorphism of ``C`` from ``A`` to ``B``.

        The core of ``C`` owns which arrows are represented isomorphisms, so
        its Mor decides.
        """
        if (
            arrow.domain() is not self.domain_object()
            or arrow.codomain() is not self.codomain_object()
        ):
            return False
        return arrow in self.base_category().Core().Mor(
            self.domain_object(), self.codomain_object()
        )

    def super_categories(self):
        packet = _category_packet(self.base_category())
        domain = self.domain_object()
        codomain = self.codomain_object()
        inherited = [
            self.mor_family().family_over(supercategory).Of(domain, codomain)
            for supercategory in _packet_supercategories(self.base_category())
        ]
        supers = [
            packet.Mors().Of(domain, codomain),
            packet.Monos().Of(domain, codomain),
            packet.Epis().Of(domain, codomain),
            *inherited,
        ]
        if self.aut_family() is not None:
            supers.append(packet.Ends().Of(domain))
            supers.extend(
                self.aut_family().family_over(supercategory).Of(domain)
                for supercategory in _packet_supercategories(self.base_category())
            )
        return _distinct_supercategories(supers)

    def identity_automorphism(self) -> CategoricalIsomorphism:
        if self.aut_family() is None:
            raise ValueError(
                f"{self} is not the automorphism category Aut(X) of an object, so it has no identity automorphism"
            )
        if self.domain_object() is not self.codomain_object():
            raise ValueError(
                f"the identity automorphism exists only on Aut(X), but {self} is "
                f"Iso({self.domain_object()}, {self.codomain_object()})"
            )
        obj = self.domain_object()
        return self.base_category().Core().Mor(obj, obj).identity()

    one = identity_automorphism

    def _repr_(self) -> str:
        if self.aut_family() is not None:
            return f"Aut_{self.base_category()}({self.domain_object()})"
        return (
            f"Iso_{self.base_category()}({self.domain_object()}, "
            f"{self.codomain_object()})"
        )


class FixedAutCategory(FixedIsoCategory):
    def super_categories(self):
        packet = _category_packet(self.base_category())
        obj = self.domain_object()
        inherited = [
            self.mor_family().family_over(supercategory).Of(obj)
            for supercategory in _packet_supercategories(self.base_category())
        ]
        return _distinct_supercategories(
            [packet.Ends().Of(obj), packet.Isos().Of(obj, obj), *inherited]
        )


class MorCategories(OwnedCategoryBase):
    r"""The category of represented fixed-endpoint Mor categories.

    Its objects are the categories ``Hom_C(A,B)``, each built by the ``Of``
    entry of the Mor family of its base category ``C``.
    """

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return [Cat()]

    def Mor(self, domain: Category, codomain: Category) -> Category:
        r"""Return the represented functor category between fixed-Mor categories.

        ``MorCategories`` is a full subcategory of ``Cat`` on represented Mor
        categories. Its arrows are therefore the actual functors and natural
        transformations of ``Cat``; constructing them through a raw generic
        Mor-family ingress records the unrepresented endpoints and breaks the
        identity-sensitive admission lookup. Normalize both endpoints through
        the owner before entering that canonical family.
        """
        from sage_extensions.categories.abstract_categories.cat import Cat

        cat = Cat()
        return cat.functor_mor(cat.object(domain), cat.object(codomain))

    def an_object(self) -> Category:
        r"""The Mor of the witness of the category of sets to itself."""
        from sage_extensions.categories.sets.set_categories import Sets

        witness = Sets().an_object()
        return Sets().Mor(witness, witness)

    class ParentMethods:
        def is_endomorphism_set(self) -> bool:
            r"""Whether this fixed Mor is End_C(A) = Hom_C(A,A)."""
            return self.domain_object() is self.codomain_object()

    def __contains__(self, candidate: Any) -> bool:
        r"""Whether ``candidate`` is a fixed Mor category.

        A fixed Mor category built over the owned category base records this
        placement as its ``category()``.  A Mor realized on Sage's ``Mor``,
        or a restricted Mor with independently enriched elements, has one
        ``category()`` slot holding that enrichment (a set, a module).  Its
        placement here is therefore recorded where it was made:
        by the family whose ``Of`` entry built it for its endpoints. Read
        that recorded construction; containment must not call ``Of`` again
        and select or construct another Mor as a side effect.
        """
        match candidate:
            case CategoricalMor() | RestrictedMorCategoryParent():
                return (
                    candidate.mor_family()._cached_between(
                        candidate.domain_object(), candidate.codomain_object()
                    )
                    is candidate
                )
            case _:
                return super().__contains__(candidate)


FixedMorObject = CategoricalMor | FixedMorCategory
FixedMorClass = type[CategoricalMor] | type[FixedMorCategory]


class CategoryPacket:
    r"""The coordinated ``C / Hom_C / End_C / Iso_C / Aut_C`` families of one category.

    Not a mathematical object: the six families are the values of six
    operations of ``C`` (``MorCategory()``, ``EndCategory()``, ...), and this
    is the memo that holds them so that each is built once.  It is interned
    by the identity of ``C`` in :func:`_category_packet`.
    """

    def __init__(self, category: Category) -> None:
        self._category = category
        # Family objects are deliberately lazy.  The End family has the Mor
        # family as a semantic supercategory, which Sage requests during End
        # initialization.  Eager construction would re-enter a half-built packet.
        # The packet object is interned first; each family can then safely ask
        # for its siblings during category initialization.
        self._homs = None
        self._ends = None
        self._monos = None
        self._epis = None
        self._isos = None
        self._auts = None

    def category(self) -> Category:
        return self._category

    C = category

    def Mors(self) -> _MorCategoryOf:
        if self._homs is None:
            self._homs = _declared_family(
                self.category(), "_MorCategory", _MorCategoryOf
            )
        return self._homs

    def Ends(self) -> _EndCategoryOf:
        if self._ends is None:
            self._ends = _declared_family(
                self.category(), "_EndCategory", _EndCategoryOf
            )
        return self._ends

    def Monos(self) -> _MonoCategoryOf:
        if self._monos is None:
            self._monos = _declared_family(
                self.category(), "_MonoCategory", _MonoCategoryOf
            )
        return self._monos

    def Epis(self) -> _EpiCategoryOf:
        if self._epis is None:
            self._epis = _declared_family(
                self.category(), "_EpiCategory", _EpiCategoryOf
            )
        return self._epis

    def Isos(self) -> _IsoCategoryOf:
        if self._isos is None:
            self._isos = _declared_family(
                self.category(), "_IsoCategory", _IsoCategoryOf
            )
        return self._isos

    def Auts(self) -> _AutCategoryOf:
        if self._auts is None:
            self._auts = _declared_family(
                self.category(), "_AutCategory", _AutCategoryOf
            )
        return self._auts

    def super_packets(self):
        from sage_extensions.categories.sets.finite_families import finite_family

        return finite_family(
            (
                _category_packet(category)
                for category in _packet_supercategories(self.category())
            ),
            name="Supercategory packets",
        )

    def __repr__(self) -> str:
        return f"Category packet of {self.category()}"


def _declared_construction(category, declaration_name):
    r"""Return the first packet-family declaration on the category MRO, if any.

    This reads the ``_MorCategory`` / ``_EndCategory`` / ... declarations a
    category class makes, the same way the owned root reads a category's
    ``ParentMethods`` declaration: off the declaring class graph, never off
    an instance.  This is the ``OWN-06`` runtime adapter for that declaration
    protocol: class/descriptor inspection here selects the implementation of
    a mathematical Mor construction already chosen by category placement; it
    does not infer mathematical structure from an owned object.
    """
    declaring = type(category)
    if declaring.__name__.endswith("_with_category"):
        declaring = declaring.__base__
    for ancestor in declaring.__mro__:
        construction = ancestor.__dict__.get(declaration_name)
        if isinstance(construction, property):
            # A recursive category construction may declare its family lazily.
            # Read only the explicit descriptor at its declaring owner, rather
            # than invoking Sage's dynamic category attribute fallback.
            construction = construction.__get__(category, declaring)
        if isinstance(construction, type):
            return construction
    return None


def _ambient_of(category: Category) -> Category:
    r"""Remove the axioms of ``category`` whose subcategories are full.

    An axiom is removed exactly when its subcategory is full, with the same
    arrows as its base: finite sets have the set maps, commutative algebras
    the algebra maps.  A data subcategory carries chosen structure and keeps
    its arrows, and so does an axiom subcategory that is not full (unital
    algebras, whose arrows preserve the unit).  An axiom class marks itself
    non-full by declaring its own ``_MorCategory``.  A join is taken
    component by component.

    ``OWN-06`` adapter of Sage's category runtime: a join is the class Sage
    builds for a meet of components, read here through its ``super_categories``,
    and an axiom category is read through ``base_category``.
    """
    match category:
        case SageJoinCategory():
            return owned_category_join(
                tuple(
                    _ambient_of(component) for component in category.super_categories()
                )
            )
        case SageCategoryWithAxiom() if (
            _declared_construction(category, "_MorCategory") is None
        ):
            return _ambient_of(category.base_category())
        case _:
            return category


def _declared_family(category, declaration_name, default):
    r"""Construct the packet family ``category`` declares, else ``default``."""
    construction = _declared_construction(category, declaration_name)
    return (default if construction is None else construction)(category)


@cached_function(key=lambda category: id(category))
def _category_packet(category: Category) -> CategoryPacket:
    r"""The packet attached to this exact category object.

    Unverified specimen: a Mor's native value comparison must not identify
    two categories whose endpoint parents are distinct::

        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: left = finite_ordered_set(("a", "b"))
        sage: right = finite_ordered_set(("a", "b"))
        sage: left == right and left is not right
        True
        sage: first, second = Sets().Mor(left, left), Sets().Mor(right, right)
        sage: first.category_packet().C() is first
        True
        sage: second.category_packet().C() is second
        True
        sage: first.category_packet().Mors().base_category() is first
        True
        sage: second.category_packet().Mors().base_category() is second
        True
        sage: first.category_packet() is not second.category_packet()
        True
    """
    return CategoryPacket(category)


class _MorCategoryOf(OwnedCategoryBase):
    r"""The family ``(A,B) |-> Hom_C(A,B)`` attached to one category ``C``.

    An object here is the exact category selected by ``Of``, not an arbitrary
    subcategory of it.  Restricting its arrows or changing their base theory
    need not select that same category, so neither operation declares an
    inclusion of the classifying families.  A property category may still
    reuse an individual fixed Mor literally; its constructor records that
    shared object in both families.
    """

    FixedCategoryClass = FixedMorCategory
    _declaration_name = "_MorCategory"

    @staticmethod
    @cached_function(key=lambda cls, base_category: (cls, id(base_category)))
    def __classcall__(cls, base_category):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category)
        # A category that declares its own Mor family has exactly one; naming
        # the generic family on it resolves to the declared one.
        declared = _declared_construction(base_category, cls._declaration_name)
        if declared is not None and not issubclass(cls, declared):
            return declared(base_category)
        # A fixed Mor is also a Mor whose native comparison may compare
        # its endpoints by value. The family is attached to the exact category,
        # not to another Mor with equal-but-distinct endpoint objects.
        return typecall(cls, base_category)

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        # Several owned Mor-family specializations choose a concrete fixed
        # Mor parent class from the endpoints.  Keep that endpoint cache on
        # the common family object rather than relying on Sage category
        # internals for it.
        self._objects = {}
        self._resolved_endpoint_categories = {}
        super().__init__()

    def _make_named_class_key(self, name):
        return id(self._base_category)

    def base_category(self) -> Category:
        return self._base_category

    def _mor_endpoint(self, obj):
        r"""Represent a fixed-Mor object at this family's own Mor boundary.

        Objects of this family are categories, and its arrows are the
        functors inherited from ``Cat``.  Use ``Cat``'s exact represented
        endpoint before the nested Mor family selects and caches its object.
        An already represented endpoint retains its identity and category
        datum.  The endpoints of ``self.Of(A, B)`` still enter through
        ``self.base_category()`` and keep that category's representation.
        """
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().object(obj)

    def family_over(self, category: Category) -> _MorCategoryOf:
        return _category_packet(category).Mors()

    def fixed_category_class(self) -> FixedMorClass:
        return self.FixedCategoryClass

    def fixed_category_class_for(
        self,
        domain: Parent,
        codomain: Parent,
    ) -> FixedMorClass:
        r"""Return the represented fixed Mor class for these endpoints."""
        return self.fixed_category_class()

    def _inherits_morphisms_from(self, supercategory, domain, codomain) -> bool:
        r"""Whether this family may reuse ``supercategory``'s object literally.

        The Mor family itself has nothing further to ask: the class of what it
        would build against the class of what it inherits already decides it.
        A family that carves its objects out of a Mor overrides this, because
        the carving is only the same when the Mor is.
        """
        return True

    def _cached_between(self, domain, codomain):
        r"""Return the exact cached fixed-endpoint object, if present.

        Endpoint identity is part of the mathematical type.  Hashing/equality of
        endpoints is deliberately irrelevant here and can itself re-enter Mor
        construction, so every Mor-family specialization shares this one
        identity-sensitive lookup.
        """
        cached = self._objects.get((id(domain), id(codomain)))
        if cached is None:
            return None
        return (
            cached
            if (
                cached.domain_object() is domain
                and cached.codomain_object() is codomain
            )
            else None
        )

    def _remember_between(self, domain, codomain, value):
        r"""Record this family's constructed fixed Mor, including literal reuse.

        All ``Of`` specializations finish here.  The canonical End/Aut role
        attachments use this same record when an inherited family constructs
        their shared object first.  Containment only reads the record; it
        neither populates it nor infers a different family from the endpoints.
        """
        self._objects[id(domain), id(codomain)] = value
        return value

    def an_object(self) -> Category:
        r"""The Mor of the base category's witness to itself."""
        witness = self.base_category().an_object()
        return self.Of(witness, witness)

    def super_categories(self):
        return [MorCategories()]

    def Of(self, domain: Parent, codomain: Parent) -> FixedMorObject:
        r"""Select the defining Mor object without losing inherited structure.

        This is the constructor entry for the objects of this family and the
        ``OWN-06`` private realization boundary, so the one place the runtime class a
        fixed Mor is realized by is compared:
        a property subcategory inherits the declaration of the category it
        refines and reuses the parent that category built.

        Unverified specimens: a property category shares its defining Mor;
        a restricted category shares the underlying Mor object, not its predicate::

            sage: from sage_extensions.categories.sets.set_categories import Sets, FiniteSets
            sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
            sage: points = finite_ordered_set(("a", "b"))
            sage: Mor = FiniteSets().category_packet().Mors().Of(points, points)
            sage: Mor is Sets().Mor(points, points)
            True
            sage: end = FiniteSets().category_packet().Ends().Of(points)
            sage: end is Mor and end.end_family() is Sets().category_packet().Ends()
            True
            sage: monos = Sets().category_packet().Monos().Of(points, points)
            sage: epis = Sets().category_packet().Epis().Of(points, points)
            sage: monos.arrow_set() is Mor and epis.arrow_set() is Mor
            True
            sage: constant = Mor(lambda point: "a")
            sage: constant in Mor, constant in monos, constant in epis
            (True, False, False)
            sage: swap = Mor(lambda point: "b" if point == "a" else "a")
            sage: swap in monos and swap in epis
            True
            sage: aut = FiniteSets().category_packet().Auts().Of(points)
            sage: aut is Sets().category_packet().Isos().Of(points, points)
            True
            sage: aut.aut_family() is Sets().category_packet().Auts()
            True
            sage: identity = Mor.identity_2(swap)
            sage: identity * identity == identity
            True
        """
        if _has_category_packet_surface(self.base_category()):
            domain = self.base_category()._mor_endpoint(domain)
            codomain = self.base_category()._mor_endpoint(codomain)
        # Endpoint identity, not a hash: hashing a Mor endpoint re-enters Mor
        # construction, so Sage's cached_method recurses here.  Endpoint or
        # category refinement may strengthen the represented fixed Mor.  Their
        # runtime classes are the inputs to every specialized
        # ``fixed_category_class_for``, so an unchanged tuple lets a resolved
        # parent return before selecting that class again.
        cached = self._cached_between(domain, codomain)
        endpoint_categories = (domain.category(), codomain.category())
        declared_supers = self.base_category()._set_of_super_categories
        runtime_classes = (
            type(self.base_category()),
            type(domain),
            type(codomain),
            type(endpoint_categories[0]),
            type(endpoint_categories[1]),
        )
        resolved = self._resolved_endpoint_categories.get((id(domain), id(codomain)))
        if resolved is not None:
            (
                previous_domain,
                previous_codomain,
                previous_supers,
                previous_runtime_classes,
                previous_result,
            ) = resolved
            if (
                previous_domain is endpoint_categories[0]
                and previous_codomain is endpoint_categories[1]
                and previous_supers is declared_supers
                and previous_runtime_classes == runtime_classes
                and previous_result is cached
            ):
                return cached
        fixed_class = self.fixed_category_class_for(domain, codomain)
        if domain not in self.base_category() or codomain not in self.base_category():
            raise TypeError(
                f"Mor(X, Y) in {self.base_category()} needs X and Y objects of it, but got {domain} and {codomain}"
            )
        # A family with its own fixed-Mor class cannot reuse an inherited
        # object unless an admitted supercategory builds that class (or a
        # specialization of it). Decide that from the declarations before
        # constructing every supercategory Mor merely to reject it. The
        # resulting object's ``super_categories`` still realizes the complete
        # mathematical graph when that graph is asked for.
        if fixed_class is not FixedMorCategory and not any(
            domain in supercategory
            and codomain in supercategory
            and self._inherits_morphisms_from(supercategory, domain, codomain)
            and issubclass(
                self.family_over(supercategory).fixed_category_class_for(
                    domain, codomain
                ),
                fixed_class,
            )
            for supercategory in _packet_supercategories(self.base_category())
        ):
            result = (
                cached
                if isinstance(cached, fixed_class) and cached.mor_family() is self
                else fixed_class(self, domain, codomain)
            )
            self._remember_between(domain, codomain, result)
            self._resolved_endpoint_categories[id(domain), id(codomain)] = (
                *endpoint_categories,
                declared_supers,
                runtime_classes,
                result,
            )
            return result
        # What decides whether this category needs a Mor parent of its own is
        # whether the Mor it would build differs from one it already inherits,
        # not whether a class was declared somewhere in its Python ancestry: a
        # property subcategory inherits the declaration of the category it
        # refines and would build exactly the parent that category built.  So
        # the supercategories are walked on construction and after endpoint
        # refinement, and a candidate survives when
        # this category states nothing stronger than the class it already is.
        inherited = []
        declared = []
        for supercategory in _packet_supercategories(self.base_category()):
            if not self._inherits_morphisms_from(supercategory, domain, codomain):
                continue
            # Some owned categories admit substrate objects by their own
            # mathematical recognition rule (Sets admits Sage set parents, for
            # example) without mutating those parents into every semantic
            # supercategory.  A Mor can only be inherited from a supercategory
            # when that supercategory actually admits both endpoints; otherwise
            # there is no fixed Mor object there to reuse.
            if domain not in supercategory or codomain not in supercategory:
                continue
            candidate = self.family_over(supercategory).Of(domain, codomain)
            if all(candidate is not known for known in declared):
                declared.append(candidate)
            if not (
                fixed_class is FixedMorCategory or isinstance(candidate, fixed_class)
            ):
                continue
            if all(candidate is not known for known in inherited):
                inherited.append(candidate)

        inherited = _minimal_inherited_homs(inherited)
        # A literal reuse is the Mor of this category only when it lies under
        # every Mor its supercategories give: a map of associative unital
        # algebras is a ring map, though a map of unital algebras is not.
        if len(inherited) == 1 and all(
            _declared_category_reaches(inherited[0], other) for other in declared
        ):
            # One inherited Mor of the class this category would have built:
            # the subcategory adds no morphisms, so reuse that object literally
            # rather than fabricating a second parent for the same maps.
            result = inherited[0]
        elif fixed_class is not FixedMorCategory:
            # This family states a Mor class of its own.  Nothing it inherits
            # is that class, or several inherited ones disagree; either way it
            # is not, for morphism purposes, a subcategory of any single one,
            # and it builds what it declared.
            result = (
                cached
                if isinstance(cached, fixed_class) and cached.mor_family() is self
                else fixed_class(self, domain, codomain)
            )
        elif inherited:
            raise TypeError(
                f"{self.base_category()} inherits two incompatible constructions of Mor(X, Y) from its "
                "supercategories, so it must state its own"
            )
        else:
            # No declared or inherited implementation remains.  The root
            # fixed category owns its private Mor object; the public Mor ingress
            # must not be called recursively while this object is constructed.
            result = (
                cached
                if isinstance(cached, fixed_class) and cached.mor_family() is self
                else fixed_class(self, domain, codomain)
            )
        self._remember_between(domain, codomain, result)
        # Store the categories read before construction: if construction
        # refined an endpoint, the next call must resolve the new declaration.
        self._resolved_endpoint_categories[id(domain), id(codomain)] = (
            *endpoint_categories,
            declared_supers,
            runtime_classes,
            result,
        )
        return result

    Between = Of

    def __contains__(self, candidate: Any) -> bool:
        r"""Read the fixed Mor selected at this family's construction entry.

        ``Of`` records both a newly constructed Mor and an inherited Mor that
        is reused literally.  Membership reads that same identity-sensitive
        record; it does not select a construction from the candidate's
        endpoints or implicitly pass to another base category.  An End or
        Aut attachment records its canonical owning family at attachment, so
        an inherited constructor need not be followed by an owner query.

        ``Cat.object(M)`` is the exact category ``M``; membership reads
        that category directly.
        """
        if candidate not in MorCategories():
            return False
        return (
            self._cached_between(candidate.domain_object(), candidate.codomain_object())
            is candidate
        )

    def _repr_(self) -> str:
        return f"Mor-category packet of {self.base_category()}"


class _DiscreteTwoMorCategoryOf(_MorCategoryOf):
    r"""The Mor family of a fixed Mor category with only identity 2-arrows.

    An object of the base is a represented arrow. Between identical arrow
    objects there is its identity; between distinct objects there is no arrow.
    The ordinary Mor-family cache owns both constructions.

    Unverified specimens: the explicit 2-Mor and the packet select one parent,
    and an ordinary identity functor can act on its actual identity arrow::

        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: from sage_extensions.categories.functors.core import IdentityFunctor
        sage: points = finite_ordered_set(("a", "b"))
        sage: Mor = Sets().Mor(points, points)
        sage: swap = Mor(lambda point: {"a": "b", "b": "a"}[point])
        sage: obj = Mor(swap)
        sage: two_mor = Mor.two_mor(swap, swap)
        sage: two_mor is Mor.MorCategory().Of(obj, obj)
        True
        sage: two_mor is Mor.category_packet().Mors().Between(swap, swap)
        True
        sage: two_mor is _category_mor_parent(Mor, obj, obj)
        True
        sage: identity = two_mor.identity()
        sage: IdentityFunctor(Mor)(identity) is identity
        True
        sage: identity * identity == identity
        True
        sage: monos = Sets().Mono(points, points)
        sage: two_mor is monos.Mor(swap, swap)
        True
        sage: monos.two_mor(swap, swap) is monos.category_packet().Mors().Of(obj, obj)
        True
        sage: Mor.two_mor(swap, Mor.identity()).identity()
        Traceback (most recent call last):
        ...
        ValueError: distinct arrows have no represented 2-morphism

    Unverified specimen for a Mor that also has a module structure::

        sage: from dzack_research.preamble.all import Modules, QQ
        sage: module = QQ.free_module(1)
        sage: linear_mor = Modules(QQ).Mor(module, module)
        sage: identity = linear_mor.identity()
        sage: obj = linear_mor(identity)
        sage: two_mor = linear_mor.two_mor(identity, identity)
        sage: _category_mor_parent(linear_mor, obj, obj) is two_mor
        True
        sage: IdentityFunctor(linear_mor)(two_mor.identity()) is two_mor.identity()
        True
    """

    FixedCategoryClass = MorArrowDiscreteMor


def _carves_the_same_mor(self, supercategory, domain, codomain) -> bool:
    r"""Whether this category and ``supercategory`` have one and the same Mor.

    The monomorphisms, epimorphisms and isomorphisms of a category are cut out
    of its Mor, so a subcategory inherits them exactly when it inherits the
    Mor they are cut from.  A category of Lie algebras and the modules under
    it agree on which linear maps are bijections and disagree on which maps
    are morphisms at all, so its automorphisms are its own.
    """
    if _declared_construction(
        self.base_category(), self._declaration_name
    ) is not _declared_construction(supercategory, self._declaration_name):
        # A declared restriction may change even when the underlying Mor
        # does not.  Do not replace that predicate by an ancestor's predicate
        # merely because both use FixedRestrictedMorCategory to represent it.
        return False
    return _category_packet(self.base_category()).Mors().Of(
        domain, codomain
    ) is _category_packet(supercategory).Mors().Of(domain, codomain)


class _EndCategoryOf(_MorCategoryOf):
    r"""The diagonal Mor family, with ``End_C(A) is Hom_C(A,A)``."""

    FixedCategoryClass = FixedEndCategory
    _declaration_name = "_EndCategory"

    def family_over(self, category: Category) -> _EndCategoryOf:
        return _category_packet(category).Ends()

    def super_categories(self):
        return [_category_packet(self.base_category()).Mors()]

    def an_object(self) -> Category:
        return self.Of(self.base_category().an_object())

    def Of(
        self,
        obj: Parent,
        codomain: Parent | None = None,
    ) -> FixedMorObject:
        if _has_category_packet_surface(self.base_category()):
            obj = self.base_category()._mor_endpoint(obj)
            if codomain is not None:
                codomain = self.base_category()._mor_endpoint(codomain)
        if codomain is not None and codomain is not obj:
            raise ValueError(
                f"End(X) = Mor(X, X) needs equal endpoints, but got {obj} and {codomain}"
            )
        if obj not in self.base_category():
            raise TypeError(
                f"End(X) in {self.base_category()} needs X an object of it, but {obj} is not one"
            )
        endomorphisms = _category_packet(self.base_category()).Mors().Of(obj, obj)
        # A Mor shared with the category above is the same set of morphisms, so
        # its endomorphisms are the same too and the End object is that one.
        # Its defining category owns the role regardless of which inherited
        # family is queried first.
        if endomorphisms.end_family() is None:
            endomorphisms.attach_end_family(
                _category_packet(endomorphisms.base_category()).Ends()
            )
        return self._remember_between(obj, obj, endomorphisms)

    def Between(self, domain: Parent, codomain: Parent) -> FixedMorObject:
        return self.Of(domain, codomain)

    def _repr_(self) -> str:
        return f"End-category packet of {self.base_category()}"


class _RestrictedMorCategoryOf(_MorCategoryOf):
    r"""A family of fixed-endpoint subcategories of an existing ``Mor``."""

    FixedCategoryClass = FixedRestrictedMorCategory

    _inherits_morphisms_from = _carves_the_same_mor

    @abstract_method
    def accepts(self, arrow: Morphism) -> bool:
        r"""Whether ``arrow`` belongs to this restricted Mor family."""

    def _accepts_by_placement(self, arrow: Morphism) -> bool:
        r"""Whether a stronger represented Mor already places ``arrow`` here.

        A restriction with no theory-specific decision procedure cannot infer
        its predicate from methods exposed by an arbitrary arrow.  What it can
        know is construction: an arrow parent which is this fixed restricted
        Mor, or a declared subcategory of it, already carries the restriction.
        Concrete theories such as sets may override :meth:`accepts` with a
        theorem-backed decision procedure for their own morphisms.
        """
        if (
            arrow.domain() not in self.base_category()
            or arrow.codomain() not in self.base_category()
        ):
            return False
        selected = self.Of(arrow.domain(), arrow.codomain())
        arrow_parent = arrow.parent()
        return arrow_parent is selected or (
            arrow_parent in MorCategories()
            and _declared_category_reaches(arrow_parent, selected)
        )


_RestrictedCategoryOf = _RestrictedMorCategoryOf


def _is_selected_identity_in(category, arrow):
    r"""Recognize a retained identity, including along category inclusions."""
    mor = arrow.parent()
    if (
        arrow.domain() is not arrow.codomain()
        or mor not in MorCategories()
        or arrow is not mor.identity()
        or arrow.domain() not in category
    ):
        return False
    selected = _category_packet(category).Mors().Of(arrow.domain(), arrow.codomain())
    return mor is selected or _declared_category_reaches(mor, selected)


class _MonoCategoryOf(_RestrictedMorCategoryOf):
    r"""Represented monomorphisms absent a stronger theory-specific decision.

    The generic family is placement-only.  It does not interpret an
    ``is_injective`` method as categorical monicity; categories such as sets
    that have a theorem identifying the two override :meth:`accepts` at their
    own declaration.
    """

    _declaration_name = "_MonoCategory"

    def family_over(self, category: Category) -> _MonoCategoryOf:
        return _category_packet(category).Monos()

    def accepts(self, arrow: Morphism) -> bool:
        return _is_selected_identity_in(
            self.base_category(), arrow
        ) or self._accepts_by_placement(arrow)


class _EpiCategoryOf(_RestrictedMorCategoryOf):
    r"""Represented epimorphisms absent a stronger theory-specific decision.

    An arbitrary ``is_surjective`` method is likewise not the definition of a
    categorical epimorphism.  Theory-specific declarations may supply their
    own exact admission rule.
    """

    _declaration_name = "_EpiCategory"

    def family_over(self, category: Category) -> _EpiCategoryOf:
        return _category_packet(category).Epis()

    def accepts(self, arrow: Morphism) -> bool:
        return _is_selected_identity_in(
            self.base_category(), arrow
        ) or self._accepts_by_placement(arrow)


class _IsoCategoryOf(_MorCategoryOf):
    FixedCategoryClass = FixedIsoCategory
    _declaration_name = "_IsoCategory"

    _inherits_morphisms_from = _carves_the_same_mor

    def family_over(self, category: Category) -> _IsoCategoryOf:
        return _category_packet(category).Isos()


class _AutCategoryOf(_IsoCategoryOf):
    r"""The diagonal Iso family, with ``Aut_C(A) is Iso_C(A,A)``."""

    FixedCategoryClass = FixedAutCategory
    _declaration_name = "_AutCategory"

    def family_over(self, category: Category) -> _AutCategoryOf:
        return _category_packet(category).Auts()

    def an_object(self) -> Category:
        return self.Of(self.base_category().an_object())

    def super_categories(self):
        return [_category_packet(self.base_category()).Isos()]

    def Of(
        self,
        obj: Parent,
        codomain: Parent | None = None,
    ) -> FixedMorObject:
        if _has_category_packet_surface(self.base_category()):
            obj = self.base_category()._mor_endpoint(obj)
            if codomain is not None:
                codomain = self.base_category()._mor_endpoint(codomain)
        if codomain is not None and codomain is not obj:
            raise ValueError(
                f"Aut(X) needs equal endpoints, but got {obj} and {codomain}"
            )
        if obj not in self.base_category():
            raise TypeError(
                f"Aut(X) in {self.base_category()} needs X an object of it, but {obj} is not one"
            )
        automorphisms = _category_packet(self.base_category()).Isos().Of(obj, obj)
        # As for End above: a shared Iso object has the same isomorphisms, so
        # the same automorphisms. Their defining category owns the role.
        if automorphisms.aut_family() is None:
            automorphisms.attach_aut_family(
                _category_packet(automorphisms.base_category()).Auts()
            )
        return self._remember_between(obj, obj, automorphisms)

    def Between(self, domain: Parent, codomain: Parent) -> FixedMorObject:
        return self.Of(domain, codomain)

    def _repr_(self) -> str:
        return f"Aut-category packet of {self.base_category()}"


class MorCategoryConstruction(_MorCategoryOf):
    pass


class EndCategoryConstruction(_EndCategoryOf):
    pass


class MonoCategoryConstruction(_MonoCategoryOf):
    pass


class EpiCategoryConstruction(_EpiCategoryOf):
    pass


class IsoCategoryConstruction(_IsoCategoryOf):
    pass


def AutCategoryConstruction(base_category: Category) -> _AutCategoryOf:
    r"""Return the canonical automorphism family of the supplied category.

    This compatibility spelling returns the packet's existing family
    (``CAT-22``). Its objects are the selected diagonal isomorphism categories
    ``Aut_C(X) = Iso_C(X, X)``, with the packet's one remembered population.
    """
    return _category_packet(base_category).Auts()


__all__ = [
    "AutCategoryConstruction",
    "CategoricalIsomorphism",
    "CategoricalMor",
    "CategoryPacketMethods",
    "EndCategoryConstruction",
    "EpiCategoryConstruction",
    "FixedAutCategory",
    "FixedEndCategory",
    "FixedIsoCategory",
    "FixedMorCategory",
    "IsoCategoryConstruction",
    "MonoCategoryConstruction",
    "MorArrowIdentity",
    "MorCategories",
    "MorCategoryConstruction",
    "RestrictedMorCategoryParent",
]
