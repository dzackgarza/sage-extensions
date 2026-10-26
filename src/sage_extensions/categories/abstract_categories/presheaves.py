r"""Presheaves, coverages, descent equalizers, and sheaves.

The category of presheaves on ``C`` with values in ``D`` is

.. MATH::

    \mathrm{Presh}(C, D) := [C^{\mathrm{op}}, D],

the functor category the tree already owns, reached from ``C`` by
``C.presheaves(D)`` (``D = Sets()`` when omitted).  No new category class is
introduced: ``C.presheaves(D)`` is ``Cat().Mor(C.opposite(), D)``, so a
presheaf is an object of a functor category and its morphisms are natural
transformations.  The value category is a parameter because that is what the
later passage to sheaves of modules, of algebras, and to stacks changes.

The construction is a bifunctor ``Cat^op x Cat -> Cat``.  It is stated on
``Cat`` by its two actions: on objects, ``Cat().presheaves(C, D)``; on
morphisms ``F: C' -> C`` and ``G: D -> D'``, ``Cat().presheaf_transport(F, G)``
is the functor ``[C^op, D] -> [C'^op, D']``, ``P |-> G o P o F^op`` on objects
and ``eta |-> G eta F^op`` on natural transformations.

The Yoneda embedding ``y: C -> Presh(C)`` sends ``X`` to the representable
presheaf ``Mor_C(-, X)`` and ``h: X -> Y`` to postcomposition with ``h``
(Mac Lane, *Categories for the Working Mathematician*, III.2; nLab,
*Yoneda embedding*).  It is what distinguishes ``[C^op, Set]`` from a category
of maps: its objects are functors, and ``y`` is a functor into it.

A covering family of ``U`` is a finite family of arrows ``U_i -> U`` with a
chosen overlap span ``U_i <- U_ij -> U_j`` for each pair, an object of
``CoveringFamilies(C)``.  A coverage selects, for each object, the families
that cover it; represented, that selection is a subcategory of
``CoveringFamilies(C)``, and the coverage is that subcategory.  For
``F: C^op -> D`` and a cover ``{U_i -> U}``, with ``D`` carrying the selected
finite products and equalizers used here, :class:`DescentEqualizer` retains
the canonical map

.. MATH::

    F(U) \longrightarrow
    \operatorname{Eq}\left(
      \prod_i F(U_i) \rightrightarrows \prod_{i<j} F(U_{ij})
    \right).

Sheafhood is represented by inverses to these canonical maps, not by a boolean
predicate.  Consequently :class:`Sheaves` is the full subcategory of the
presheaf category whose objects retain that descent data, while its morphisms
remain exactly natural transformations of the underlying presheaves.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from itertools import combinations

from sage.categories.category import Category
from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.parent import Parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalIsomorphism,
    CategoricalMor,
    MorCategoryConstruction,
    _category_mor_parent,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
)
from sage_extensions.categories.functors.core import (
    Functor,
    NaturalTransformation,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    finite_indexed_family,
)
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import Category as OwnedCategoryBase
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class _OppositeFunctor(Functor):
    r"""``F^op: C^op -> D^op``, the functor ``F`` read on the opposite categories."""

    def __init__(self, functor: Functor) -> None:
        self._functor = functor
        super().__init__(functor.domain().opposite(), functor.codomain().opposite())

    def original(self) -> Functor:
        return self._functor

    def _apply_object(self, obj: Parent) -> ObjectOfCategory:
        return self.codomain()(self.original()(obj.underlying_object()))

    def _apply_morphism(self, morphism: Map) -> Map:
        # An arrow op(A) -> op(B) of C^op is an arrow B -> A of C; its image
        # is F(B) -> F(A), read as the arrow op(F(A)) -> op(F(B)) of D^op.
        return self.codomain().Mor(self(morphism.domain()), self(morphism.codomain()))(
            self.original()(morphism.underlying_arrow())
        )

    def _repr_(self) -> str:
        return f"({self.original()})^op"


class _RepresentablePresheaf(Functor):
    r"""``Mor_C(-, X): C^op -> Set`` for one object ``X`` of ``C``."""

    def __init__(self, category: Category, representing_object: Parent) -> None:
        from sage_extensions.categories.sets.set_categories import Sets

        assert representing_object in category, (
            f"the representable presheaf Mor(-, X) on {category} needs X an object of {category}, but "
            f"{representing_object} is not one"
        )
        self._category = category
        self._representing_object = representing_object
        super().__init__(category.opposite(), Sets())

    def representing_object(self) -> ObjectOfCategory:
        return self._representing_object

    def _apply_object(self, obj: Parent) -> ObjectOfCategory:
        return self._category.Mor(obj.underlying_object(), self.representing_object())

    def _apply_morphism(self, morphism: Map) -> Map:
        r"""Precomposition: an arrow ``u: B -> A`` of ``C`` gives ``g |-> g o u``."""
        from sage_extensions.categories.sets.set_categories import Sets

        precompose = morphism.underlying_arrow()
        return Sets().Mor(self(morphism.domain()), self(morphism.codomain()))(
            lambda arrow: arrow * precompose
        )

    def _repr_(self) -> str:
        return f"Mor_{self._category}(-, {self.representing_object()})"


class _YonedaEmbedding(Functor):
    r"""``y: C -> [C^op, Set]``, ``X |-> Mor_C(-, X)``."""

    _faithful = True

    def __init__(self, category: Category) -> None:
        self._category = category
        super().__init__(category, category.presheaves())

    def _apply_object(self, obj: Parent) -> ObjectOfCategory:
        return self.codomain()(_RepresentablePresheaf(self._category, obj))

    def _apply_morphism(self, morphism: Map) -> Map:
        r"""Postcomposition with ``h: X -> Y``, natural in the argument."""
        from sage_extensions.categories.sets.set_categories import Sets

        source = self(morphism.domain())
        target = self(morphism.codomain())
        source_presheaf = source.functor()
        target_presheaf = target.functor()

        def component(obj):
            return Sets().Mor(source_presheaf(obj), target_presheaf(obj))(
                lambda arrow: morphism * arrow
            )

        return self.codomain().Mor(source, target)(
            NaturalTransformation(source_presheaf, target_presheaf, component)
        )

    def _repr_(self) -> str:
        return f"Yoneda embedding of {self._category}"


class _PresheafTransport(Functor):
    r"""``[C^op, D] -> [C'^op, D']`` along ``F: C' -> C`` and ``G: D -> D'``.

    This is the action of the presheaf bifunctor on a pair of arrows of
    ``Cat``: contravariant in the site through precomposition with ``F^op``,
    covariant in the values through postcomposition with ``G``.
    """

    def __init__(self, site_functor: Functor, value_functor: Functor) -> None:
        self._site_functor = site_functor
        self._value_functor = value_functor
        self._opposite_site_functor = _OppositeFunctor(site_functor)
        super().__init__(
            site_functor.codomain().presheaves(value_functor.domain()),
            site_functor.domain().presheaves(value_functor.codomain()),
        )

    def site_functor(self) -> Functor:
        return self._site_functor

    def value_functor(self) -> Functor:
        return self._value_functor

    def _transport_presheaf(self, presheaf: Functor) -> Functor:
        return self._opposite_site_functor.then(presheaf).then(self.value_functor())

    def _apply_object(self, obj: Parent) -> ObjectOfCategory:
        return self.codomain()(self._transport_presheaf(obj.functor()))

    def _apply_morphism(self, morphism: Map) -> Map:
        transformation = morphism.transformation()
        source = self._transport_presheaf(transformation.source())
        target = self._transport_presheaf(transformation.target())
        opposite_site = self._opposite_site_functor
        value = self.value_functor()

        def component(obj):
            return value(transformation.component(opposite_site(obj)))

        return self.codomain().Mor(self(morphism.domain()), self(morphism.codomain()))(
            NaturalTransformation(source, target, component)
        )

    def _repr_(self) -> str:
        return f"Presh({self.site_functor()}, {self.value_functor()})"


def _finite_family(values, *, name: str) -> IndexedFamily:
    r"""Normalize finite labelled data without discarding its index set."""

    match values:
        case IndexedFamily():
            if not values.cardinality().is_finite():
                raise TypeError(
                    f"{name} must be finite, but it is a family of cardinality {values.cardinality()}"
                )
            return values
        case Mapping():
            labels = finite_ordered_set(tuple(values))
            return finite_indexed_family(labels, lambda label: values[label], name=name)
    entries = tuple(values)
    labels = finite_ordered_set(range(len(entries)))
    return finite_indexed_family(
        labels,
        lambda label: entries[int(labels.ranking_map()(label))],
        name=name,
    )


def _family_on_index_set(index_set, values, *, name: str) -> IndexedFamily:
    r"""Read finite data on the exact supplied index set."""

    match values:
        case IndexedFamily():
            if values.cardinality() != index_set.cardinality():
                raise ValueError(
                    f"{name} must have one entry for each of the {index_set.cardinality()} elements of "
                    f"{index_set}, but it has {values.cardinality()}"
                )
            if set(values.index_set()) == set(index_set):
                return finite_indexed_family(index_set, values.__getitem__, name=name)
            return finite_indexed_family(
                index_set,
                lambda label: values[values.index_set()[int(index_set.ranking_map()(label))]],
                name=name,
            )
        case Mapping():
            if set(values) != set(index_set):
                raise ValueError(
                    f"{name} must be keyed by exactly the elements of {index_set}, but its keys are {set(values)}"
                )
            return finite_indexed_family(index_set, values.__getitem__, name=name)
    entries = tuple(values)
    if len(entries) != int(index_set.cardinality().finite_value()):
        raise ValueError(
            f"{name} must have one entry for each of the {index_set.cardinality()} elements of "
            f"{index_set}, but it has {len(entries)}"
        )
    ranking = index_set.ranking_map()
    return finite_indexed_family(
        index_set,
        lambda label: entries[int(ranking(label))],
        name=name,
    )


class _CoverPresentationDiagram(Functor):
    r"""The finite diagram in ``C`` underlying one represented cover presentation.

    The shape has one terminal vertex for the covered object, one vertex for
    each cover domain, and one vertex for each selected pairwise overlap.  Its
    nonidentity arrows are exactly overlap-to-member, member-to-target and the
    forced overlap-to-target composites.  It is thin, so the two routes from
    an overlap to the target are one arrow; functoriality is precisely the
    commuting condition checked by the covering-family entry.
    """

    def __init__(
        self,
        site: Category,
        target: Parent,
        members: IndexedFamily,
        overlaps: IndexedFamily,
    ) -> None:
        from sage_extensions.categories.abstract_categories.products import (
            PosetCategory,
        )

        self._target = target
        self._members = members
        self._overlaps = overlaps
        self._member_labels = tuple(members.index_set())
        self._pair_labels = tuple(overlaps.index_set())
        shape_labels = finite_ordered_set(
            (
                ("target", 0),
                *(("member", position) for position in range(len(self._member_labels))),
                *(("overlap", position) for position in range(len(self._pair_labels))),
            )
        )

        def precedes(left, right):
            if left == right:
                return True
            left_kind, left_position = left
            right_kind, right_position = right
            if right_kind == "target" and left_kind in {"member", "overlap"}:
                return True
            if left_kind != "overlap" or right_kind != "member":
                return False
            pair = self._pair_labels[int(left_position)]
            member = self._member_labels[int(right_position)]
            return member in pair

        self._shape = PosetCategory(shape_labels, le=precedes)
        super().__init__(self._shape, site)

    def _label(self, obj: Parent):
        return obj.value()

    def _member_index(self, position):
        return self._member_labels[int(position)]

    def _pair(self, position):
        return self._pair_labels[int(position)]

    def _apply_object(self, obj: Parent) -> ObjectOfCategory:
        kind, position = self._label(obj)
        match kind:
            case "target":
                return self._target
            case "member":
                return self._members[self._member_index(position)].domain()
            case "overlap":
                return self._overlaps[self._pair(position)].apex()
            case _:
                raise ValueError(
                    f"{obj} is not a vertex of the diagram of the covering family: it is neither the target, a "
                    f"member, nor an overlap (its kind is {kind!r})"
                )

    def _apply_morphism(self, morphism: Map) -> Map:
        source_kind, source_position = self._label(morphism.domain())
        target_kind, target_position = self._label(morphism.codomain())
        source_object = self(morphism.domain())
        target_object = self(morphism.codomain())
        if morphism.domain() is morphism.codomain():
            return _category_mor_parent(self.codomain(), source_object, source_object).identity()
        if source_kind == "member" and target_kind == "target":
            return self._members[self._member_index(source_position)]
        if source_kind == "overlap" and target_kind == "member":
            pair = self._pair(source_position)
            span = self._overlaps[pair]
            member = self._member_index(target_position)
            if member == pair[0]:
                return span.left_leg()
            if member == pair[1]:
                return span.right_leg()
        if source_kind == "overlap" and target_kind == "target":
            pair = self._pair(source_position)
            span = self._overlaps[pair]
            return self._members[pair[0]] * span.left_leg()
        raise ValueError(
            f"the diagram of the covering family has no arrow {morphism.domain()} -> {morphism.codomain()}"
        )


class CoveringFamilyMorphism(Morphism):
    r"""A comparison of represented covering families.

    For covers ``(U_i -> U)`` and ``(V_a -> V)`` in one category ``C``, a
    morphism from the latter to the former is a map ``V -> U``, a map
    ``a |-> i(a)`` of index sets, and arrows ``V_a -> U_{i(a)}`` whose
    triangles to the covered objects commute.  A refinement in the usual
    sense is the case where ``V = U`` and the target map is the identity
    (Stacks Project, Tag 00VI).

    The selected pairwise overlap spans carried by a cover are computational
    presentation data.  Concrete refinements such as finite affine atlases may
    impose additional compatibility with those spans in a subclass.
    """

    def __init__(self, parent, index_map, member_maps, *, target_map=None, check=False) -> None:
        Morphism.__init__(self, parent)
        source = self.domain()
        target = self.codomain()
        if source.site_category() is not target.site_category():
            raise ValueError(
                f"a morphism of covering families needs both families in one site, but {source} lies in "
                f"{source.site_category()} and {target} lies in {target.site_category()}"
            )
        site = source.site_category()
        self._index_map = _family_on_index_set(
            source.index_set(),
            index_map,
            name="Fine-to-coarse covering-family indices",
        ).map(
            target.index_set(),
            name="Fine-to-coarse covering-family indices",
        )
        self._member_maps = _family_on_index_set(
            source.index_set(),
            member_maps,
            name="Component maps of a covering-family comparison",
        )
        if target_map is None:
            if source.target() is not target.target():
                raise ValueError(
                    f"the covering families {source} and {target} cover different objects {source.target()} and "
                    f"{target.target()}, so a map between their targets must be given"
                )
            target_map = _category_mor_parent(site, source.target(), source.target()).identity()
        if target_map not in site.Mor(source.target(), target.target()):
            raise TypeError(
                f"the map of targets {target_map} is not a morphism {source.target()} -> {target.target()} of {site}"
            )
        self._target_map = target_map
        for label in source.index_set():
            coarse_label = self.index_map(label)
            component = self.component(label)
            fine_member = source.member(label)
            coarse_member = target.member(coarse_label)
            if component not in site.Mor(fine_member.domain(), coarse_member.domain()):
                raise TypeError(
                    f"the component {component} for {label} is not a morphism {fine_member.domain()} -> "
                    f"{coarse_member.domain()} of {site}"
                )
        if check:
            self.validate_triangles()

    def index_map(self, fine_index):
        return self._index_map[self.domain().index_set()(fine_index)]

    def component(self, fine_index):
        return self._member_maps[self.domain().index_set()(fine_index)]

    member_map = component

    def target_map(self):
        return self._target_map

    def triangle_decision(self, fine_index):
        source = self.domain()
        target = self.codomain()
        label = source.index_set()(fine_index)
        coarse_label = self.index_map(label)
        return (
            target.member(coarse_label) * self.component(label)
            == self.target_map() * source.member(label)
        )

    def triangles_decision(self):
        from sage_extensions.logic import conjunction

        return conjunction(
            self.triangle_decision(label) for label in self.domain().index_set()
        )

    def validate_triangles(self):
        decision = self.triangles_decision()
        if decision is False:
            raise ValueError(
                f"{self} is not a morphism of covering families: at least one component triangle does not commute"
            )
        return decision

    def __mul__(self, other):
        match other:
            case CoveringFamilyMorphism() if other.codomain() is self.domain():
                category = self.parent().base_category()
                return category.Mor(other.domain(), self.codomain())(
                    {
                        label: self.index_map(other.index_map(label))
                        for label in other.domain().index_set()
                    },
                    {
                        label: self.component(other.index_map(label)) * other.component(label)
                        for label in other.domain().index_set()
                    },
                    target_map=self.target_map() * other.target_map(),
                )
            case _:
                return NotImplemented

    def __eq__(self, other):
        from sage_extensions.logic import conjunction

        if not isinstance(other, CoveringFamilyMorphism) or other.parent() is not self.parent():
            return False
        return conjunction(
            (
                other.target_map() == self.target_map(),
                *(
                    equality
                    for label in self.domain().index_set()
                    for equality in (
                        other.index_map(label) == self.index_map(label),
                        other.component(label) == self.component(label),
                    )
                ),
            )
        )

    def __ne__(self, other):
        from sage_extensions.logic import negation

        return negation(self == other)


class CoveringFamilyMor(CategoricalMor):
    r"""Comparisons between two represented covering families."""

    Element = CoveringFamilyMorphism

    def _element_constructor_(self, index_map, member_maps=None, *, target_map=None, check=False):
        match index_map:
            case CoveringFamilyMorphism() if member_maps is None:
                if index_map.parent() is self:
                    return index_map
                raise TypeError(f"{index_map} belongs to another Mor; apply the functor between the categories")
        if member_maps is None:
            raise TypeError(
                f"a morphism of covering families {self.domain()} -> {self.codomain()} needs a component map "
                "for each member, but none were given"
            )
        return self.element_class(
            self,
            index_map,
            member_maps,
            target_map=target_map,
            check=check,
        )

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(U, U), but this is Mor({self.domain()}, {self.codomain()})"
            )
        cover = self.domain()
        site = cover.site_category()
        return self(
            {label: label for label in cover.index_set()},
            {
                label: _category_mor_parent(
                    site,
                    cover.member(label).domain(),
                    cover.member(label).domain(),
                ).identity()
                for label in cover.index_set()
            },
            target_map=_category_mor_parent(site, cover.target(), cover.target()).identity(),
        )


class CoveringFamilyMorCategoryConstruction(MorCategoryConstruction):
    r"""The Mor family of represented covering families."""

    def fixed_category_class(self):
        return CoveringFamilyMor


def _covering_family(category: Category, target: Parent, members, overlaps, *, _engine=None, **data):
    r"""The covering family of ``target`` by ``members`` in ``category``, a category of covering families.

    ``members`` are the cover arrows ``U_i -> U``; ``overlaps`` maps each pair
    of member labels to the span ``U_i <- U_ij -> U_j`` of the site, built by
    ``site.span``.  A pair given in the reverse order ``(j, i)`` carries the
    span ``U_j <- U_ij -> U_i``.  The family retains these typed overlap spans;
    their commutation equations are structural laws checked only on request.
    """
    site = category.site_category()
    if target not in site:
        raise TypeError(
            f"a covering family needs its target to be an object of the site {site}, but {target} is not one"
        )
    family = _finite_family(members, name="Cover arrows")
    if int(family.cardinality().finite_value()) == 0:
        raise ValueError(
            f"a covering family of {target} needs at least one member, but none was given"
        )
    for arrow in family:
        match arrow:
            case Morphism() | CategoricalArrow():
                pass
            case _:
                raise TypeError(
                    f"the members of a covering family of {target} are morphisms of {site}, but {arrow!r} is not a morphism"
                )
        if arrow.codomain() is not target or arrow.domain() not in site:
            raise ValueError(
                f"the member {arrow} of a covering family of {target} must be a morphism of {site} ending at "
                f"{target}, but it is a map {arrow.domain()} -> {arrow.codomain()}"
            )
        if arrow not in site.Mor(arrow.domain(), target):
            raise ValueError(
                f"the member {arrow} of a covering family of {target} is not a morphism of {site}"
            )

    ranking = family.index_set().ranking_map()
    expected_pairs = tuple(combinations(tuple(family.index_set()), 2))
    normalized = {}
    for raw_pair, span in dict(overlaps).items():
        left_index, right_index = raw_pair
        if span.target_category() is not site:
            raise ValueError(
                f"the overlap of the members {left_index} and {right_index} must be a span of {site}, "
                f"but it is {span}"
            )
        match ranking(left_index) < ranking(right_index):
            case True:
                normalized[left_index, right_index] = span
            case False:
                normalized[right_index, left_index] = site.span(span.right_leg(), span.left_leg())
    if set(normalized) != set(expected_pairs):
        raise ValueError(
            f"a covering family needs one overlap for each pair of members {expected_pairs}, but the "
            f"overlaps given are for {tuple(normalized)}"
        )

    spans = {}
    for pair in expected_pairs:
        span = normalized[pair]
        overlap_object, left_map, right_map = span.apex(), span.left_leg(), span.right_leg()
        left = family[pair[0]]
        right = family[pair[1]]
        if overlap_object not in site:
            raise TypeError(
                f"the overlap {overlap_object} of the members {left} and {right} is not an object of {site}"
            )
        if (
            left_map.domain() is not overlap_object
            or left_map.codomain() is not left.domain()
            or left_map not in site.Mor(overlap_object, left.domain())
        ):
            raise ValueError(
                f"the left map of the overlap {overlap_object} must be a morphism {overlap_object} -> "
                f"{left.domain()} of {site}, but it is {left_map}"
            )
        if (
            right_map.domain() is not overlap_object
            or right_map.codomain() is not right.domain()
            or right_map not in site.Mor(overlap_object, right.domain())
        ):
            raise ValueError(
                f"the right map of the overlap {overlap_object} must be a morphism {overlap_object} -> "
                f"{right.domain()} of {site}, but it is {right_map}"
            )
        spans[pair] = span
    overlap_family = finite_indexed_family(
        finite_ordered_set(expected_pairs),
        lambda pair: spans[pair],
        name="Pair overlaps of a covering family",
    )
    presentation = _CoverPresentationDiagram(site, target, family, overlap_family)
    from sage_extensions.categories.abstract_categories.arrow_categories import (
        SliceCategory,
    )

    # The family is its index category ``J`` with the presentation
    # ``J -> C``, an object of ``Cat/C``, together with the cover data.
    match _engine:
        case None:
            object_engine = None
        case (owner, object_engine, None) if owner is category:
            pass
        case _:
            raise TypeError(f"the private covering realization must serve {category}, got {_engine}")
    return SliceCategory(Cat(), Cat().object(site)).object(
        Cat().arrow(presentation),
        categories=(category,),
        _engine=object_engine,
        construction_data={
            "covered_object": target,
            "members": family,
            "overlaps": overlap_family,
            **data,
        },
    )


class CoveringFamilies(OwnedCategory):
    r"""Represented finite covering families in one category ``C``.

    An object is a finite family of arrows ``u_i: U_i -> U`` of ``C`` with a
    common target, together with a chosen overlap for each pair of indices:
    a span ``U_i <- U_ij -> U_j`` of ``C`` whose two composites with the cover
    arrows agree.  Forgetting which vertices are target/member/overlap leaves
    the finite presentation functor ``J -> C`` itself, hence an object of the
    slice ``Cat/C``.  Morphisms in this covering-family level are the
    cover comparisons/refinements above: an index map, component maps and a
    target map.  Every coverage, which selects some of these objects, builds them by
    :meth:`SubcategoryMethods.family`.

    Unverified specimen: the cover is literally placed over its presentation
    functor, not recognized afterwards from methods on an arbitrary object::

        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: C = CoveringFamilies(Sets())
        sage: cover = C.an_object()
        sage: cover in C and cover in C.presentation_category()
        True
        sage: cover.presentation().codomain() is Sets()
        True
        sage: C.Mor(cover, cover).identity().domain() is cover
        True

        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: points = finite_ordered_set(("a", "b"))
        sage: identity = Sets().Mor(points, points).identity()
        sage: covers = CoveringFamilies(Sets())
        sage: cover = covers.family(points, (identity,), {})
        sage: cover.presentation().codomain() is Sets()
        True
        sage: cover in covers.presentation_category()
        True
    """

    _MorCategory = CoveringFamilyMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, site_category: Category):
        return Category.__classcall__(cls, site_category)

    def __init__(self, site_category: Category) -> None:
        self._site_category = site_category
        super().__init__()

    def site_category(self) -> Category:
        return self._site_category

    def presentation_category(self):
        r"""The slice ``Cat/C`` containing the finite presentation diagrams."""
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            SliceCategory,
        )

        return SliceCategory(Cat(), Cat().object(self.site_category()))

    def super_categories(self):
        return [self.presentation_category()]

    def an_object(self):
        target = self.site_category().an_object()
        identity = _category_mor_parent(self.site_category(), target, target).identity()
        return self.family(target, (identity,), {})

    class ParentMethods:
        r"""A finite family ``{U_i -> U}`` with its chosen pairwise overlap spans."""

        def __init__(
            self,
            covered_object: Parent,
            members: IndexedFamily,
            overlaps: IndexedFamily,
            **rest,
        ) -> None:
            self._covered_object = covered_object
            self._members = members
            self._overlaps = overlaps
            super().__init__(**rest)

        def covering_family_category(self) -> Category:
            return self.category()

        def presentation(self) -> Functor:
            r"""The finite diagram ``J -> C`` carrying this cover presentation."""
            return self.arrow().functor()

        def site_category(self) -> Category:
            return self.category().site_category()

        def coverage(self) -> Category:
            r"""The coverage this family was built in: the category of covering families selecting it."""
            return self.category()

        def target(self):
            return self._covered_object

        covered_object = target

        def members(self) -> IndexedFamily:
            return self._members

        def member(self, index) -> Morphism:
            return self.members()[index]

        def index_set(self):
            return self.members().index_set()

        def pair_index_set(self):
            return self.overlaps().index_set()

        @cached_method
        def cech_site(self):
            r"""The labelled finite incidence site of this covering family.

            Its objects are the covered-object label ``()``, member labels
            ``(i,)``, and the selected pair labels ``(i,j)``. The geometric
            overlap spans remain data of the original cover; this site records
            their incidence for the pairwise descent equalizer. Incidence uses
            equality of labels and does not require them to be hashable.
            """
            from sage_extensions.categories.abstract_categories.products import (
                PosetCategory,
            )

            labels = [()]
            labels.extend((index,) for index in self.index_set())
            labels.extend(tuple(pair) for pair in self.pair_index_set())
            # A covering family's labels have a selected finite ranking.
            # Čech incidence is containment of their positions, not Python
            # tuple membership on potentially symbolic or unhashable labels.
            # The empty covered-object label is terminal in the incidence
            # order: every member and pair maps to the covered object.
            rank = self.index_set().ranking_map()
            return PosetCategory(
                finite_ordered_set(tuple(labels)),
                le=lambda finer, coarser: all(
                    any(rank(point) == rank(index) for point in finer)
                    for index in coarser
                ),
            )

        @cached_method
        def cech_covering_family(self):
            r"""The member arrows as the selected cover of :meth:`cech_site`."""
            site = self.cech_site()
            category = _CechCoveringFamilies(self)
            target = site(())
            members = finite_indexed_family(
                self.index_set(),
                lambda index: site.Mor(site((index,)), target).unique(),
                name="Čech cover arrows",
            )
            overlaps = {
                tuple(pair): site.span(
                    site.Mor(site(tuple(pair)), site((pair[0],))).unique(),
                    site.Mor(site(tuple(pair)), site((pair[1],))).unique(),
                )
                for pair in self.pair_index_set()
            }
            return category.family(target, members, overlaps)

        @cached_method
        def cech_coverage(self) -> Category:
            r"""The coverage selected by this cover's finite Čech family."""
            return Coverage(self.cech_site(), _CechCoveringFamilies(self))

        def overlap_span(self, left_index, right_index):
            r"""The overlap span ``U_i <- U_ij -> U_j`` of two members, in either order."""
            ranking = self.index_set().ranking_map()
            match ranking(left_index) < ranking(right_index):
                case True:
                    return self.overlaps()[left_index, right_index]
                case False:
                    span = self.overlaps()[right_index, left_index]
                    return self.site_category().span(span.right_leg(), span.left_leg())

        def overlaps(self) -> IndexedFamily:
            return self._overlaps

        def overlap_commutation_decision(self, left_index, right_index):
            span = self.overlap_span(left_index, right_index)
            left = self.member(left_index)
            right = self.member(right_index)
            return left * span.left_leg() == right * span.right_leg()

        def overlaps_commutation_decision(self):
            from sage_extensions.logic import conjunction

            return conjunction(
                self.overlap_commutation_decision(pair[0], pair[1])
                for pair in self.pair_index_set()
            )

        def validate_overlaps(self):
            decision = self.overlaps_commutation_decision()
            if decision is False:
                raise ValueError(
                    f"{self} is not a valid covering-family presentation: at least one chosen overlap does not commute"
                )
            return decision

        def _repr_(self) -> str:
            return f"Covering family of {self.target()}"

    class SubcategoryMethods:
        def family(self, target: Parent, members, overlaps, **data):
            r"""The covering family of ``target`` by ``members`` with the stated pairwise overlaps.

            The entry of every category of covering families: the family is
            built in this category.
            """
            return _covering_family(self, target, members, overlaps, **data)

        def sheaves(self, value_category: Category | None = None) -> Category:
            r"""``Sh(C, D)`` for the coverage this category of covering families selects."""
            if value_category is None:
                from sage_extensions.categories.sets.set_categories import Sets

                value_category = Sets()
            return Sheaves(self, value_category)

        def terminal_site_object(self) -> Parent:
            r"""A terminal object ``t`` of the site, where ``Gamma(F) = F(t)``.

            For a presheaf ``F: C^op -> D`` the global sections are the limit
            of ``F`` over ``C^op``; when ``C`` has a terminal object ``t``,
            ``t`` is initial in ``C^op`` and that limit is ``F(t)``.  A
            coverage whose site states its terminal object supplies it.
            """
            assert False, (
                f"terminal object of the site of {self}: not implemented, so global sections "
                "over it are the limit of the presheaf, which is not computed"
            )

    def _repr_(self) -> str:
        return f"Covering families in {self.site_category()}"


class _CechCoveringFamilies(OwnedCategoryBase):
    r"""The selected family coverage of one represented finite Cech diagram.

    A represented cover supplies its finite Cech site and the distinguished
    family of chart arrows on that site. This subcategory of
    :class:`CoveringFamilies` selects that family; its morphisms remain the
    covering-family comparison morphisms inherited from the common owner.
    """

    @staticmethod
    @cached_function(key=lambda cls, presentation: (cls, id(presentation)))
    def __classcall__(cls, presentation):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(presentation)
            case _:
                return typecall(cls, presentation)

    def __init__(self, presentation) -> None:
        self._presentation = presentation
        OwnedCategoryBase.__init__(self)

    def presentation(self):
        return self._presentation

    def site_category(self) -> Category:
        return self.presentation().cech_site()

    def super_categories(self):
        return [CoveringFamilies(self.site_category())]

    def an_object(self):
        return self.presentation().cech_covering_family()

    def _repr_object_names(self):
        return f"chosen Cech covering family of {self.presentation()}"


class TrivialCoveringFamilies(OwnedCategoryBase):
    r"""Singleton identity covers, the trivial coverage on ``C``."""

    @staticmethod
    @cached_function(key=lambda cls, site_category: (cls, id(site_category)))
    def __classcall__(cls, site_category: Category):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(site_category)
        return typecall(cls, site_category)

    def __init__(self, site_category: Category) -> None:
        self._site_category = site_category
        OwnedCategoryBase.__init__(self)

    def site_category(self) -> Category:
        return self._site_category

    def super_categories(self):
        return [CoveringFamilies(self.site_category())]

    @cached_method(key=lambda self, target: id(target))
    def family(self, target: Parent):
        r"""The singleton identity cover of ``target``, one for each target."""
        if target not in self.site_category():
            raise TypeError(
                f"the trivial cover of {target} needs {target} to be an object of the site "
                f"{self.site_category()}, but it is not"
            )
        identity = _category_mor_parent(self.site_category(), target, target).identity()
        return _covering_family(self, target, (identity,), {})

    def an_object(self):
        return self.family(self.site_category().an_object())

    def _repr_(self) -> str:
        return f"Trivial covering families in {self.site_category()}"


class OpenCoveringFamilies(OwnedCategoryBase):
    r"""Open covers ``{U_i -> U}`` in the site ``Open(X)`` of a topological space ``X``.

    The site is the poset category of the open subsets of ``X`` ordered by
    inclusion, and a family of opens covers ``U`` when its union is ``U``.
    ``Sh(X, D)`` is the full subcategory of ``[Open(X)^op, D]`` of the
    presheaves satisfying descent for these covers (Mathlib,
    ``Mathlib/Topology/Sheaves/Sheaf.lean``, ``TopCat.Sheaf C X``).  The
    whole space ``X`` is the terminal object of ``Open(X)``.
    """

    @staticmethod
    @cached_function(key=lambda cls, space: (cls, id(space)))
    def __classcall__(cls, space: Parent):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(space)
        return typecall(cls, space)

    def __init__(self, space: Parent) -> None:
        self._space = space
        OwnedCategoryBase.__init__(self)

    def space(self) -> Parent:
        return self._space

    def site_category(self) -> Category:
        return self.space().open_subsets_site()

    def super_categories(self):
        return [CoveringFamilies(self.site_category())]

    def whole_open(self) -> Parent:
        r"""``X`` as the terminal object of its open site.

        The topology retains its inclusion into the power set of its points.
        In particular an affine scheme uses the points of its prime spectrum.

        Unexecuted affine sections specimen (Stacks, Tag 01I8)::

            sage: from dzack_research.preamble.all import *
            sage: ring = QQ["x"]
            sage: line = AffineSchemes(QQ)(ring)
            sage: module = ring.free_module(1)
            sage: sheaf = QuasiCoherentSheaves(line).associated_sheaf(module)
            sage: whole = sheaf.descent_data().coverage().whole_open()
            sage: sheaf.sections(whole) is module
            True
            sage: site = sheaf.descent_data().coverage().site_category()
            sage: x = ring.algebra_generator("x")
            sage: basic = site(line.underlying_space().distinguished_open(x))
            sage: opposite = site.opposite()
            sage: arrow = opposite.Mor(opposite(whole), opposite(basic))(
            ....:     site.Mor(basic, whole).unique()
            ....: )
            sage: restriction = sheaf.open_sections_presheaf()(arrow)
            sage: localized = sheaf.sections(basic)
            sage: e = module.module_generator(0)
            sage: image = restriction(e)
            sage: image != localized.zero()
            True
            sage: localized.base_ring()(x).is_unit()
            True
            sage: restriction(module.scalar_multiple(x, e)) == localized.scalar_multiple(
            ....:     localized.base_ring()(x), image
            ....: )
            True
        """
        opens = self.site_category().object_set()
        power = opens.inclusion().codomain()
        return self.site_category()(power.top())

    terminal_site_object = whole_open

    @cached_method(key=lambda self, target: id(target))
    def family(self, target: Parent):
        r"""The singleton identity cover ``{U -> U}`` of an open ``U``."""
        identity = _category_mor_parent(self.site_category(), target, target).identity()
        return _covering_family(self, target, (identity,), {})

    def open_cover(self, target: Parent, opens):
        r"""The cover of the open ``target`` by a family of opens ``U_i`` with union ``target``.

        Domain: an object ``U`` of ``Open(X)`` and an indexed family of objects
        ``U_i`` of ``Open(X)`` with ``U_i <= U`` and union ``U``.  Codomain: the
        covering family ``{U_i -> U}`` with overlaps ``U_i <- U_i cap U_j -> U_j``.
        """
        assert False, (
            f"open cover of {target} in {self} with overlaps U_i cap U_j: not implemented"
        )

    def an_object(self):
        return self.family(self.whole_open())

    def _repr_(self) -> str:
        return f"Open covering families of {self.space()}"


def Coverage(site_category: Category, covering_families: Category) -> Category:
    r"""The coverage on ``site_category`` whose covers are the objects of ``covering_families``.

    A coverage selects the families that cover each object.  Represented,
    that selection is a subcategory of ``CoveringFamilies(site_category)``,
    whose objects are built in it, so the coverage is that subcategory and
    no family is admitted by an after-the-fact predicate or registry.
    """
    if not covering_families.is_subcategory(CoveringFamilies(site_category)):
        raise TypeError(
            f"a coverage on {site_category} is a subcategory of its covering families, but "
            f"{covering_families} is not one"
        )
    return covering_families


class DescentDataOnCover(OwnedCategoryBase):
    r"""Represented descent data relative to one covering family.

    This is the placement common to concrete descent theories: modules,
    algebras, or objects of another represented fibre theory may carry
    different local data and different Mor constructions, but they are all
    descent data on the same cover.  The concrete theory remains responsible
    for its transition maps, cocycle law, and morphisms; this category records
    the cover-relative mathematical placement instead of rediscovering it by
    inspecting the implementation class afterwards.

    The root ``Objects()`` declaration below is deliberate.  A descent datum
    in the sense of Definition 31.3 of ``mathematical-theory-foundations.md``
    is relative to a fibred category.  Module and algebra descent therefore
    have no stronger *same-object* common parent: forgetting to the family of
    local objects or to its Čech diagram changes the object and is a functor,
    not a supercategory declaration (``CAT-16``).  The cover itself has a
    genuine in-place presentation parent, ``Cat/C``, supplied by
    :class:`CoveringFamilies`; the fibre theory remains with each concrete
    descent category.
    """

    @staticmethod
    @cached_function(
        key=lambda cls, coverage, covering_family: (
            cls,
            id(coverage),
            id(covering_family),
        )
    )
    def __classcall__(cls, coverage: Category, covering_family):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(coverage, covering_family)
        return typecall(cls, coverage, covering_family)

    def __init__(self, coverage: Category, covering_family) -> None:
        if covering_family not in coverage:
            raise TypeError(
                f"descent data are defined for a covering family of {coverage}, but {covering_family} is not one"
            )
        self._coverage = coverage
        self._covering_family = covering_family
        OwnedCategoryBase.__init__(self)

    def coverage(self) -> Category:
        return self._coverage

    def covering_family(self):
        return self._covering_family

    cover = covering_family

    def super_categories(self):
        return [Objects()]

    def _repr_(self) -> str:
        return f"Descent data on {self.covering_family()}"


@cached_function(key=lambda site_category: id(site_category))
def trivial_coverage(site_category: Category) -> Category:
    r"""Return the trivial coverage consisting only of identity singleton covers."""

    return Coverage(site_category, TrivialCoveringFamilies(site_category))


def _presheaf_functor(presheaf) -> Functor:
    r"""The functor of a presheaf given as a functor or as an object of its functor category."""
    match presheaf:
        case Functor():
            return presheaf
        case _:
            return presheaf.functor()


def _opposite_arrow(site: Category, arrow: Morphism) -> Morphism:
    opposite = site.opposite()
    return opposite.Mor(
        opposite(arrow.codomain()),
        opposite(arrow.domain()),
    )(arrow)


def _identity_equalizer_construction(value_category: Category, obj: Parent):
    r"""The selected equalizer of ``id_obj`` with itself, without a backend."""

    from sage_extensions.categories.abstract_categories.products import (
        SelectedLimitConstruction,
        _parallel_pair_diagram,
    )

    identity = _category_mor_parent(value_category, obj, obj).identity()
    diagram = _parallel_pair_diagram(identity, identity, value_category)
    shape = diagram.domain()
    universal_cone = diagram.Cones().cone(
        obj,
        lambda _index: identity,
    )

    def factorizer(cone):
        return cone.structure_morphism(shape.source())

    return SelectedLimitConstruction(diagram, universal_cone, factorizer)


class DescentEqualizer(SageObject):
    r"""The canonical Čech equalizer comparison for one presheaf and cover.

    This is a retained construction record, not a second public category of
    equalizer outputs: the products and equalizer are selected universal
    constructions of the value category, and the comparison is an owned
    morphism between their owned objects.
    """

    def __init__(
        self,
        coverage: Category,
        presheaf,
        covering_family: Parent,
        *,
        equalizer_selector=None,
    ) -> None:
        self._coverage = coverage
        self._presheaf = _presheaf_functor(presheaf)
        self._covering_family = covering_family
        self._equalizer_selector = equalizer_selector
        if covering_family not in coverage:
            raise TypeError(
                f"descent is defined for a covering family of {coverage}, but {covering_family} is not one"
            )
        site = coverage.site_category()
        if self._presheaf.domain() != site.opposite():
            raise ValueError(
                f"descent along {covering_family} needs a presheaf on {site}, but {presheaf} is a functor on "
                f"{self._presheaf.domain()}, not on {site.opposite()}"
            )
        self._value_category = self._presheaf.codomain()
        self._build()

    def coverage(self) -> Category:
        return self._coverage

    def presheaf(self) -> Functor:
        return self._presheaf

    def covering_family(self):
        return self._covering_family

    cover = covering_family

    def value_category(self) -> Category:
        return self._value_category

    def _value(self, obj: Parent) -> ObjectOfCategory:
        return self.presheaf()(self.coverage().site_category().opposite()(obj))

    def _restriction(self, arrow: Morphism) -> Morphism:
        return self.presheaf()(_opposite_arrow(self.coverage().site_category(), arrow))

    def _build(self) -> None:
        cover = self.covering_family()
        values = finite_indexed_family(
            cover.index_set(),
            lambda index: self._value(cover.member(index).domain()),
            name="Presheaf values on a cover",
        )
        self._local_product = self.value_category().product_construction(values)
        local_diagram = self._local_product.diagram()
        local_product = self._local_product.object()

        global_value = self._value(cover.target())
        global_cone = local_diagram.Cones().cone(
            global_value,
            lambda index: self._restriction(cover.member(index.value())),
        )
        self._restriction_to_product = self._local_product.factor(global_cone).apex_map()

        pairs = tuple(cover.pair_index_set())
        if not pairs:
            identity = _category_mor_parent(
                self.value_category(), local_product, local_product
            ).identity()
            self._left = identity
            self._right = identity
            self._matching_product = None
        else:
            overlap_values = finite_indexed_family(
                cover.pair_index_set(),
                lambda pair: self._value(cover.overlap_span(*pair).apex()),
                name="Presheaf values on pair overlaps",
            )
            self._matching_product = self.value_category().product_construction(
                overlap_values
            )
            overlap_diagram = self._matching_product.diagram()

            def side_map(side: str):
                cone = overlap_diagram.Cones().cone(
                    local_product,
                    lambda index: self._overlap_leg(index.value(), side),
                )
                return self._matching_product.factor(cone).apex_map()

            self._left = side_map("left")
            self._right = side_map("right")
        if self._equalizer_selector is not None:
            self._equalizer = self._equalizer_selector(self)
        elif not pairs:
            self._equalizer = _identity_equalizer_construction(
                self.value_category(), local_product
            )
        else:
            self._equalizer = self.value_category().equalizer_construction(
                self._left,
                self._right,
            )

        equalizer_diagram = self._equalizer.diagram()
        shape = equalizer_diagram.domain()
        selected_inclusion = self._equalizer.structure_morphism(shape.source())
        if selected_inclusion is self._restriction_to_product:
            common = self._equalizer.structure_morphism(shape.target())
        else:
            common = self._left * self._restriction_to_product
            if (common == self._right * self._restriction_to_product) is not True:
                raise ValueError(
                    f"the restrictions of {self._presheaf} to the cover {self.covering_family()} do not form a "
                    "cone over the two Cech maps: the two composites differ"
                )
        global_equalizer_cone = equalizer_diagram.Cones().cone(
            global_value,
            lambda index: (
                self._restriction_to_product if index is shape.source() else common
            ),
        )
        if (
            global_value is self._equalizer.object()
            and selected_inclusion is self._restriction_to_product
        ):
            self._canonical_map = _category_mor_parent(
                self.value_category(), global_value, global_value
            ).identity()
            return
        self._canonical_map = self._equalizer.factor(global_equalizer_cone).apex_map()

    def _overlap_leg(self, pair, side: str) -> Morphism:
        cover = self.covering_family()
        left_index, right_index = pair
        overlap = cover.overlap_span(left_index, right_index)
        local_index = left_index if side == "left" else right_index
        overlap_map = overlap.left_leg() if side == "left" else overlap.right_leg()
        local_object = self._local_product.diagram().domain()(local_index)
        projection = self._local_product.structure_morphism(local_object)
        return self._restriction(overlap_map) * projection

    def local_product_construction(self):
        return self._local_product

    def restriction_to_product(self) -> Morphism:
        return self._restriction_to_product

    def matching_product_construction(self):
        return self._matching_product

    def parallel_maps(self):
        from sage_extensions.categories.sets.set_categories import Sets

        product = Sets().product((self._left.parent(), self._right.parent()))
        return product((self._left, self._right))

    def equalizer_construction(self):
        return self._equalizer

    def equalizer_object(self) -> ObjectOfCategory:
        return self.equalizer_construction().object()

    def canonical_map(self) -> Morphism:
        return self._canonical_map

    def comparison(self, inverse: Morphism) -> CategoricalIsomorphism:
        return self.value_category().Core().Mor(
            self.canonical_map().domain(),
            self.canonical_map().codomain(),
        )(self.canonical_map(), inverse)


class DescentEqualizerComparison(SageObject):
    r"""An actual isomorphism from ``F(U)`` to its selected descent equalizer.

    The record retains the Čech construction beside the already-owned
    :class:`CategoricalIsomorphism`; it does not classify a new kind of object.
    """

    def __init__(self, equalizer: DescentEqualizer, inverse: Morphism) -> None:
        self._equalizer = equalizer
        self._isomorphism = equalizer.comparison(inverse)

    def descent_equalizer(self) -> DescentEqualizer:
        return self._equalizer

    def covering_family(self):
        return self.descent_equalizer().covering_family()

    def presheaf(self) -> Functor:
        return self.descent_equalizer().presheaf()

    def isomorphism(self) -> CategoricalIsomorphism:
        return self._isomorphism

    comparison = isomorphism


class DescentData(SageObject):
    r"""Chosen equalizer-comparison data for every family of one coverage.

    ``inverse_for`` is proof data, not a predicate.  Given the canonical
    :class:`DescentEqualizer` for a represented cover it returns the inverse
    arrow to the canonical comparison.  The two inverse identities are then
    checked by :class:`CategoricalIsomorphism` when that cover is requested.
    Thus an unbounded coverage is represented by a rule for all of its covers,
    rather than by pretending they can be enumerated.

    This is selected proof/construction data carried by a sheaf object.  The
    sheaf itself is constructed by :class:`Sheaves`; no category of these
    retained records is introduced.

    Unverified separating specimen: the same presheaf fails descent for a
    two-member cover but has canonical descent data for the trivial coverage::

        sage: from sage_extensions.categories.abstract_categories.products import PosetCategory
        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: labels = finite_ordered_set(("U", "U0", "U1", "U01"))
        sage: relations = {("U0", "U"), ("U1", "U"), ("U01", "U0"), ("U01", "U1"), ("U01", "U")}
        sage: site = PosetCategory(labels, le=lambda left, right: left == right or (left, right) in relations)
        sage: families = CoveringFamilies(site)
        sage: cover = families.family(
        ....:     site("U"),
        ....:     (
        ....:         site.Mor(site("U0"), site("U")).unique(),
        ....:         site.Mor(site("U1"), site("U")).unique(),
        ....:     ),
        ....:     {(0, 1): (
        ....:         site("U01"),
        ....:         site.Mor(site("U01"), site("U0")).unique(),
        ....:         site.Mor(site("U01"), site("U1")).unique(),
        ....:     )},
        ....: )
        sage: coverage = Coverage(site, families)
        sage: coverage is families
        True
        sage: two = finite_ordered_set((0, 1)); one = finite_ordered_set((0,))
        sage: class FailingPresheaf(Functor):
        ....:     def __init__(self):
        ....:         super().__init__(site.opposite(), Sets())
        ....:     def _apply_object(self, obj):
        ....:         return two if obj.underlying_object() is site("U") else one
        ....:     def _apply_morphism(self, arrow):
        ....:         source, target = self(arrow.domain()), self(arrow.codomain())
        ....:         if source is target:
        ....:             return Sets().Mor(source, target).identity()
        ....:         return Sets().Mor(source, target)(lambda _point: target(0))
        sage: presheaf = FailingPresheaf()
        sage: bad = DescentData(
        ....:     coverage,
        ....:     presheaf,
        ....:     lambda equalizer: Sets().Mor(equalizer.equalizer_object(), two)(lambda _point: two(0)),
        ....: )
        sage: bad.comparison(cover)
        Traceback (most recent call last):
        ...
        ValueError: the supplied maps do not establish a left inverse
        sage: trivial = DescentData.trivial(presheaf)
        sage: identity_cover = trivial.coverage().family(site("U"))
        sage: trivial.comparison(identity_cover).isomorphism().domain() is two
        True
    """

    def __init__(
        self,
        coverage: Category,
        presheaf,
        inverse_for: Callable[[DescentEqualizer], Morphism | DescentEqualizerComparison],
        *,
        equalizer_for=None,
    ) -> None:
        self._coverage = coverage
        self._presheaf = _presheaf_functor(presheaf)
        self._inverse_for = inverse_for
        self._equalizer_for = equalizer_for
        if self._presheaf.domain() != coverage.site_category().opposite():
            raise ValueError(
                f"descent data for {coverage} need a presheaf on its site, but {presheaf} is a functor on "
                f"{self._presheaf.domain()}, not on {coverage.site_category().opposite()}"
            )

    @staticmethod
    def trivial(presheaf):
        r"""Return the canonical descent data for the trivial coverage.

        Every covering family in the trivial coverage is the singleton
        identity cover.  The presheaf value itself is selected as the
        equalizer object, with the canonical map into the one-factor product
        as its equalizer inclusion.  Hence the descent comparison is literally
        the identity even when equality of arbitrary maps in the value
        category is not decidable.
        """

        functor = _presheaf_functor(presheaf)
        site = functor.domain().base_category()
        coverage = trivial_coverage(site)

        def equalizer_for(equalizer: DescentEqualizer):
            from sage_extensions.categories.abstract_categories.products import (
                SelectedLimitConstruction,
                _parallel_pair_diagram,
            )

            cover = equalizer.covering_family()
            label = next(iter(cover.index_set()))
            product = equalizer.local_product_construction()
            index = product.diagram().domain()(label)
            projection = product.structure_morphism(index)
            inclusion = equalizer.restriction_to_product()
            left, right = equalizer.parallel_maps()
            diagram = _parallel_pair_diagram(
                left,
                right,
                equalizer.value_category(),
            )
            shape = diagram.domain()
            global_value = inclusion.domain()
            universal_cone = diagram.Cones().cone(
                global_value,
                lambda position: (
                    inclusion
                    if position is shape.source()
                    else left * inclusion
                ),
            )

            def factorizer(cone):
                return projection * cone.structure_morphism(shape.source())

            return SelectedLimitConstruction(diagram, universal_cone, factorizer)

        def inverse_for(equalizer: DescentEqualizer):
            global_value = equalizer.canonical_map().domain()
            return _category_mor_parent(
                equalizer.value_category(),
                global_value,
                global_value,
            ).identity()

        return DescentData(
            coverage,
            functor,
            inverse_for,
            equalizer_for=equalizer_for,
        )

    def coverage(self) -> Category:
        return self._coverage

    def presheaf(self) -> Functor:
        return self._presheaf

    def value_category(self) -> Category:
        return self.presheaf().codomain()

    @cached_method(key=lambda self, covering_family: id(covering_family))
    def comparison(self, covering_family: Parent) -> DescentEqualizerComparison:
        if covering_family not in self.coverage():
            raise TypeError(
                f"{covering_family} is not a covering family of the coverage {self.coverage()}"
            )
        equalizer = DescentEqualizer(
            self.coverage(),
            self.presheaf(),
            covering_family,
            equalizer_selector=self._equalizer_for,
        )
        selected = self._inverse_for(equalizer)
        match selected:
            case DescentEqualizerComparison():
                if (
                    selected.descent_equalizer().coverage() is not self.coverage()
                    or selected.presheaf() is not self.presheaf()
                    or selected.covering_family() is not covering_family
                ):
                    raise ValueError(
                        f"the descent comparison given for {covering_family} belongs to a different coverage, "
                        "presheaf, or covering family"
                    )
                comparison = selected
            case _:
                comparison = DescentEqualizerComparison(equalizer, selected)
        return comparison


class Sheaves(OwnedCategoryBase):
    r"""The full subcategory ``Sh(C,D)`` of presheaves satisfying descent.

    An object is a presheaf ``F: C^op -> D`` built with a descent datum for
    the coverage: an object of the presheaf category ``[C^op, D]``, threaded
    through that category's construction on the functor, with the descent
    datum as the one datum this level adds.  Its morphisms are the natural
    transformations of the presheaf category.
    """

    @staticmethod
    @cached_function(
        key=lambda cls, coverage, value_category: (
            cls,
            id(coverage),
            id(value_category),
        )
    )
    def __classcall__(cls, coverage: Category, value_category: Category):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(coverage, value_category)
        return typecall(cls, coverage, value_category)

    def __init__(self, coverage: Category, value_category: Category) -> None:
        self._coverage = coverage
        self._value_category = value_category
        OwnedCategoryBase.__init__(self)

    def coverage(self) -> Category:
        return self._coverage

    def site_category(self) -> Category:
        return self.coverage().site_category()

    def value_category(self) -> Category:
        return self._value_category

    def presheaf_category(self) -> Category:
        return self.site_category().presheaves(self.value_category())

    def super_categories(self):
        return [Cat().Mor(self.site_category().opposite(), self.value_category())]

    class ParentMethods:
        r"""A presheaf with its chosen descent datum for the coverage."""

        def __init__(
            self,
            descent_data: DescentData,
            fixed_mor_category: Category,
            **rest,
        ) -> None:
            self._descent_data = descent_data
            self._fixed_mor_category = fixed_mor_category
            super().__init__(**rest)

        def descent_data(self) -> DescentData:
            return self._descent_data

        def sections(self, site_object: Parent) -> Parent:
            r"""``Gamma(U, F) = F(U)``, an object of the value category ``D``.

            Domain: an object ``U`` of the site ``C``.  ``Gamma(U, -)`` is
            evaluation at ``U``, read in ``C^op``, on the functor category
            ``[C^op, D]``, restricted to this full subcategory of sheaves.
            """
            coverage = self.descent_data().coverage()
            site_opposite = coverage.site_category().opposite()
            evaluation = self.functor_category().evaluation_functor(site_opposite(site_object))
            return evaluation(self)

        def global_sections(self) -> Parent:
            r"""``Gamma(F)``, the limit of ``F: C^op -> D``, an object of ``D``.

            When the site ``C`` has a terminal object ``t``, ``t`` is initial
            in ``C^op`` and the limit is ``F(t)``, so ``Gamma(F)`` is the
            sections over the terminal object the coverage supplies.  For a
            space ``X`` with site ``Open(X)`` this is ``F(X)`` (Mathlib,
            ``TopCat.Sheaf``, ``Mathlib/Topology/Sheaves/Sheaf.lean``).
            """
            return self.sections(self.descent_data().coverage().terminal_site_object())

        def _repr_(self) -> str:
            return f"Sheaf object ({self.functor()})"

    def object(
        self,
        presheaf,
        descent_data: DescentData,
        *,
        categories=(),
        construction_data=None,
        _engine=None,
    ):
        r"""The sheaf on ``presheaf`` with ``descent_data``: this category's one entry."""
        functor = _presheaf_functor(presheaf)
        if functor.domain() != self.site_category().opposite():
            raise ValueError(
                f"a sheaf in {self} needs a presheaf on {self.site_category()}, but {presheaf} is a functor on "
                f"{functor.domain()}"
            )
        if functor.codomain() != self.value_category():
            raise ValueError(
                f"a sheaf in {self} needs a presheaf with values in {self.value_category()}, but {presheaf} "
                f"takes values in {functor.codomain()}"
            )
        if descent_data.coverage() is not self.coverage():
            raise ValueError(
                f"the descent data {descent_data} belong to the coverage {descent_data.coverage()}, not to "
                f"{self.coverage()}"
            )
        if descent_data.presheaf() is not functor:
            raise ValueError(
                f"the descent data {descent_data} belong to the presheaf {descent_data.presheaf()}, not to {presheaf}"
            )
        if categories or construction_data is not None or _engine is not None:
            data = dict(construction_data or {})
            return functor._with_structure(
                (self, *tuple(categories)),
                {
                    "descent_data": descent_data,
                    "fixed_mor_category": self,
                    **data,
                },
                engine=_engine,
            )
        return self._object_on(functor, descent_data)

    @cached_method(key=lambda self, functor, descent_data: (id(functor), id(descent_data)))
    def _object_on(self, functor: Functor, descent_data: DescentData):
        return functor._with_structure(
            (self,),
            {
                "descent_data": descent_data,
                "fixed_mor_category": self,
            },
        )

    __call__ = object

    def Mor(self, domain: Parent, codomain: Parent):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two sheaves in it, but got {domain} and {codomain}"
            )
        return self.presheaf_category().Mor(domain, codomain)

    def identity(self, obj: Parent):
        return self.Mor(obj, obj).identity()

    def sections_functor(self, site_object: Parent) -> Functor:
        r"""``Gamma(U, -): Sh(C, D) -> D``, for an object ``U`` of the site ``C``.

        The inclusion ``Sh(C, D) -> [C^op, D]`` followed by evaluation at
        ``U`` read in ``C^op``.
        """
        presheaves = self.presheaf_category()
        evaluation = presheaves.evaluation_functor(self.site_category().opposite()(site_object))
        return self.inclusion_into(presheaves).then(evaluation)

    def global_sections_functor(self) -> Functor:
        r"""``Gamma: Sh(C, D) -> D``, sections over the terminal object of the site."""
        return self.sections_functor(self.coverage().terminal_site_object())

    def extension_from_basis(self, space: Parent) -> Functor:
        r"""``Sh(B, D) -> Sh(Open(X), D)``, extension of sheaves from a basis.

        Hypotheses: the site ``B`` of this category is a basis of the
        topology of the topological space ``X``, as a full subcategory of
        ``Open(X)``, its covering families are the covers in ``B`` of an open
        of ``B``, and ``D`` has limits.  Domain: this category ``Sh(B, D)``.
        Codomain: ``Sheaves(OpenCoveringFamilies(X), D)``.  It sends ``F`` to
        ``U |-> lim_{V in B, V <= U} F(V)``, and it is quasi-inverse to
        restriction along ``B -> Open(X)``: restriction is an equivalence
        (comparison lemma; Stacks 009H, Hartshorne II Ex. 1.22, locator to
        check).
        """
        assert False, "extension of sheaves from a basis to Open(X) on Sheaves: not implemented"

    def _repr_(self) -> str:
        return f"Sh({self.site_category()}, {self.value_category()}; {self.coverage()})"


__all__ = [
    "Coverage",
    "CoveringFamilies",
    "DescentData",
    "DescentDataOnCover",
    "DescentEqualizer",
    "DescentEqualizerComparison",
    "OpenCoveringFamilies",
    "Sheaves",
    "TrivialCoveringFamilies",
    "trivial_coverage",
]
