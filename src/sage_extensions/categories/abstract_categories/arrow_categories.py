r"""Arrow categories, commuting squares, cores, and slice-style categories.

The arrow category of ``C`` is the functor category out of the walking arrow,

.. MATH::

    \mathrm{Ar}(C) = [[1], C], \qquad [1] = \mathtt{FiniteOrdinalCategory(2)},

reached as ``C.ArrowCategory()``, which is ``Cat().Mor(FiniteOrdinalCategory(2), C)``.
An arrow ``f`` of ``C`` is the functor ``[1] -> C`` sending ``0 -> 1`` to
``f``, and a morphism of arrows is a natural transformation between two such
functors: its components at ``0`` and ``1`` are the two edges of a commuting
square.  The slice, coslice, endomorphism, isomorphism, automorphism,
monomorphism, epimorphism and endofunctor-algebra categories are subcategories
of ``Ar(C)``: each declares it and states only its condition on arrows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from sage.categories.category import Category
from sage.categories.homset import Homset as SageHomset
from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.element import parent
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.cat import (
    Cat,
    NaturalTransformationMor,
    NaturalTransformationMorphism,
    _FunctorCategory,
    _apex_isomorphism_in_subgroup,
)
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoricalIsomorphism,
    FixedRestrictedMorCategory,
    MorCategories,
    MorCategoryConstruction,
    _RestrictedMorCategoryOf,
    _category_accepts_morphism,
    _category_mor_parent,
    _declared_construction,
    _is_selected_identity_in,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.functors.core import Functor, NaturalTransformation
from sage_extensions.categories.sets.indexed_families import IndexedFamily, indexed_family
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import Category as OwnedCategoryBase
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

if TYPE_CHECKING:
    from sage_extensions.logic import Predicate
    from sage_extensions.owned_category import ConstructionData


_Object = TypeVar("_Object")


class _ArrowAsFunctor(Functor):
    r"""The functor ``[1] -> C`` sending the arrow ``0 -> 1`` to one morphism of ``C``."""

    def __init__(self, base_category: Category, arrow: Morphism) -> None:
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        self._arrow = arrow
        super().__init__(FiniteOrdinalCategory(2), base_category)

    def arrow(self) -> Morphism:
        return self._arrow

    def _apply_object(self, obj: Parent) -> ObjectOfCategory:
        match obj.position():
            case 0:
                return self._arrow.domain()
            case 1:
                return self._arrow.codomain()
            case _:
                raise ValueError(
                    f"the walking arrow 0 -> 1 has only the objects 0 and 1, but got {obj}"
                )

    def _apply_morphism(self, morphism: Map) -> Map:
        left = morphism.domain().position()
        right = morphism.codomain().position()
        if left == right:
            endpoint = self._arrow.domain() if left == 0 else self._arrow.codomain()
            return _category_mor_parent(self.codomain(), endpoint, endpoint).identity()
        if left == 0 and right == 1:
            return self._arrow
        raise ValueError(f"the walking arrow 0 -> 1 has no morphism {left} -> {right}")


@cached_function(key=lambda category, arrow: (id(category), id(arrow)))
def _walking_arrow_functor(category: Category, arrow: Morphism) -> _ArrowAsFunctor:
    r"""The functor ``[1] -> category`` picking out ``arrow``, one for each arrow.

    It is the defining datum an arrow determines, so an arrow category's entry
    receives the same functor each time it is handed the same arrow, and
    builds one object for it.
    """
    return _ArrowAsFunctor(category, arrow)


class CommutativeSquare(NaturalTransformationMorphism):
    r"""A morphism of ``Ar(C)``: a natural transformation between two arrows.

    For arrows ``f: A -> B`` and ``g: A' -> B'`` of ``C``, read as functors out
    of the walking arrow, the components at ``0`` and ``1`` are the left edge
    ``A -> A'`` and the right edge ``B -> B'``, and naturality at ``0 -> 1`` is
    the square ``g left = right f``.
    """

    _commutativity_premises = None
    _commutativity_identity_data = None

    def _walking_arrow(self) -> Category:
        return self.parent().source().domain()

    def left(self) -> Morphism:
        r"""The component at ``0``: the edge between the sources."""
        return self.component(self._walking_arrow()(0))

    def right(self) -> Morphism:
        r"""The component at ``1``: the edge between the targets."""
        return self.component(self._walking_arrow()(1))

    def components(self):
        r"""The two natural-transformation components in their owned product."""
        from sage_extensions.categories.sets.set_categories import Sets

        product = Sets().product((self.left().parent(), self.right().parent()))
        return product((self.left(), self.right()))

    @cached_method
    def commutativity_decision(self):
        r"""The square's defining equations, without forcing an undecided equality.

        Identity construction retains its actual source arrow and identity
        edges.  A view or composite retains its actual input squares; their
        decided laws are sufficient for commutativity, but failed or unknown
        input laws do not refute the result's own equation.  Slice and related
        Mor providers additionally state their fixed-component equations.
        """
        from sage_extensions.logic import conjunction

        mor = self.parent()
        source, target = mor._domain_arrow(), mor._codomain_arrow()
        left, right = self.left(), self.right()
        identity_data = self._commutativity_identity_data
        if identity_data is not None:
            identity_source, left_identity, right_identity = identity_data
            if (
                source is identity_source
                and target is identity_source
                and left is left_identity
                and right is right_identity
            ):
                # Every subcategory here retains these same identities.  Do
                # not ask mor.identity(): strict validation can run while
                # that cached identity is still being constructed.
                return True
        premises = self._commutativity_premises
        if premises and all(
            square.commutativity_decision() is True for square in premises
        ):
            commutes = True
        else:
            commutes = right * source == target * left
        return conjunction((commutes, *mor._component_equations(self)))

    @validator
    def validate_commutativity(self) -> None:
        r"""Check the retained square law when requested (``OWN-22``)."""
        decision = self.commutativity_decision()
        if decision is False:
            raise ValueError(
                f"the square from {self.domain()} to {self.codomain()} with "
                f"left edge {self.left()} and right edge {self.right()} fails "
                "its defining square or component equations"
            )
        assert decision is True, (
            "no selected morphism-equality algorithm decides the commuting-square "
            f"equations of {self}"
        )

    def __eq__(self, other: Any) -> bool | Predicate:
        r"""Two squares between the same arrows agree when both of their edges do."""
        if self is other:
            return True
        if parent(other) is not self.parent():
            return False
        equalities = (self.left() == other.left(), self.right() == other.right())
        from sage_extensions.logic import conjunction

        return conjunction(equalities)

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
        category = self.parent().arrow_category()
        other = category.Mor(other.domain(), other.codomain())(other)
        # If r f = g l and s g = h m, then (s r) f = h (m l).
        return category.Mor(other.domain(), self.codomain())._from_commuting_edges(
            self.left() * other.left(),
            self.right() * other.right(),
            commutativity_premises=(self, other),
        )

    def _repr_(self) -> str:
        return f"Commutative square from {self.domain()} to {self.codomain()}"


class ArrowMor(NaturalTransformationMor):
    r"""The Mor of ``Ar(C)``, or of a subcategory of it, written by its two edges."""

    Element = CommutativeSquare

    def arrow_category(self) -> Category:
        return self.base_category()

    def _edge_category(self) -> Category:
        r"""``C``, the category whose morphisms the edges are."""
        return self.source().codomain()

    def _domain_arrow(self) -> Morphism:
        r"""The arrow of ``C`` that the domain of this Mor is."""
        return self.domain().arrow()

    def _codomain_arrow(self) -> Morphism:
        r"""The arrow of ``C`` that the codomain of this Mor is."""
        return self.codomain().arrow()

    def _component_equations(self, square):
        r"""Additional defining component equations of a slice-style Mor.

        An ordinary arrow square has only its naturality equation.  A
        refined provider states its fixed-edge equations here, on the same
        retained components; it does not replace supplied edges by identities.
        """
        return ()

    def _element_constructor_(self, left, right=None, *, check=False):
        match left:
            case CommutativeSquare() if right is None:
                if left.parent() is self:
                    left.validate_commutativity(check=check)
                    return left
                raise TypeError(f"{left} belongs to another Mor; apply the functor between the categories")
            case NaturalTransformation() if right is None:
                # The inherited supplier retains this literal transformation
                # and checks its original functor endpoints.  Request both
                # components to perform their existing category admission.
                square = self._transformation(left, element_class=self.element_class)
                square.left()
                square.right()
                square.validate_commutativity(check=check)
                return square
        if right is None:
            left, right = left
        return self._square(left, right, verify=check)

    def _square(
        self,
        left: Morphism,
        right: Morphism,
        *,
        verify: bool = False,
        element_class=None,
        construction_data=None,
        commutativity_premises=None,
        identity_data=None,
    ) -> CommutativeSquare:
        r"""Retain these admitted edges and defer checking their square law.

        ``verify`` is the standard diagnostic check flag, not a certificate.
        A view or composite may retain its actual prior squares in
        ``commutativity_premises``.  The sole supplier of ``identity_data`` is
        :meth:`identity`: its tuple contains the actual source arrow and the
        two identity edges obtained from the base category.  These data are
        installed before validation, including for private square classes.
        """
        source = self._domain_arrow()
        target = self._codomain_arrow()
        if left.domain() is not source.domain() or left.codomain() is not target.domain():
            raise ValueError(
                f"a square from {source} to {target} needs its left edge to be a map {source.domain()} -> "
                f"{target.domain()}, but {left} is a map {left.domain()} -> {left.codomain()}"
            )
        if right.domain() is not source.codomain() or right.codomain() is not target.codomain():
            raise ValueError(
                f"a square from {source} to {target} needs its right edge to be a map {source.codomain()} -> "
                f"{target.codomain()}, but {right} is a map {right.domain()} -> {right.codomain()}"
            )
        base = self._edge_category()
        if not _category_accepts_morphism(base, source.domain(), target.domain(), left):
            raise ValueError(f"the left edge {left} of the square is not a morphism of {base}")
        if not _category_accepts_morphism(base, source.codomain(), target.codomain(), right):
            raise ValueError(f"the right edge {right} of the square is not a morphism of {base}")
        edges = {0: left, 1: right}
        transformation = NaturalTransformation(
            self.source(),
            self.target(),
            lambda obj: edges[obj.position()],
        )
        selected = self.element_class if element_class is None else element_class
        square = selected(self, transformation, **dict(construction_data or {}))
        square._commutativity_premises = (
            None if commutativity_premises is None else tuple(commutativity_premises)
        )
        square._commutativity_identity_data = identity_data
        square.validate_commutativity(check=verify)
        return square

    def _from_commuting_edges(
        self, left: Morphism, right: Morphism, *, commutativity_premises=None
    ) -> CommutativeSquare:
        r"""Retain constructed edges and any actual sufficient square premises."""
        return self._square(
            left, right, commutativity_premises=commutativity_premises
        )

    @object_level
    @cached_method
    def identity(self) -> CommutativeSquare:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        arrow = self._domain_arrow()
        category = self._edge_category()
        left = _category_mor_parent(category, arrow.domain(), arrow.domain()).identity()
        right = _category_mor_parent(category, arrow.codomain(), arrow.codomain()).identity()
        return self._square(
            left, right, identity_data=(arrow, left, right)
        )


class ArrowMorCategoryConstruction(MorCategoryConstruction):
    r"""The family ``(f, g) |-> Hom_Ar(C)(f, g)`` of commuting-square categories.

    The base is the chosen ``Ar(C) = [[1], C]``. Each ``Of(f, g)`` retains
    its literal walking-arrow functors and selects :class:`ArrowMor`: its
    objects are pairs ``(l, r)`` with ``r f = g l``. The common Mor family
    owns endpoint normalization, literal reuse and the ``Of``/``Between``
    entries; this specialization adds only that fixed-category selection.

    An object of this family is a fixed category of squares. The family's
    arrows are the functors inherited from ``Cat`` between those exact
    categories, and the morphisms between those functors are the existing
    natural transformations. They retain their separate construction from
    the squares classified by ``Of(f, g)``.
    """

    FixedCategoryClass = ArrowMor


class _WalkingArrowFunctorCategory(_FunctorCategory):
    r"""``Ar(C) = [[1], C]``, the functor category out of the walking arrow.

    This is ``Cat().Mor(FiniteOrdinalCategory(2), C)``: ``Cat``'s Mor family
    selects this realization for the walking arrow, so there is one category
    object, and ``C.ArrowCategory()`` names it.  Its objects are functors built
    by the entry of ``[J, C]`` and its morphisms are natural transformations;
    what it adds is the vocabulary the shape ``[1]`` names -- the arrow a
    functor picks out, its source and target, the two edges of a square -- and
    the entry that reads an arrow of ``C`` as the functor it determines.
    """

    _MorCategory = ArrowMorCategoryConstruction

    class ParentMethods:
        r"""A functor ``[1] -> C``, read as the arrow of ``C`` it picks out."""

        def arrow(self) -> Morphism:
            r"""The image of the arrow ``0 -> 1`` of the walking arrow."""
            walking_arrow = self.functor().domain()
            return self.functor()(walking_arrow.Mor(walking_arrow(0), walking_arrow(1)).unique())

        def source_object(self):
            return self.functor()(self.functor().domain()(0))

        def target_object(self):
            return self.functor()(self.functor().domain()(1))

        def arrow_category(self) -> Category:
            return self.functor_category()

        def _repr_(self) -> str:
            return f"Arrow object ({self.source_object()} -> {self.target_object()})"

    def an_object(self):
        r"""The identity of an object of ``C``, as an arrow."""
        base = self.codomain_category()
        witness = base.an_object()
        return self.object(_category_mor_parent(base, witness, witness).identity())

    def admits_arrow(self, arrow: Morphism) -> bool:
        r"""Whether ``arrow`` is an arrow of ``C``."""
        base = self.codomain_category()
        return (
            arrow.domain() in base
            and arrow.codomain() in base
            and _category_accepts_morphism(base, arrow.domain(), arrow.codomain(), arrow)
        )

    def object(self, value: Functor | Morphism):
        r"""The object of ``[[1], C]`` on a functor out of the walking arrow, or on an arrow of ``C``.

        The functor is the defining datum.  An arrow ``f`` of ``C`` determines
        the functor sending ``0 -> 1`` to ``f``, and that functor is handed to
        the one entry of ``[[1], C]``.  In particular a morphism of ``Cat``
        entering ``Ar(Cat)`` is an arrow of the base, not its underlying
        functor reinterpreted as a walking-arrow diagram.
        """
        match value:
            case Functor():
                return super().__call__(value)
        if not self.admits_arrow(value):
            raise TypeError(
                f"{value} is not an object of {self}: it is not an arrow of the base category"
            )
        return super().__call__(_walking_arrow_functor(self.codomain_category(), value))

    __call__ = object

    def morphism(
        self,
        source: Parent,
        target: Parent,
        left: Morphism,
        right: Morphism,
    ) -> CommutativeSquare:
        return self.Mor(source, target)(left, right)

    def compose(
        self,
        second: CommutativeSquare,
        first: CommutativeSquare,
    ) -> CommutativeSquare:
        if first.codomain() is not second.domain():
            raise ValueError(
                f"cannot compose the squares {second} o {first}: {first} ends at {first.codomain()}, but "
                f"{second} starts at {second.domain()}"
            )
        return second * first

    def _repr_(self) -> str:
        return f"Arrow category of {self.codomain_category()}"


class _SubcategoryOfArrows(OwnedCategory):
    r"""A subcategory of ``Ar(C)`` whose objects are the arrows of ``C`` satisfying a condition.

    It declares ``Ar(C)``, or a subcategory of it, and states only its
    condition, :meth:`admits_arrow`.  Its entry reads an arrow as the functor
    out of the walking arrow it determines and builds the object on that
    functor, so the object is placed here and threads through ``Ar(C)``.  An
    object of a declared category does not acquire narrower placement merely
    because its arrow satisfies the condition; it enters through this
    constructor. A subcategory whose morphisms are all the squares between
    its objects declares no Mor family and has the Mor of ``Ar(C)``.
    """

    @abstract_method
    def base_category(self) -> Category:
        r"""``C``, whose arrows the objects of this category are."""

    def admits_arrow(self, arrow: Morphism) -> bool:
        r"""Whether ``arrow`` is the arrow of an object of this category."""
        base = self.base_category()
        return (
            arrow.domain() in base
            and arrow.codomain() in base
            and _category_accepts_morphism(base, arrow.domain(), arrow.codomain(), arrow)
        )

    def __contains__(self, candidate):
        match candidate:
            case Functor():
                return candidate in self.base_category().ArrowCategory() and self.admits_arrow(candidate.arrow())
            case _:
                return super().__contains__(candidate)

    def an_object(self):
        r"""The identity of an object of ``C``, as an arrow."""
        base = self.base_category()
        witness = base.an_object()
        return self.object(_category_mor_parent(base, witness, witness).identity())

    def object(self, arrow: Morphism) -> ObjectOfCategory:
        if not self.admits_arrow(arrow):
            raise TypeError(
                f"{arrow} is not an object of {self}: it is not an arrow of the base category"
            )
        return self._object_on(_walking_arrow_functor(self.base_category(), arrow))

    __call__ = object

    @cached_method(key=lambda self, functor: id(functor))
    def _object_on(self, functor: Functor):
        return self.base_category().ArrowCategory()(functor)

    def Mor(self, source: Parent, target: Parent) -> ArrowMor:
        if source not in self or target not in self:
            raise TypeError(
                f"a morphism in {self} needs two objects of {self}, but got {source} and {target}"
            )
        return self.MorCategory().Of(source, target)

    def morphism(
        self,
        source: Parent,
        target: Parent,
        left: Morphism,
        right: Morphism,
    ) -> CommutativeSquare:
        return self.Mor(source, target)(left, right)

    def identity(self, arrow_object: Parent) -> CommutativeSquare:
        return self.Mor(arrow_object, arrow_object).identity()

    def compose(
        self,
        second: CommutativeSquare,
        first: CommutativeSquare,
    ) -> CommutativeSquare:
        if first.codomain() is not second.domain():
            raise ValueError(
                f"cannot compose the squares {second} o {first}: {first} ends at {first.codomain()}, but "
                f"{second} starts at {second.domain()}"
            )
        return second * first


class _EndofunctorAlgebraMor(ArrowMor):
    r"""Morphisms ``f`` with ``f a = b T(f)`` between ``T``-algebras.

    A morphism of the arrow category is a commuting square.  Here its left
    edge satisfies ``left = T(f)``.  Omitting it selects ``T(f)``; an explicit
    edge is retained with this equation, including an undecided equation.
    Thus one underlying arrow determines one structured morphism once the
    defining laws hold, exactly as in ``Inserter(T, Id)``.
    """

    class Element(CommutativeSquare):
        r"""A structured map acting through its underlying morphism."""

        def underlying_morphism(self) -> Morphism:
            return self.right()

        def _call_(self, element):
            return self.underlying_morphism()(element)

    def _element_constructor_(self, left, right=None, *, check=False):
        category = self.arrow_category()
        match left:
            case CommutativeSquare() | NaturalTransformation() if right is None:
                return super()._element_constructor_(left, check=check)
        if right is None:
            right = left
            left = category.endofunctor()(right)
        return self._square(left, right, verify=check)

    def _component_equations(self, square):
        r"""Supply the additional inserter equation to the square-law owner."""
        return super()._component_equations(square) + (
            square.left() == self.arrow_category().endofunctor()(square.right()),
        )


class _EndofunctorAlgebraForgetfulFunctor(Functor):
    r"""The forgetful functor ``Alg(T) -> C``, ``(X, a) |-> X``."""

    _faithful = True

    def __init__(self, algebras: _EndofunctorAlgebraCategory) -> None:
        self._algebras = algebras
        super().__init__(algebras, algebras.base_category())

    def _apply_object(self, algebra: Parent) -> ObjectOfCategory:
        return algebra.target_object()

    def _apply_morphism(self, morphism: Map) -> Map:
        return morphism.right()

    def _repr_(self) -> str:
        return f"Forgetful functor {self.domain()} -> {self.codomain()}"


class _EndofunctorAlgebraMorCategory(MorCategoryConstruction):
    FixedCategoryClass = _EndofunctorAlgebraMor


class _EndofunctorAlgebraCategory(_SubcategoryOfArrows):
    r"""The category of algebras of an endofunctor ``T : C -> C``.

    An object is an arrow ``a : T(X) -> X`` of ``C``, built as an object of
    ``Ar(C)`` on that exact arrow, so neither endpoint is rebuilt.  Its Mors
    are cut down from all commuting squares to the squares whose left edge is
    ``T(f)``; hence its objects and morphisms are those of ``Inserter(T, Id_C)``.
    """

    _MorCategory = _EndofunctorAlgebraMorCategory

    def __init__(self, endofunctor: Functor) -> None:
        if endofunctor.domain() is not endofunctor.codomain():
            raise ValueError(
                f"an endofunctor must have equal domain and codomain, but {endofunctor} is a functor "
                f"{endofunctor.domain()} -> {endofunctor.codomain()}"
            )
        self._endofunctor = endofunctor
        super().__init__()

    def _make_named_class_key(self, name):
        return self._endofunctor._cache_key()

    def endofunctor(self) -> Functor:
        return self._endofunctor

    def base_category(self) -> Category:
        return self.endofunctor().domain()

    def arrow_category(self) -> Category:
        return self.base_category().ArrowCategory()

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        return [Cat().Mor(FiniteOrdinalCategory(2), self.base_category())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        r"""An algebra structure on its target: an arrow ``T(X) -> X``."""
        return super().admits_arrow(arrow) and arrow.domain() is self.endofunctor()(arrow.codomain())

    def algebra(
        self,
        underlying_object: Parent,
        structure: Morphism,
    ) -> ObjectOfCategory:
        r"""Return ``(X, structure : T(X) -> X)`` for the object ``X`` of ``C``.

        Both the supplied object and the supplied structure arrow are kept
        literally. In particular two different structure arrows on one object
        produce two different algebra objects whose forgetful image is that
        same object.
        """
        if underlying_object not in self.base_category():
            raise TypeError(
                f"an algebra for {self.endofunctor()} needs an object of {self.base_category()}, but "
                f"{underlying_object} is not one"
            )
        if structure.domain() is not self.endofunctor()(underlying_object):
            raise ValueError(
                f"an algebra structure on {underlying_object} for T = {self.endofunctor()} is a map "
                f"T(X) -> X starting at {self.endofunctor()(underlying_object)}, but {structure} starts at "
                f"{structure.domain()}"
            )
        if structure.codomain() is not underlying_object:
            raise ValueError(
                f"an algebra structure on {underlying_object} is a map T(X) -> X ending at {underlying_object}, "
                f"but {structure} ends at {structure.codomain()}"
            )
        return self.object(structure)

    def underlying_object(self, algebra: Parent):
        if algebra not in self:
            raise TypeError(f"{algebra} is not an algebra for {self.endofunctor()}")
        return algebra.target_object()

    def structure(self, algebra: Parent) -> Morphism:
        if algebra not in self:
            raise TypeError(f"{algebra} is not an algebra for {self.endofunctor()}")
        return algebra.arrow()

    def homomorphism(
        self,
        source: Parent,
        target: Parent,
        underlying_morphism: Morphism,
    ) -> CommutativeSquare:
        r"""Equip ``f`` with its forced commuting square ``(T(f), f)``."""
        return self.Mor(source, target)(underlying_morphism)

    @cached_method
    def forgetful(self) -> Functor:
        return _EndofunctorAlgebraForgetfulFunctor(self)

    def _repr_(self) -> str:
        return f"Algebras of {self.endofunctor()}"


type ArrowLevel = dict[Category, Morphism]
r"""One arrow level of an object: each slice (or each coslice) category it was
constructed in, with the arrow it has as an object of that category.  It is
construction data of the level (``OWN-05``), which no public operation
returns; the public question is ``category.arrow(obj)``."""


def _level_arrow(arrows: ArrowLevel, category: Category, obj: Parent) -> Morphism:
    r"""The arrow of ``obj`` as an object of the slice or coslice ``category``.

    ``arrows`` is one arrow level of ``obj``.  The arrow is the one recorded
    with ``category``, or with a category that refines it over the same fixed
    object, as the subsets of ``X`` refine ``Set/X``: the inclusion of that
    refinement into ``category`` keeps the arrow.
    """
    match tuple(
        arrow
        for level, arrow in arrows.items()
        if level.is_subcategory(category) and level.base_object() is category.base_object()
    ):
        case (arrow,):
            return arrow
        case found:
            assert False, (
                f"{obj} is an object of {category}, but it has {len(found)} arrows recorded in it or in a "
                f"refinement of it over {category.base_object()}, not one: it was constructed in "
                f"{tuple(arrows)}"
            )


def _chosen_arrow(obj: Parent) -> Morphism:
    r"""The arrow of an object as an object of its finest slice or coslice.

    The finest is the slice or coslice it was constructed in that is a
    subcategory of every other.  A finite Galois stage is an object of
    ``(K/Fields)/e``, which declares ``K/Fields``; its arrow in ``K/Fields`` is
    the image of its arrow ``(K -> L) -> e`` under the forgetful functor, so
    its chosen arrow is the arrow in ``(K/Fields)/e``.  An object of ``C/X``
    and of ``C/Y`` has no finest one: it has one arrow as an object of each,
    and the slice names which, ``category.arrow(obj)``.
    """
    categories, _ = obj._added_structure({})
    match tuple(
        category
        for category in categories
        if all(category.is_subcategory(other) for other in categories)
    ):
        case (category,):
            return category.arrow(obj)
        case _:
            assert False, (
                f"{obj} is an object of the slices and coslices {categories}, none of them finer than the "
                "others, with one arrow as an object of each: ask the arrow of the category that names it, "
                "category.arrow(obj)"
            )


class SliceMor(ArrowMor):
    r"""Morphisms in a slice; the edge at the fixed codomain is the identity."""

    def _domain_arrow(self) -> Morphism:
        return self.arrow_category().arrow(self.domain())

    def _codomain_arrow(self) -> Morphism:
        return self.arrow_category().arrow(self.codomain())

    def _edge_category(self) -> Category:
        return self.arrow_category().base_category()

    def source(self) -> Functor:
        r"""The functor ``[1] -> C`` that the domain's chosen arrow determines."""
        return _walking_arrow_functor(self._edge_category(), self._domain_arrow())

    def target(self) -> Functor:
        r"""The functor ``[1] -> C`` that the codomain's chosen arrow determines."""
        return _walking_arrow_functor(self._edge_category(), self._codomain_arrow())

    def _element_constructor_(self, factor, right=None, *, check=False):
        match factor:
            case CommutativeSquare() | NaturalTransformation() if right is None:
                return super()._element_constructor_(factor, check=check)
        fixed = self._domain_arrow().codomain()
        if self._codomain_arrow().codomain() is not fixed:
            raise ValueError(
                f"a morphism in a slice category C/X needs both objects over one X, but {self.domain()} lies "
                f"over {fixed} and {self.codomain()} lies over {self._codomain_arrow().codomain()}"
            )
        if right is None:
            right = _category_mor_parent(self._edge_category(), fixed, fixed).identity()
        return self._square(factor, right, verify=check)

    def _component_equations(self, square):
        r"""Retain the fixed-target identity equation, without replacing its edge."""
        fixed = self._domain_arrow().codomain()
        identity = _category_mor_parent(self._edge_category(), fixed, fixed).identity()
        return super()._component_equations(square) + (square.right() == identity,)

    def canonical_morphism(self) -> CommutativeSquare:
        inclusion = self._domain_arrow()
        target_inclusion = self._codomain_arrow()
        return self(inclusion.factor_through(target_inclusion))


class SliceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SliceMor

    def fixed_category_class_for(self, domain, codomain):
        r"""Use the slice's declared arrow implementation, if it supplies one.

        The declaration implements this same fixed slice Mor. Its owner
        supplies any lower-arrow initialization required by its represented
        objects; other slices retain the existing square implementation.
        """
        declared = _declared_construction(self.base_category(), "_SliceMor")
        return self.FixedCategoryClass if declared is None else declared


class SliceCategory(_SubcategoryOfArrows):
    r"""The slice category \(C/X\): arrows into ``X``, with squares whose right edge is ``id_X``.

    Unverified specimens retain equal-but-distinct base sets and keep the
    slice and coslice fixed edges under nonidentity composition::

        sage: from dzack_research.preamble.all import Sets
        sage: X, T = Sets.Δ[1], Sets.Δ[0]
        sage: C = SliceCategory(Sets(), T)
        sage: A = C(Sets().Mor(X, T)(lambda point: T(0)))
        sage: swap = Sets().Mor(X, X)(lambda point: X(1-int(point)))
        sage: square = C.Mor(A, A)(swap)
        sage: square * square == C.Mor(A, A).identity()
        True
        sage: square.left() == swap and square.right() == Sets().Mor(T, T).identity()
        True

        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: from sage_extensions.categories.functors.core import IdentityFunctor
        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: points = finite_ordered_set(("a", "b"))
        sage: other_points = finite_ordered_set(("a", "b"))
        sage: points == other_points and points is not other_points
        True
        sage: SliceCategory(Sets(), points).base_object() is points
        True
        sage: SliceCategory(Sets(), other_points).base_object() is other_points
        True
        sage: CosliceCategory(Sets(), other_points).base_object() is other_points
        True
        sage: SubobjectCategory(Sets(), other_points).base_object() is other_points
        True
        sage: one = finite_ordered_set(("*",))
        sage: swap = Sets().Mor(points, points)(lambda point: "b" if point == "a" else "a")
        sage: slice_category = SliceCategory(Sets(), one)
        sage: retained_arrow = Sets().Mor(points, one)(lambda point: "*")
        sage: obj = slice_category(retained_arrow)
        sage: obj in Sets() and slice_category.arrow(obj) is retained_arrow
        True
        sage: Mor = slice_category.Mor(obj, obj)
        sage: Mor is slice_category.MorCategory().Of(obj, obj)
        True
        sage: square = Mor(swap)
        sage: square * square == Mor.identity()
        True
        sage: coslice = CosliceCategory(Sets(), one)
        sage: obj = coslice(Sets().Mor(one, points)(lambda point: "a"))
        sage: Mor = coslice.Mor(obj, obj)
        sage: collapse = Mor(Sets().Mor(points, points)(lambda point: "a"))
        sage: collapse * collapse == collapse
        True
        sage: Mor.identity() * collapse == collapse
        True
        sage: algebras = IdentityFunctor(Sets()).algebras()
        sage: algebra = algebras.algebra(points, swap)
        sage: Mor = algebras.Mor(algebra, algebra)
        sage: Mor is algebras.MorCategory().Of(algebra, algebra)
        True
        sage: Mor(swap) * Mor(swap) == Mor.identity()
        True
    """

    _MorCategory = SliceMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, base_category, base_object: (cls, id(base_category), id(base_object)))
    def __classcall__(cls, base_category: Category, base_object: Parent):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category, base_object)
        if cls is SliceCategory:
            declared = _declared_construction(base_category, "_SliceCategory")
            if declared is not None:
                selected = declared._slice_category_class_for(base_category, base_object)
                if selected is not None:
                    # The cache belongs to this exact SliceCategory(C, X)
                    # entry, including when its owner supplies a more specific
                    # implementation. No second category is constructed.
                    return typecall(selected, base_category, base_object)
        return typecall(cls, base_category, base_object)

    def __init__(self, base_category: Category, base_object: Parent) -> None:
        if base_object not in base_category:
            raise TypeError(
                f"the slice category C/X needs X an object of C = {base_category}, but {base_object} is not one"
            )
        self._base_category = base_category
        self._base_object = base_object
        super().__init__()

    def _make_named_class_key(self, name):
        return self._base_category, id(self._base_object)

    def base_category(self) -> Category:
        return self._base_category

    def base_object(self) -> ObjectOfCategory:
        return self._base_object

    def object(
        self,
        arrow: Morphism,
        *,
        categories=(),
        construction_data=None,
        _engine=None,
    ) -> ObjectOfCategory:
        r"""The object ``(A, p)`` of ``C/X`` on an arrow ``p: A -> X``, optionally with stronger structure.

        The owner of ``A`` constructs it on the data of ``A`` (``OWN-16``):
        the result is an object of ``C/X``, which adds only ``p``, and of
        ``C``, which ``C/X`` declares; the finer categories of ``A`` do not
        place it (``ARC-08``, ``CON-07``).  ``categories`` and
        ``construction_data`` are further levels that a caller adds with
        their data, and ``_engine`` is a private computation class of this
        level.
        """
        if not self.admits_arrow(arrow):
            raise TypeError(
                f"{arrow} is not an object of {self}: it is not an arrow of the base category ending at the base object"
            )
        if _engine is None and construction_data is None and not categories:
            return self._object_on(arrow)
        return self._construct_on(arrow, tuple(categories), _engine, construction_data)

    __call__ = object

    @cached_method(key=lambda self, arrow: id(arrow))
    def _object_on(self, arrow: Morphism):
        return self._construct_on(arrow, (), None, None)

    def _construct_on(self, arrow: Morphism, categories, engine, construction_data):
        return arrow.domain()._with_structure(
            (self, *categories),
            {"slice_arrows": {self: arrow}, **dict(construction_data or {})},
            engine=engine,
        )

    def arrow(self, obj: ObjectOfCategory) -> Morphism:
        r"""The arrow ``p: A -> X`` of an object ``(A, p)`` of this slice ``C/X``.

        One object can lie in several slices, ``C/X`` and ``C/Y``, and it has
        one arrow as an object of each; the slice names which.  The arrow is
        the image of the object under the functor ``C/X -> Ar(C)``.
        """
        assert obj in self, f"{obj} is not an object of {self}, so it has no arrow in it"
        return obj._slice_arrow_in(self)

    def super_categories(self):
        r"""An object ``(A, p: A -> X)`` of ``C/X`` is an object ``A`` of ``C`` with the chosen arrow ``p``.

        The inclusion of ``C/X`` into ``Ar(C)`` is a functor, not this
        declaration (``CAT-16``, ``CAT-20``).
        """
        return [self.base_category()]

    class ParentMethods:
        r"""An object ``A`` of ``C`` with its chosen arrow ``p: A -> X`` to the fixed object."""

        def __init__(self, slice_arrows: ArrowLevel, **rest) -> None:
            self._slice_arrows = slice_arrows
            super().__init__(**rest)

        def arrow(self) -> Morphism:
            r"""The chosen arrow, when this object was constructed in one slice or coslice only."""
            return _chosen_arrow(self)

        def _underlying_slice_object(self):
            r"""Return A from the retained arrow p: A -> X."""
            return self.arrow().domain()

        def _cardinality_decision(self):
            r"""The slice object has the cardinality of its underlying object."""
            return self._underlying_slice_object().cardinality()

        def _finiteness_decision(self):
            r"""The slice object is finite exactly when its underlying object is finite."""
            return self._underlying_slice_object().is_finite()

        def __iter__(self):
            r"""Enumerate the points of the underlying object when it is enumerated."""
            return iter(self._underlying_slice_object())

        def __contains__(self, element):
            r"""Membership in a slice object is membership in its underlying object."""
            return element in self._underlying_slice_object()

        is_parent_of = __contains__

        def _slice_arrow_in(self, category: Category) -> Morphism:
            r"""The arrow of this object as an object of the slice ``category``.

            Protected contract (``OWN-05``).  Owner: ``SliceCategory``, whose
            level stores the slice arrows.  Caller: ``SliceCategory.arrow``,
            the dispatcher, after it has established that this object is an
            object of ``category``.  The arrows are construction data, which
            no public operation returns; the public question is
            ``category.arrow(obj)``.
            """
            return _level_arrow(self._slice_arrows, category, self)

        def _added_structure(
            self,
            construction_data: dict[str, ConstructionData],
        ) -> tuple[tuple[Category, ...], dict[str, ConstructionData]]:
            r"""The slices of this object and their arrows, with the slice arrows in ``construction_data``.

            Kept when this object is constructed again (``OWN-05``; see
            ``Objects``): the result is an object of each slice of this object
            and of each further slice, with its arrow in each.
            """
            further = dict(construction_data)
            arrows = {**self._slice_arrows, **further.pop("slice_arrows", {})}
            categories, data = super()._added_structure(further)
            return (*categories, *arrows), {**data, "slice_arrows": arrows}

    def an_object(self) -> ObjectOfCategory:
        r"""The identity of the fixed base object."""
        base_object = self.base_object()
        return self.object(
            _category_mor_parent(self.base_category(), base_object, base_object).identity()
        )

    def admits_arrow(self, arrow: Morphism) -> bool:
        r"""An arrow into the fixed base object."""
        return arrow.codomain() is self.base_object() and super().admits_arrow(arrow)

    def _repr_(self) -> str:
        return f"Slice category {self.base_category()}/{self.base_object()}"


class CosliceMor(ArrowMor):
    r"""Morphisms in a coslice; the edge at the fixed domain is the identity."""

    def _domain_arrow(self) -> Morphism:
        return self.arrow_category().arrow(self.domain())

    def _codomain_arrow(self) -> Morphism:
        return self.arrow_category().arrow(self.codomain())

    def _edge_category(self) -> Category:
        return self.arrow_category().base_category()

    def source(self) -> Functor:
        r"""The functor ``[1] -> C`` that the domain's chosen arrow determines."""
        return _walking_arrow_functor(self._edge_category(), self._domain_arrow())

    def target(self) -> Functor:
        r"""The functor ``[1] -> C`` that the codomain's chosen arrow determines."""
        return _walking_arrow_functor(self._edge_category(), self._codomain_arrow())

    def _element_constructor_(self, left, right=None, *, check=False):
        match left:
            case CommutativeSquare() | NaturalTransformation() if right is None:
                return super()._element_constructor_(left, check=check)
        fixed = self._domain_arrow().domain()
        if self._codomain_arrow().domain() is not fixed:
            raise ValueError(
                f"a morphism in a coslice category X/C needs both objects under one X, but {self.domain()} lies "
                f"under {fixed} and {self.codomain()} lies under {self._codomain_arrow().domain()}"
            )
        if right is None:
            right = left
            left = _category_mor_parent(self._edge_category(), fixed, fixed).identity()
        return self._square(left, right, verify=check)

    def _component_equations(self, square):
        r"""Retain the fixed-source identity equation, without replacing its edge."""
        fixed = self._domain_arrow().domain()
        identity = _category_mor_parent(self._edge_category(), fixed, fixed).identity()
        return super()._component_equations(square) + (square.left() == identity,)

class CosliceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = CosliceMor


class CosliceCategory(_SubcategoryOfArrows):
    r"""The coslice category \(X/C\): arrows out of ``X``, with squares whose left edge is ``id_X``.

    A nonidentity idempotent square retains the fixed identity edge::

        sage: from dzack_research.preamble.all import Sets
        sage: T, X = Sets.Δ[0], Sets.Δ[1]
        sage: C = CosliceCategory(Sets(), T)
        sage: A = C(Sets().Mor(T, X)(lambda point: X(0)))
        sage: collapse = Sets().Mor(X, X)(lambda point: X(0))
        sage: square = C.Mor(A, A)(collapse)
        sage: square * square == square
        True
        sage: square.left() == Sets().Mor(T, T).identity() and square.right() == collapse
        True
    """

    _MorCategory = CosliceMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, base_category, base_object: (cls, id(base_category), id(base_object)))
    def __classcall__(cls, base_category: Category, base_object: Parent):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category, base_object)
        if cls is CosliceCategory:
            # X/C is the functorial construction C |-> X/C: a category class
            # declares the construction's class for its coslices as the nested
            # ``Coslices`` (a subclass of CosliceCategory), found through its
            # class inheritance like any category-level declaration.
            construction = _declared_construction(base_category, "Coslices")
            if construction is not None:
                return typecall(construction, base_category, base_object)
        return typecall(cls, base_category, base_object)

    def __init__(self, base_category: Category, base_object: Parent) -> None:
        if base_object not in base_category:
            raise TypeError(
                f"the coslice category X/C needs X an object of C = {base_category}, but {base_object} is not one"
            )
        self._base_category = base_category
        self._base_object = base_object
        super().__init__()

    def _make_named_class_key(self, name):
        return self._base_category, id(self._base_object)

    def base_category(self) -> Category:
        return self._base_category

    def base_object(self) -> ObjectOfCategory:
        return self._base_object

    def object(
        self,
        arrow: Morphism,
        *,
        _engine=None,
        construction_data=None,
    ) -> ObjectOfCategory:
        r"""The object ``(B, i)`` of ``X/C`` on an arrow ``i: X -> B``, optionally with a private realization.

        The owner of ``B`` constructs it on the data of ``B`` (``OWN-16``):
        the result is an object of ``X/C``, which adds only ``i``, and of
        ``C``, which ``X/C`` declares; the finer categories of ``B`` do not
        place it (``ARC-08``, ``CON-07``).
        """
        if not self.admits_arrow(arrow):
            raise TypeError(
                f"{arrow} is not an object of {self}: it is not an arrow of the base category starting at the base object"
            )
        if _engine is None and construction_data is None:
            return self._object_on(arrow)
        return self._construct_on(arrow, _engine, construction_data)

    __call__ = object

    @cached_method(key=lambda self, arrow: id(arrow))
    def _object_on(self, arrow: Morphism):
        return self._construct_on(arrow, None, None)

    def _construct_on(self, arrow: Morphism, engine, construction_data):
        return arrow.codomain()._with_structure(
            (self,),
            {"coslice_arrows": {self: arrow}, **dict(construction_data or {})},
            engine=engine,
        )

    def arrow(self, obj: ObjectOfCategory) -> Morphism:
        r"""The arrow ``i: X -> B`` of an object ``(B, i)`` of this coslice ``X/C``.

        One object can lie in several coslices, and in slices, with one arrow
        as an object of each; the coslice names which.  The arrow is the image
        of the object under the functor ``X/C -> Ar(C)``.
        """
        assert obj in self, f"{obj} is not an object of {self}, so it has no arrow in it"
        return obj._coslice_arrow_in(self)

    def super_categories(self):
        r"""An object ``(B, i: X -> B)`` of ``X/C`` is an object ``B`` of ``C`` with the chosen arrow ``i``.

        The inclusion of ``X/C`` into ``Ar(C)`` is a functor, not this
        declaration (``CAT-16``, ``CAT-20``).
        """
        return [self.base_category()]

    class ParentMethods:
        r"""An object ``B`` of ``C`` with its chosen arrow ``i: X -> B`` from the fixed object."""

        def __init__(self, coslice_arrows: ArrowLevel, **rest) -> None:
            self._coslice_arrows = coslice_arrows
            super().__init__(**rest)

        def arrow(self) -> Morphism:
            r"""The chosen arrow, when this object was constructed in one slice or coslice only."""
            return _chosen_arrow(self)

        def _coslice_arrow_in(self, category: Category) -> Morphism:
            r"""The arrow of this object as an object of the coslice ``category``.

            Protected contract (``OWN-05``).  Owner: ``CosliceCategory``,
            whose level stores the coslice arrows.  Caller:
            ``CosliceCategory.arrow``, the dispatcher, after it has
            established that this object is an object of ``category``.  The
            arrows are construction data, which no public operation returns;
            the public question is ``category.arrow(obj)``.
            """
            return _level_arrow(self._coslice_arrows, category, self)

        def _added_structure(
            self,
            construction_data: dict[str, ConstructionData],
        ) -> tuple[tuple[Category, ...], dict[str, ConstructionData]]:
            r"""The coslices of this object and their arrows, with the coslice arrows in ``construction_data``.

            Kept when this object is constructed again (``OWN-05``; see
            ``Objects``): the result is an object of each coslice of this
            object and of each further coslice, with its arrow in each.
            """
            further = dict(construction_data)
            arrows = {**self._coslice_arrows, **further.pop("coslice_arrows", {})}
            categories, data = super()._added_structure(further)
            return (*categories, *arrows), {**data, "coslice_arrows": arrows}

    def an_object(self) -> ObjectOfCategory:
        r"""The identity of the fixed base object."""
        base_object = self.base_object()
        return self.object(
            _category_mor_parent(self.base_category(), base_object, base_object).identity()
        )

    def admits_arrow(self, arrow: Morphism) -> bool:
        r"""An arrow out of the fixed base object."""
        return arrow.domain() is self.base_object() and super().admits_arrow(arrow)

    # Implementer side of CoreMor's core contract (OWN-05) for X/C: an
    # isomorphism (B, i) -> (B', i') is a base isomorphism g with g i = i',
    # the square (id_X, g). The base category owns the marked decisions, as it
    # does for marked diagrams (_FunctorCategory).
    def _core_isomorphism_from_apex(self, core_mor, apex):
        r"""The isomorphism of ``core_mor`` whose component on the apex is ``apex``."""
        source, target = core_mor.domain(), core_mor.codomain()
        base = self.base_object()
        identity = _category_mor_parent(self.base_category(), base, base).identity()
        forward = self.Mor(source, target)(identity, apex)
        inverse = self.Mor(target, source)(identity, ~apex)
        return core_mor(forward, inverse)

    def _core_isomorphism_witness(self, core_mor):
        r"""One isomorphism of ``core_mor``, or ``None`` when the base category decides there is none."""
        apex = self.base_category()._marked_isometry(self, core_mor.domain(), core_mor.codomain())
        return None if apex is None else self._core_isomorphism_from_apex(core_mor, apex)

    def _core_automorphism_generators(self, core_mor):
        r"""Automorphisms of the marked object generating its automorphism group, from the base category."""
        from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

        assert core_mor.domain() is core_mor.codomain(), (
            f"group generators belong to Aut(X) = Iso(X, X), but {core_mor} has distinct endpoints"
        )
        apexes = self.base_category()._marked_automorphism_generators(self, core_mor.domain())
        return finite_ordered_set(tuple(self._core_isomorphism_from_apex(core_mor, apex) for apex in apexes))

    def _core_isomorphism_in(self, core_mor, subgroup):
        r"""An isomorphism in the coslice with apex in ``subgroup``, or ``None``.

        Coslice automorphisms fix the source marking pointwise.  Their apex
        images supply the stabilizer for the same finite-coset transporter
        computation used by functor categories.
        """
        if core_mor.is_empty():
            return None
        witness = core_mor.an_element().forward().right()
        apex = _apex_isomorphism_in_subgroup(
            witness,
            subgroup,
            self.base_category()._marked_automorphism_generators(self, core_mor.domain()),
        )
        return None if apex is None else self._core_isomorphism_from_apex(core_mor, apex)

    def _repr_(self) -> str:
        return f"Coslice category {self.base_object()}/{self.base_category()}"


class _FullSubcategoryOfArrows(_SubcategoryOfArrows):
    r"""A full subcategory of ``Ar(C)`` cut out by a property of its arrows.

    Parameterized by ``C`` alone; each category of this shape states its own
    declaration, so the declared graph reads it at the category.
    """

    @staticmethod
    @cached_function(key=lambda cls, base_category: (cls, id(base_category)))
    def __classcall__(cls, base_category: Category):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category)
        return typecall(cls, base_category)

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        super().__init__()

    def _make_named_class_key(self, name):
        return id(self._base_category)

    def base_category(self) -> Category:
        return self._base_category


class _EndArrowCategory(_FullSubcategoryOfArrows):
    r"""The full subcategory of ``Ar(C)`` on endomorphisms."""

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        return [Cat().Mor(FiniteOrdinalCategory(2), self.base_category())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return arrow.domain() is arrow.codomain() and super().admits_arrow(arrow)

    def _repr_(self) -> str:
        return f"Endomorphism arrows of {self.base_category()}"


class _IsoArrowCategory(_FullSubcategoryOfArrows):
    r"""The full subcategory of ``Ar(C)`` on isomorphisms.

    Which arrows are isomorphisms is the core's question: an arrow lies here
    when it is an arrow of ``Core(C)``.
    """

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        return [Cat().Mor(FiniteOrdinalCategory(2), self.base_category())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return super().admits_arrow(arrow) and (
            _is_selected_identity_in(self.base_category(), arrow)
            or arrow in self.base_category().Core().Mor(arrow.domain(), arrow.codomain())
        )

    def _repr_(self) -> str:
        return f"Isomorphism arrows of {self.base_category()}"


class _AutomorphismArrowCategory(_IsoArrowCategory):
    r"""The full subcategory of the arrow category on automorphisms."""

    def super_categories(self):
        return [
            _IsoArrowCategory(self.base_category()),
            _EndArrowCategory(self.base_category()),
        ]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return arrow.domain() is arrow.codomain() and super().admits_arrow(arrow)

    def _repr_(self) -> str:
        return f"Automorphism arrows of {self.base_category()}"


class _MonomorphismArrowCategory(_FullSubcategoryOfArrows):
    r"""The full subcategory of the arrow category on represented monomorphisms.

    Which arrows are monic is the base category's own question, so this asks
    the mono family that category declares.  Injectivity is the answer in sets
    and modules and is the declared default there; it is neither necessary nor
    sufficient in every category, so it is not the definition used here.
    """

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        return [Cat().Mor(FiniteOrdinalCategory(2), self.base_category())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return super().admits_arrow(arrow) and self.base_category().category_packet().Monos().accepts(arrow)

    def _repr_(self) -> str:
        return f"Monomorphism arrows of {self.base_category()}"


class _EpimorphismArrowCategory(_FullSubcategoryOfArrows):
    r"""The full subcategory of the arrow category on represented epimorphisms.

    As for monomorphisms, the base category's declared epi family answers.
    """

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.products import (
            FiniteOrdinalCategory,
        )

        return [Cat().Mor(FiniteOrdinalCategory(2), self.base_category())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return super().admits_arrow(arrow) and self.base_category().category_packet().Epis().accepts(arrow)

    def _repr_(self) -> str:
        return f"Epimorphism arrows of {self.base_category()}"


def _subobject_source(subobject):
    inclusion = subobject.inclusion()
    return inclusion.domain() if inclusion is subobject else subobject


class SubobjectMorphism(Morphism):
    r"""A factor map with its retained commuting triangle of subobjects.

    Monic cancellation proves uniqueness only under the two actual triangle
    laws.  Undecided laws remain on their selected slice squares, rather than
    turning every same-parent factor datum into an established unique map.
    """

    def __init__(
        self,
        parent: SubobjectMor,
        factor_morphism: Morphism,
        *,
        verify: bool = False,
        _slice_square=None,
    ) -> None:
        Morphism.__init__(self, parent)
        if factor_morphism.domain() is not _subobject_source(self.domain()):
            raise ValueError(
                f"a morphism of subobjects {self.domain()} -> {self.codomain()} needs a map starting at "
                f"{_subobject_source(self.domain())}, but {factor_morphism} starts at {factor_morphism.domain()}"
            )
        if factor_morphism.codomain() is not _subobject_source(self.codomain()):
            raise ValueError(
                f"a morphism of subobjects {self.domain()} -> {self.codomain()} needs a map ending at "
                f"{_subobject_source(self.codomain())}, but {factor_morphism} ends at {factor_morphism.codomain()}"
            )
        base = parent.subobject_category().base_category()
        if not _category_accepts_morphism(
            base,
            _subobject_source(self.domain()),
            _subobject_source(self.codomain()),
            factor_morphism,
        ):
            raise ValueError(
                f"{factor_morphism} is not a morphism of the base category, so it is not a morphism of "
                f"subobjects {self.domain()} -> {self.codomain()}"
            )
        self._factor_morphism = factor_morphism
        slice_mor = parent._slice_mor()
        if _slice_square is None:
            _slice_square = slice_mor(factor_morphism)
        elif (
            _slice_square.parent() is not slice_mor
            or _slice_square.left() is not factor_morphism
        ):
            raise ValueError(
                "a retained subobject triangle needs the exact selected slice "
                "Mor and the same factor map"
            )
        self._slice_square = _slice_square
        self.validate_commutativity(check=verify)

    def factor_morphism(self) -> Morphism:
        return self._factor_morphism

    def commutativity_decision(self):
        r"""Return the actual slice square's triangle law, preserving unknowns."""
        return self._slice_square.commutativity_decision()

    def validate_commutativity(self, *, check=True):
        r"""Use the square owner's validator on the retained triangle datum."""
        return self._slice_square.validate_commutativity(check=check)

    def __call__(self, element):
        return self.factor_morphism()(element)

    def _call_(self, element):
        return self.factor_morphism()(element)

    def __eq__(self, other: Any):
        if self is other:
            return True
        if parent(other) is not self.parent() or not isinstance(other, SubobjectMorphism):
            return False
        # A monomorphism cancels on the left: there is at most one factor
        # whose actual triangle commutes with the two chosen inclusions.
        if (
            self.commutativity_decision() is True
            and other.commutativity_decision() is True
        ):
            return True
        return self.factor_morphism() == other.factor_morphism()

    def __ne__(self, other: Any):
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self) -> int:
        return hash(id(self.parent()))

    def __mul__(self, other):
        if not isinstance(other, SubobjectMorphism) or not _precomposable(self, other):
            return NotImplemented
        parent_mor = self.parent().subobject_category().Mor(
            other.domain(), self.codomain()
        )
        # If j f = i and k g = j, then k (g f) = i.
        square = self._slice_square * other._slice_square
        return SubobjectMorphism(
            parent_mor, square.left(), _slice_square=square
        )


class SubobjectMor(CategoricalMor):
    Element = SubobjectMorphism

    def __init__(
        self,
        family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(
            self, family, domain, codomain
        )

    def subobject_category(self) -> SubobjectCategory:
        return self.base_category()

    @cached_method
    def _slice_mor(self):
        r"""The slice Mor whose fixed-edge square is this subobject Mor's triangle."""
        category = self.subobject_category()
        return category.slice_category().Mor(
            category.as_slice_object(self.domain()),
            category.as_slice_object(self.codomain()),
        )

    def _canonical_factor(self):
        factor = self.domain().inclusion().factor_through_or_none(
            self.codomain().inclusion()
        )
        if factor is None:
            raise ValueError(
                f"the subobject {self.domain()} is not contained in the subobject {self.codomain()}"
            )
        return factor

    def has_morphism(self) -> bool:
        return (
            self.domain().inclusion().factor_through_or_none(
                self.codomain().inclusion()
            )
            is not None
        )

    def canonical_morphism(self) -> SubobjectMorphism:
        return SubobjectMorphism(self, self._canonical_factor(), verify=False)

    def _element_constructor_(self, factor_morphism=None, *, check=False):
        match factor_morphism:
            case SubobjectMorphism():
                if factor_morphism.parent() is self:
                    factor_morphism.validate_commutativity(check=check)
                    return factor_morphism
                raise TypeError(f"{factor_morphism} belongs to another Mor; apply the functor between the categories")
            case None:
                result = self.canonical_morphism()
                result.validate_commutativity(check=check)
                return result
        return SubobjectMorphism(self, factor_morphism, verify=check)

    @object_level
    def identity(self) -> SubobjectMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        square = self._slice_mor().identity()
        return SubobjectMorphism(self, square.left(), _slice_square=square)


class SubobjectMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SubobjectMor


class SubobjectCategory(OwnedCategoryBase):
    r"""The category of represented subobjects of one fixed object.

    An object is an object ``A`` of the base category equipped with its chosen
    monomorphism ``A.inclusion(): A -> X``.  Morphisms are the commuting
    triangles between those inclusions.

    Unverified specimen: a represented module subobject retains its selected
    inclusion when its fixed-base placement and its Mor are requested::

        sage: from dzack_research.preamble.all import Modules, ZZ
        sage: from sage_extensions.refine import refine
        sage: submodule = ZZ.ideal(2)
        sage: inclusion = submodule.inclusion()
        sage: category = SubobjectCategory(Modules(ZZ), inclusion.codomain())
        sage: submodule in category
        True
        sage: category.super_categories()[0] is Modules(ZZ)
        True
        sage: _ = refine(submodule, category)
        sage: submodule in category
        True
        sage: Mor = category.Mor(submodule, submodule)
        sage: Mor is category.MorCategory().Of(submodule, submodule)
        True
        sage: identity = Mor.identity()
        sage: identity * identity == identity
        True
        sage: submodule.inclusion() is inclusion
        True
    """

    _MorCategory = SubobjectMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, base_category, base_object: (cls, id(base_category), id(base_object)))
    def __classcall__(cls, base_category: Category, base_object: Parent):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category, base_object)
        return typecall(cls, base_category, base_object)

    def __init__(self, base_category: Category, base_object: Parent) -> None:
        if base_object not in base_category:
            raise TypeError(
                f"subobjects of X in C need X an object of C = {base_category}, but {base_object} is not one"
            )
        self._base_category = base_category
        self._base_object = base_object
        super().__init__()

    def _make_named_class_key(self, name):
        return self._base_category, id(self._base_object)

    def base_category(self) -> Category:
        return self._base_category

    def base_object(self) -> ObjectOfCategory:
        return self._base_object

    def super_categories(self):
        r"""A subobject of an object of ``C`` is an object of ``C``.

        What the subobject additionally has is its chosen monomorphism into
        the fixed base object; forgetting that leaves an object of the base
        category, with every operation the base category owns.
        """
        return [self.base_category()]

    def slice_category(self) -> SliceCategory:
        r"""Return the slice ``C/X`` in which subobjects are monomorphisms."""
        return SliceCategory(self.base_category(), self.base_object())

    def monomorphism_category(self) -> _MonomorphismArrowCategory:
        r"""Return the monomorphism subcategory of the arrow category of ``C``."""
        return self.base_category().MonomorphismArrowCategory()

    @cached_method(key=lambda self, subobject: id(subobject))
    def as_slice_object(self, subobject: Parent) -> ObjectOfCategory:
        if subobject not in self:
            raise TypeError(f"{subobject} is not a subobject in {self}")
        return self.slice_category()(subobject.inclusion())

    def Mor(self, domain: Parent, codomain: Parent) -> SubobjectMor:
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two subobjects of its base object, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    def leq(self, left: Parent, right: Parent) -> bool:
        return self.Mor(left, right).has_morphism()

    def identity(self, subobject: Parent) -> SubobjectMorphism:
        return self.Mor(subobject, subobject).identity()

    def _repr_(self) -> str:
        return f"Subobjects of {self.base_object()}"


class SetSubobjectCategory(SliceCategory):
    r"""The subsets ``(A, i: A -> X)`` of ``X``: the objects of ``Set/X`` whose arrow is monic.

    The slice ``Set/X`` constructs a subset through the set owner on the
    data of the received ``A`` (``OWN-16``), so its points, membership and
    cardinality are those of ``A``.  This level adds the subobject lattice.
    """

    def super_categories(self):
        r"""A subset ``(A, i)`` of ``X`` is an object of ``Set/X`` whose arrow is monic.

        Monicity is the admission condition on ``i``; the inclusion into
        the monomorphisms of ``Ar(Set)`` is a functor, not a declaration
        (``CAT-16``, ``CAT-20``).

        A finite ambient set forces each represented subset to be finite;
        an infinite ambient set does not impose that categorical placement::

            sage: from dzack_research.preamble.all import Sets, NN
            sage: finite = Sets().Subobjects(Sets.Δ[2])
            sage: infinite = Sets().Subobjects(NN)
            sage: Sets().Finite() in finite.super_categories()
            True
            sage: Sets().Finite() in infinite.super_categories()
            False
        """
        from sage_extensions.categories.sets.set_categories import FiniteSets

        categories = [SliceCategory(self.base_category(), self.base_object())]
        base = self.base_object()
        if base in FiniteSets() or base.is_finite() is True:
            categories.append(FiniteSets())
        return categories

    def object(self, arrow, *, categories=(), construction_data=None, _engine=None):
        from sage_extensions.categories.sets.set_categories import FiniteSets

        domain = arrow.domain()
        if domain in FiniteSets() or domain.is_finite() is True:
            categories = (*categories, FiniteSets())
        return super().object(
            arrow, categories=categories, construction_data=construction_data, _engine=_engine
        )

    __call__ = object

    def admits_arrow(self, arrow: Morphism) -> bool:
        return (
            SliceCategory.admits_arrow(self, arrow)
            and self.base_category().MonomorphismArrowCategory().admits_arrow(arrow)
        )

    def cardinality(self):
        r"""The number of represented subsets of the fixed base set."""
        return self.base_object().power_set().cardinality()

    class ParentMethods:
        r"""A set ``A`` with its inclusion into ``X``; its points are those of ``A``, constructed through the set owner."""

        def is_contained_in(self, other):
            r"""Whether this subset lies in another subset of the same set.

            Finite enumerated domains decide the universal membership
            condition. Other domains retain the subset proposition; more
            structured subsets supply their defining inclusion criterion.
            """
            from sage_extensions.categories.sets.set_categories import EnumeratedSets, FiniteSets, Sets
            from sage_extensions.logic import AtomicProposition, conjunction, negation

            ambient = self.codomain()
            if other.codomain() is not ambient:
                raise ValueError("subset inclusion requires a common ambient set")
            power = ambient.power_set()
            if self is other or self is power.bottom() or other is power.top():
                return True
            if ambient in FiniteSets() and ambient in EnumeratedSets():
                return conjunction(
                    negation(conjunction((self.is_parent_of(member), negation(other.is_parent_of(member)))))
                    for member in ambient
                )
            points = self.inclusion().domain()
            if Sets().is_provably_finite(points) and points in EnumeratedSets():
                return conjunction(other.is_parent_of(self.inclusion()(point)) for point in points)
            return AtomicProposition("is_subset", self, other)

        def inclusion(self):
            return self.arrow()

        def domain(self):
            return self.inclusion().domain()

        def codomain(self):
            return self.inclusion().codomain()

        def __contains__(self, member):
            r"""Whether ``member`` names a point of \(X\) in the image of \(A\hookrightarrow X\)."""
            from sage_extensions.logic import conjunction

            base = self.codomain()
            match base.is_parent_of(member):
                case False:
                    return False
                case True:
                    return self.inclusion().image().is_parent_of(base(member))
                case membership:
                    # The inclusion image is a subset of the ambient set.
                    # Retain both defining membership conditions, and allow
                    # a proved exclusion from the image to decide the result.
                    return conjunction((membership, self.inclusion().image().is_parent_of(member)))

        is_parent_of = __contains__

        def characteristic_morphism(self):
            return self.inclusion().characteristic_morphism()

        def factor_through_or_none(self, target):
            return self.inclusion().factor_through_or_none(target.inclusion())

        def factor_through(self, target):
            return self.inclusion().factor_through(target.inclusion())

        def _set_subobject_category(self):
            from sage_extensions.categories.sets.set_categories import Sets

            return Sets().Subobjects(self.codomain())

        def _subset_from_predicate(self, other, predicate):
            r"""The subset of \(X\) cut out by ``predicate``, for two subsets of one \(X\)."""
            if other.codomain() is not self.codomain():
                raise ValueError(
                    f"cannot combine the subsets {self.domain()} and {other.domain()}: they are subsets of "
                    f"different sets {self.codomain()} and {other.codomain()}"
                )
            return self.codomain().power_set().from_predicate(predicate)

        def __le__(self, other):
            r"""\(A\subseteq B\): the inclusion of \(A\) factors through the inclusion of \(B\)."""
            if self is other:
                return True
            if other not in self._set_subobject_category():
                return False
            if other.codomain() is not self.codomain():
                return False
            return self.is_contained_in(other)

        def union(self, other):
            from sage_extensions.logic import conjunction, negation

            return self._subset_from_predicate(other, lambda member: negation(conjunction((
                negation(self.is_parent_of(member)), negation(other.is_parent_of(member)),
            ))))

        def intersection(self, other):
            from sage_extensions.logic import conjunction

            return self._subset_from_predicate(other, lambda member: conjunction((
                self.is_parent_of(member), other.is_parent_of(member),
            )))

        def difference(self, other):
            from sage_extensions.logic import conjunction, negation

            return self._subset_from_predicate(other, lambda member: conjunction((
                self.is_parent_of(member), negation(other.is_parent_of(member)),
            )))

        def symmetric_difference(self, other):
            from sage_extensions.logic import conjunction, negation

            def predicate(member):
                left = self.is_parent_of(member)
                right = other.is_parent_of(member)
                return negation(conjunction((
                    negation(conjunction((left, negation(right)))),
                    negation(conjunction((right, negation(left)))),
                )))

            return self._subset_from_predicate(other, predicate)

        def complement(self):
            from sage_extensions.logic import negation

            return self.codomain().power_set().from_predicate(lambda member: negation(self.is_parent_of(member)))

        def __or__(self, other):
            return self.union(other)

        def __eq__(self, other):
            r"""Two subsets of \(X\) are equal when they have the same members.

            Finite enumerated ambient sets admit pointwise characteristic
            comparison. Otherwise equality is mutual containment, retaining
            undecided inclusion propositions when necessary.
            """
            from sage_extensions.categories.sets.set_categories import (
                EnumeratedSets,
                FiniteSets,
            )
            from sage_extensions.logic import conjunction, negation

            if self is other:
                return True
            if other not in self._set_subobject_category():
                return False
            base = self.codomain()
            if base in FiniteSets() and base in EnumeratedSets():
                # Equality of subsets is equality of their characteristic
                # predicates, not Python equality of their truth values.
                # Either membership may remain undecided even over a finite
                # enumerated ambient set.
                # In particular, both implications for one point must be
                # evaluated from the same two membership propositions.
                return conjunction(
                    conjunction((
                        negation(conjunction((left, negation(right)))),
                        negation(conjunction((right, negation(left)))),
                    ))
                    for member in base
                    for left, right in ((self.is_parent_of(member), other.is_parent_of(member)),)
                )
            # Equality is still the conjunction of both inclusions when
            # neither subobject has a finite enumeration. Their inclusion
            # owners retain undecided containment as propositions rather
            # than converting the absence of a factor into noncontainment.
            return conjunction((self <= other, other <= self))

        def __ne__(self, other):
            from sage_extensions.logic import negation

            return negation(self == other)

        __hash__ = None

        def _repr_(self):
            return f"Subobject of {self.codomain()} defined by {self.domain()}"


class SuperobjectCategory(CosliceCategory):
    r"""The category of represented superobjects ``X -> B`` that are monic."""

    def super_categories(self):
        return [CosliceCategory(self.base_category(), self.base_object())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return super().admits_arrow(arrow) and self.base_category().MonomorphismArrowCategory().admits_arrow(arrow)

    def _repr_(self) -> str:
        return f"Superobjects of {self.base_object()}"


class CoveringObjectCategory(SliceCategory):
    r"""The category of covering objects ``A -> X`` that are epic."""

    def super_categories(self):
        return [SliceCategory(self.base_category(), self.base_object())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return super().admits_arrow(arrow) and self.base_category().EpimorphismArrowCategory().admits_arrow(arrow)

    def _repr_(self) -> str:
        return f"Covering objects of {self.base_object()}"


class CoveredObjectCategory(CosliceCategory):
    r"""The category of covered objects ``X -> B`` that are epic."""

    def super_categories(self):
        return [CosliceCategory(self.base_category(), self.base_object())]

    def admits_arrow(self, arrow: Morphism) -> bool:
        return super().admits_arrow(arrow) and self.base_category().EpimorphismArrowCategory().admits_arrow(arrow)

    def _repr_(self) -> str:
        return f"Covered objects of {self.base_object()}"


class FixedWideMorCategory(FixedRestrictedMorCategory):
    r"""The selected arrows in one existing Mor of the underlying category.

    Its selected underlying fixed Mor has the *same* endpoints; this does
    not equate the narrower arrow class with all underlying arrows::

        sage: from dzack_research.preamble.all import Sets
        sage: X = Sets.Δ[1]
        sage: wide = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
        sage: H = wide.Mor(X, X)
        sage: K = H.super_categories()[0]
        sage: K.domain_object() is X and K.codomain_object() is X
        True
    """

    def arrow_set(self) -> SageHomset:
        return _category_mor_parent(
            self.base_category().base_category(),
            self.domain_object(),
            self.codomain_object(),
        )

    underlying_mor = arrow_set

    def cardinality(self):
        r"""Count finite-set injections when this Mor restricts to monomorphisms.

        An injection from an m-element set to an n-element set is a choice
        of m distinct images in order, numbering n!/(n-m)! for m <= n.

            sage: from dzack_research.preamble.all import Sets
            sage: X = Sets.Δ[1]
            sage: wide = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
            sage: wide.Mor(X, X).cardinality()
            2
        """
        from math import factorial

        from sage_extensions.categories.sets.cardinals import cardinal
        from sage_extensions.categories.sets.set_categories import FiniteSets, Sets

        wide = self.base_category()
        source, target = self.domain_object(), self.codomain_object()
        if (
            wide.base_category() is Sets()
            and isinstance(wide.arrow_category(), _MonomorphismArrowCategory)
            and source in FiniteSets() and target in FiniteSets()
        ):
            m, n = int(source.cardinality()), int(target.cardinality())
            return cardinal(0 if m > n else factorial(n) // factorial(n - m))
        raise TypeError("the cardinality of this restricted Mor is not determined by a finite injection count")

    def super_categories(self) -> list[Category]:
        return [
            self.base_category().base_category().category_packet().Mors().Of(
                self.domain_object(),
                self.codomain_object(),
            )
        ]


class WideMorCategoryConstruction(_RestrictedMorCategoryOf):
    r"""Mor categories cut out by a wide subcategory's arrow predicate."""

    FixedCategoryClass = FixedWideMorCategory

    def _inherits_morphisms_from(
        self, supercategory: Category, domain: Parent, codomain: Parent
    ) -> bool:
        # The object sets agree, but the supplied predicate changes the arrows.
        # Sharing the underlying Mor does not make the inclusion full.
        return False

    def accepts(self, arrow: Morphism) -> bool:
        return self.base_category().admits(arrow)


class _WideSubcategory(OwnedCategoryBase):
    r"""A category with the same objects as ``C`` and a selected class of arrows.

    The selected arrows must include every identity and be closed under
    composition. These are hypotheses on the supplied mathematical class,
    not properties decidable by enumerating an arbitrary category.
    Each fixed Mor retains that class's predicate and the original arrow parent.

    The object datum is unchanged: the selected arrow class contributes no
    object structure. Object construction is the identity on the base's
    already-placed objects, and ``ObjectType`` and ``ElementType`` are the
    base's types. Membership reads that same placement; it never evaluates
    the arrow predicate, refines an input, or infers structure from its
    representation. This equality of object classes is not a reverse
    supercategory declaration and does not identify the two Mor theories.

    This is the identity-object case of Mathlib's
    ``CategoryTheory.InducedWideCategory`` (``Widesubcategory.lean``): the
    object type is unchanged and only the Hom type is restricted. The
    preamble's chosen arrow category supplies the multiplicative class;
    no second representation of an object or proof-object API is introduced.

    Unverified specimens: injections form a wide subcategory of sets. A
    noninjective map is an underlying set map, but is not an arrow here::

        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: from sage_extensions.categories.functors.core import IdentityFunctor, NaturalTransformation
        sage: from sage_extensions.categories.sets.set_categories import Sets
        sage: points = finite_ordered_set(("a", "b"))
        sage: injections = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
        sage: injections.super_categories()[0] is Sets()
        True
        sage: points in injections
        True
        sage: maps = Sets().Mor(points, points)
        sage: Mor = injections.Mor(points, points)
        sage: Mor is injections.MorCategory().Of(points, points)
        True
        sage: points.Mor(points, category=injections) is Mor
        True
        sage: Mor.arrow_set() is maps
        True
        sage: swap = maps(lambda point: {"a": "b", "b": "a"}[point])
        sage: collapse = maps(lambda point: "a")
        sage: Mor.accepts(swap), collapse in maps, Mor.accepts(collapse)
        (True, True, False)
        sage: Mor.object(swap).arrow() is swap
        True
        sage: injections.compose(swap, swap) == injections.identity(points)
        True
        sage: identity = IdentityFunctor(injections)
        sage: identity(swap) is swap
        True
        sage: identity(collapse)
        Traceback (most recent call last):
        ...
        TypeError: the supplied map is not a morphism of the functor's domain
        sage: eta = NaturalTransformation(identity, identity, lambda obj: collapse)
        sage: eta.component(points)
        Traceback (most recent call last):
        ...
        TypeError: the component is not a morphism of the common codomain category
        sage: arrows = injections.ArrowCategory()
        sage: obj = arrows(injections.identity(points))
        sage: arrows.Mor(obj, obj)(swap, swap).left() is swap
        True
        sage: arrows.Mor(obj, obj)(collapse, collapse)
        Traceback (most recent call last):
        ...
        ValueError: the left edge is not a morphism of the base category

    An underlying bijection still has to lie in the selected Mor; creating a
    runtime parent never replaces this admission check.
    """

    _MorCategory = WideMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, base_category, arrow_category: (cls, id(base_category), id(arrow_category)))
    def __classcall__(cls, base_category: Category, arrow_category: _SubcategoryOfArrows):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category, arrow_category)
        return typecall(cls, base_category, arrow_category)

    def __init__(self, base_category: Category, arrow_category: _SubcategoryOfArrows) -> None:
        if arrow_category.base_category() is not base_category:
            raise ValueError(
                f"the arrows of a wide subcategory of {base_category} must be arrows of {base_category}, but "
                f"they are arrows of {arrow_category.base_category()}"
            )
        self._base_category = base_category
        self._arrow_category = arrow_category
        super().__init__()

    def _make_named_class_key(self, name):
        return id(self._base_category), id(self._arrow_category)

    def base_category(self) -> Category:
        return self._base_category

    def arrow_category(self) -> _SubcategoryOfArrows:
        return self._arrow_category

    def super_categories(self):
        return [self.base_category()]

    @property
    def ObjectType(self) -> type[ObjectOfCategory]:
        r"""The unchanged object type; the arrow class adds no object datum."""
        return self.base_category().ObjectType

    @property
    def ElementType(self):
        r"""The unchanged element type of each base object."""
        return self.base_category().ElementType

    def __contains__(self, candidate: Any) -> bool:
        r"""Read placement in the object class fixed by this construction.

        The base owns this placement, including represented objects of Cat
        and fixed Mor categories. The selected predicate concerns arrows
        only and is consulted by the separate fixed Mor constructor.
        """
        return candidate in self.base_category()

    def object(self, obj: _Object) -> _Object:
        r"""Retain an already-placed base object, without copying or refining it."""
        if obj not in self:
            raise TypeError(
                f"{obj} is not an object of {self}, which has exactly the objects of {self.base_category()}"
            )
        return obj

    __call__ = object

    def _mor_endpoint(self, obj):
        r"""Use the base object's representation at the fixed-Mor boundary."""
        return self.base_category()._mor_endpoint(obj)

    def an_object(self):
        return self.object(self.base_category().an_object())

    def admits(self, arrow: Morphism) -> bool:
        r"""Whether ``arrow`` is one of the selected arrows."""
        return self.arrow_category().admits_arrow(arrow)

    def identity(self, obj: Parent) -> Morphism:
        identity = _category_mor_parent(self.base_category(), obj, obj).identity()
        if not _category_accepts_morphism(self, obj, obj, identity):
            raise ValueError(
                f"{self} does not contain the identity of {obj}, so it is not a subcategory"
            )
        return identity

    def compose(self, second: Morphism, first: Morphism) -> Morphism:
        if first.codomain() is not second.domain():
            raise ValueError(
                f"cannot compose {second} o {first}: {first} ends at {first.codomain()}, but {second} starts "
                f"at {second.domain()}"
            )
        if not _category_accepts_morphism(self, first.domain(), first.codomain(), first):
            raise ValueError(f"{first} is not a morphism of {self}")
        if not _category_accepts_morphism(self, second.domain(), second.codomain(), second):
            raise ValueError(f"{second} is not a morphism of {self}")
        composite = second * first
        if not _category_accepts_morphism(self, first.domain(), second.codomain(), composite):
            raise ValueError(
                f"{self} is not closed under composition: {second} o {first} is not one of its morphisms"
            )
        return composite

    def _repr_(self) -> str:
        return f"Wide subcategory of {self.base_category()} with arrows in {self.arrow_category()}"


class CoreMor(CategoricalMor):
    Element = CategoricalIsomorphism

    def _cardinality_decision(self):
        r"""``|Iso_C(X, Y)|``, this realization of the ``Sets`` and ``OwnedGroups`` cardinality hook.

        For finite sets of cardinality m and n the bijections number m! if
        m=n and zero otherwise; no chosen ordering is part of this statement.
        Any other vertex group ``Aut_C(X)`` is counted as a group
        (``_group_cardinality``), which this realization would otherwise
        replace.  Any other core Mor supplies no count (``None``).
        """
        from math import factorial

        from sage_extensions.categories.group.groups import OwnedGroups, _group_cardinality
        from sage_extensions.categories.sets.cardinals import cardinal
        from sage_extensions.categories.sets.set_categories import FiniteSets, Sets

        source, target = self.domain(), self.codomain()
        match self:
            case _ if (
                self.core_category().base_category() is Sets()
                and source in FiniteSets() and target in FiniteSets()
            ):
                m, n = int(source.cardinality()), int(target.cardinality())
                return cardinal(factorial(m) if m == n else 0)
            case _ if self in OwnedGroups():
                return _group_cardinality(self)
            case _:
                return None

    def __init__(
        self,
        family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
        *,
        category: Category | None = None,
    ) -> None:
        r"""``category`` refines the vertex-group placement of a specialized core Mor."""
        placement = self._vertex_group_placement(domain, codomain)
        if category is not None:
            placement = category if placement is None else Cat().meet((placement, category))
        CategoricalMor.__init__(self, family, domain, codomain, category=placement)
        if domain is codomain:
            self._initialize_vertex_group()

    def _initialize_vertex_group(self) -> None:
        r"""Make ``Aut(X)`` the vertex group of the core groupoid (protected; ``OWN-05``).

        Its ambient category (``ARC-07``) is that of groups, and it selects the
        generating family its base category computes (the core contract);
        selecting computes nothing until ``group_generators()`` first reads it.
        Callers: ``CoreMor.__init__`` and specialized core Mors that do not
        initialize through it (``LatticeIsometryMor``).
        """
        # A module-level import of groups here is circular (observed: ImportError
        # on ModuleMorphismMethods while loading the preamble), so it is read here.
        from sage_extensions.categories.group.groups import OwnedGroups

        self._constructing_category = OwnedGroups()
        self.select_group_generators(
            lambda: self.core_category().base_category()._core_automorphism_generators(self)
        )

    @staticmethod
    def _vertex_group_placement(domain: Parent, codomain: Parent) -> Category | None:
        r"""``Aut_C(X) = Core(C)(X, X)`` is the vertex group of the core groupoid.

        Composition, identity and inverse are those of the groupoid.  A
        specialized core Mor (lattice isometries) takes its group placement
        from here and refines it.
        """
        if domain is not codomain:
            return None
        from sage_extensions.categories.group.groups import OwnedGroups

        return OwnedGroups()

    def one(self) -> CategoricalIsomorphism:
        r"""The identity of ``Aut(X)``: the identity isomorphism of ``X``."""
        return self.identity()

    def core_category(self) -> _CoreCategory:
        return self.base_category()

    # Protected contract (OWN-05): the core decisions of a base category C.
    # Purpose: whether two objects of C are isomorphic, one isomorphism, the
    # generators of Aut(X), and an isomorphism whose (apex) component lies
    # in a supplied subgroup, are decisions C owns; no public operation of
    # an arbitrary C answers them.  Owner: CoreMor.  Callers: CoreMor's
    # is_empty, an_element, group_generators, an_element_in; no other.
    # Implementers: the base category C = core_category().base_category():
    #   C._core_isomorphism_witness(core_mor) -> element of core_mor or None;
    #   C._core_automorphism_generators(core_mor) -> finite ordered set of
    #       elements of core_mor = Aut(X) generating it;
    #   C._core_isomorphism_in(core_mor, subgroup) -> element or None.
    # Implemented by _FunctorCategory (marked diagrams, through the codomain
    # category), Lattices and Modules.  A base category without them fails
    # at the call.

    @cached_method
    def _isomorphism_witness(self):
        r"""One isomorphism, or ``None``: the base category's decision (its protected core contract)."""
        return self.core_category().base_category()._core_isomorphism_witness(self)

    def _emptiness_decision(self) -> bool:
        r"""``Iso_C(X, Y) = ∅``, supplied to the ``Sets`` emptiness hook: the base category's decision.

        ``is_empty`` is the one operation of ``Sets``, where every fixed Mor
        is placed (``CategoricalMor``); this realization supplies only the
        decision.  On a vertex group the group owner's hook answers first.
        """
        return self._isomorphism_witness() is None

    def an_element(self) -> CategoricalIsomorphism:
        r"""One isomorphism between the endpoints; an empty core Mor has none."""
        witness = self._isomorphism_witness()
        if witness is None:
            raise ValueError(f"there is no isomorphism {self.domain()} -> {self.codomain()}")
        return witness

    def an_element_in(self, subgroup) -> CategoricalIsomorphism | None:
        r"""An isomorphism whose apex component lies in ``subgroup``, or ``None``.

        For marked diagrams, ``subgroup`` is a subgroup of the automorphism
        group of the common apex; the base category owns the search.
        """
        return self.core_category().base_category()._core_isomorphism_in(self, subgroup)

    def __call__(self, forward, inverse=None, **kwargs):
        if inverse is not None:
            return super().__call__((forward, inverse), **kwargs)
        return super().__call__(forward, **kwargs)

    def _element_constructor_(self, forward, inverse=None):
        match forward:
            case CategoricalIsomorphism() if inverse is None:
                if forward.parent() is self:
                    return forward
                raise TypeError(f"{forward} belongs to another Mor; apply the functor between the categories")
        if inverse is None:
            forward, inverse = forward
        self._require_base_morphisms(forward, inverse)
        return self.element_class(self, forward, lambda: inverse)

    def _require_base_morphisms(self, forward: Morphism, inverse: Morphism) -> None:
        base = self.core_category().base_category()
        if not _category_accepts_morphism(base, self.domain(), self.codomain(), forward):
            raise ValueError(
                f"the isomorphism {self.domain()} -> {self.codomain()} needs {forward} to be a morphism of {base}"
            )
        if not _category_accepts_morphism(base, self.codomain(), self.domain(), inverse):
            raise ValueError(
                f"the isomorphism {self.domain()} -> {self.codomain()} needs the inverse {inverse} to be a "
                f"morphism of {base}"
            )

    def _from_known_inverse_pair(self, forward, inverse):
        r"""Construct an isomorphism from an inverse pair proved by its owner."""
        self._require_base_morphisms(forward, inverse)
        return self._from_inverse_computation(forward, lambda: inverse)

    def _from_inverse_computation(self, forward, inverse_computation):
        r"""The isomorphism ``forward``, whose inverse ``inverse_computation()`` is asked on first request.

        Protected (``OWN-05``): the caller has proved that ``forward`` is an
        arrow of the base category with that inverse; a composite of two
        isomorphisms of this core (``CategoricalIsomorphism.__mul__``) is the
        first caller.  Nothing is checked or composed here (``OWN-22``).
        """
        return self.element_class(self, forward, inverse_computation, verify=False)

    @object_level
    def identity(self) -> CategoricalIsomorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        base = self.core_category().base_category()
        identity = _category_mor_parent(base, self.domain(), self.domain()).identity()
        return self._from_known_inverse_pair(identity, identity)


class CoreMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = CoreMor


class _CoreCategory(_WideSubcategory):
    r"""The wide subcategory whose arrows are represented isomorphisms.

    Mathlib's ``CategoryTheory.Core`` (``Core.lean``) supplies the same
    objects and inverse-bearing Hom data. Here the wide-subcategory
    construction retains those exact objects, while ``CoreMor`` constructs
    the forward/inverse pair in the selected base Mor theory.
    """

    _MorCategory = CoreMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, base_category: (cls, id(base_category)))
    def __classcall__(cls, base_category: Category):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(base_category)
        return typecall(cls, base_category)

    def __init__(self, base_category: Category) -> None:
        super().__init__(base_category, _IsoArrowCategory(base_category))

    def Core(self) -> Category:
        r"""A core is already a groupoid, so taking its core changes nothing."""
        return self

    def Mor(self, domain: Parent, codomain: Parent) -> CoreMor:
        return self.MorCategory().Of(domain, codomain)

    def identity(self, obj: Parent) -> CategoricalIsomorphism:
        return self.Mor(obj, obj).identity()

    def _repr_(self) -> str:
        return f"Core of {self.base_category()}"


def _core_mor(
    domain: Parent,
    codomain: Parent,
    *,
    base_category: Category | None = None,
) -> CoreMor:
    r"""Return the core Mor in the stated arrow category.

    Endpoint categories can be joins carrying several independent structures
    whose morphism theories are intentionally not identified.  When an arrow
    already names its mathematical Mor owner, use that owner rather than
    reconstructing a Mor theory from the endpoints alone.
    """
    if base_category is None:
        category = Cat().join((domain.category(), codomain.category()))
    else:
        category = base_category
    return category.Core().Mor(domain, codomain)


def _represented_morphism_category(forward: Morphism, inverse: Morphism) -> Category | None:
    r"""Return the common category whose Mor categories hold both arrows, if they share one."""
    homs = (forward.parent(), inverse.parent())
    match homs:
        case (forward_mor, inverse_mor) if (
            forward_mor in MorCategories()
            and inverse_mor in MorCategories()
            and forward_mor.base_category() is inverse_mor.base_category()
        ):
            return forward_mor.base_category()
        case _:
            return None


def _isomorphism_from_known_inverse_pair(
    forward, inverse, *, base_category: Category | None = None
):
    r"""Transport a previously proved inverse pair in the selected arrow theory.

    An induced Aut functor supplies its target category: its image arrows may
    retain stronger parents, which must not choose a different target core.
    Without a selected target, use the pair's common represented Mor theory.
    The selected core still admits both arrows; this parameter changes their
    mathematical ambient category, not their admission obligations.
    """
    match base_category:
        case None:
            base_category = _represented_morphism_category(forward, inverse)
    return _core_mor(
        forward.domain(),
        forward.codomain(),
        base_category=base_category,
    )._from_known_inverse_pair(forward, inverse)


__all__ = [
    "ArrowMor",
    "CategoricalIsomorphism",
    "CommutativeSquare",
    "CoreMor",
    "CosliceCategory",
    "CoveredObjectCategory",
    "CoveringObjectCategory",
    "SliceCategory",
    "SubobjectCategory",
    "SetSubobjectCategory",
    "SubobjectMor",
    "SubobjectMorphism",
    "SuperobjectCategory",
]
