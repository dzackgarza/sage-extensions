r"""Diagrams, cones, cocones, and selected finite product constructions."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.element import parent
from sage.structure.parent import Parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.cat import (
    Cat,
    _FunctorCategory,
)
from sage_extensions.categories.abstract_categories.functors import DiscreteCategory
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    _precomposable,
    MorCategoryConstruction,
    _category_accepts_morphism,
    _category_mor_parent,
)
from sage_extensions.categories.abstract_categories.objects import Objects as OwnedObjects
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.functors.core import Functor, NaturalTransformation
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import IndexedFamily, indexed_family
from sage_extensions.categories.sets.set_categories import EnumeratedSets, FiniteSets, Sets
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import Category as OwnedCategoryBase
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

if TYPE_CHECKING:
    from sage_extensions.logic import Predicate


class _DiagramCategory(_FunctorCategory):
    r"""The functor category ``[J,C]`` of diagrams of one shape."""

    @staticmethod
    @cached_function(key=lambda cls, index_category, target_category: (cls, id(index_category), id(target_category)))
    def __classcall__(cls, index_category: Category, target_category: Category):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(index_category, target_category)
        return typecall(cls, index_category, target_category)

    def __init__(self, index_category: Category, target_category: Category) -> None:
        super().__init__(Cat(), index_category, target_category)

    def index_category(self) -> Category:
        return self.domain_category()

    def target_category(self) -> Category:
        return self.codomain_category()

    def base_index_category(self) -> Category:
        r"""Return the index before any variance specialization; covariant diagrams use ``J`` itself."""
        return self.index_category()

    def super_categories(self):
        return [Cat().Mor(self.index_category(), self.target_category())]

    class ParentMethods:
        r"""Operations of a represented diagram, inherited by every specialization."""

        def index_category(self):
            return self.category().index_category()

        def target_category(self):
            return self.category().target_category()

        def base_index_category(self):
            return self.category().base_index_category()

        def stage(self, index):
            r"""Return the diagram value at one represented index object."""
            return self.functor()(index)

        def transition(self, morphism):
            r"""Return the diagram image of one represented indexing arrow."""
            return self.functor()(morphism)



class DirectedSystem(_DiagramCategory):
    r"""A diagram category whose index category represents a directed order."""


class InverseSystem(_DiagramCategory):
    r"""The diagram category ``[J^op,C]`` for inverse systems indexed by ``J``."""

    def __init__(self, index_category: Category, target_category: Category) -> None:
        self._base_index_category = index_category
        super().__init__(index_category.opposite(), target_category)

    def base_index_category(self) -> Category:
        r"""Return ``J`` when this inverse system category is ``[J^op,C]``."""
        return self._base_index_category



class PosetMorphism(Morphism):
    r"""The unique arrow ``p -> q`` of a thin poset category when ``p <= q``."""

    def __init__(self, parent) -> None:
        Morphism.__init__(self, parent)

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return self.parent().poset_category().Mor(other.domain(), self.codomain()).unique()

    def __eq__(self, other) -> bool:
        return parent(other) is self.parent()

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(id(self.parent()))


class PosetMor(CategoricalMor):
    Element = PosetMorphism

    def poset_category(self):
        return self.base_category()

    def _cardinality_decision(self):
        category = self.poset_category()
        return cardinal(
            1
            if category.le(self.domain().value(), self.codomain().value())
            else 0
        )

    @cached_method
    def unique(self):
        if self.cardinality() != cardinal(1):
            raise ValueError(
                f"there is no arrow {self.domain()} -> {self.codomain()} in the poset: {self.domain()} is not "
                f"<= {self.codomain()}"
            )
        return PosetMorphism(self)

    def _element_constructor_(self, value=None):
        if value is not None and value is not self.unique():
            raise ValueError(
                f"Mor({self.domain()}, {self.codomain()}) in a poset has at most one arrow, and {value} is not it"
            )
        return self.unique()

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity arrow exists only on Mor(x, x), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self.unique()


class PosetMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = PosetMor


class PosetCategory(OwnedCategory):
    r"""The thin category attached to an owned partially ordered set ``P``.

    Objects are the points of ``P`` and there is one arrow ``p -> q`` exactly
    when ``p <= q``.  The object family is lazy, so an infinite poset remains
    an infinite represented indexing category rather than an eagerly traversed
    sequence.  ``le`` may be supplied when the owned set carries its order only
    by construction rather than by element comparison.
    """

    _MorCategory = PosetMorCategoryConstruction

    class ParentMethods:
        def __init__(self, value, **rest) -> None:
            self._value = value
            super().__init__(**rest)

        def value(self):
            return self._value

        def _repr_(self) -> str:
            return repr(self.value())

    def __init__(self, ordered_set, le=None) -> None:
        if ordered_set not in Sets():
            raise TypeError(
                f"a poset category is built on a set, but {ordered_set} is not in the category of sets"
            )
        self._ordered_set = ordered_set
        self._le = le
        self._objects = indexed_family(
            ordered_set,
            lambda value: _object_of(self, value=value),
            name=f"Objects of the poset category on {ordered_set}",
        )
        super().__init__()

    def _make_named_class_key(self, name):
        return self._ordered_set, self._le

    def super_categories(self):
        return [OwnedObjects()]

    def object_set(self):
        return self._ordered_set

    def objects(self):
        return self._objects

    def __call__(self, value):
        return self._objects(self._ordered_set(value))

    def le(self, left, right) -> bool:
        left = self._ordered_set(left)
        right = self._ordered_set(right)
        if self._le is not None:
            return bool(self._le(left, right))
        return bool(left <= right)

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two of its objects, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    def identity(self, obj):
        return self.Mor(obj, obj).identity()

    @cached_method
    def arrows(self):
        assert self.object_set() in FiniteSets(), (
            f"cannot list the arrows of {self}: its set of objects {self.object_set()} is not finite; an "
            "infinite poset is given by its order relation"
        )
        return finite_ordered_set(
            tuple(
                self.Mor(self(left), self(right)).unique()
                for left in self.object_set()
                for right in self.object_set()
                if self.le(left, right)
            )
        )


class _TwoLegDiagram(Functor):
    r"""A cospan ``X -> Z <- Y`` or span ``X <- Z -> Y`` in one category.

    The diagram is a functor on the existing finite-poset category with three
    objects; the selected arrows and their actual endpoints are retained.
    """

    def __init__(self, left, right, target_category, *, cospan):
        if cospan:
            if left.codomain() is not right.codomain():
                raise ValueError("a cospan needs two morphisms with one codomain")
        elif left.domain() is not right.domain():
            raise ValueError("a span needs two morphisms with one domain")
        if any(
            endpoint not in target_category
            for endpoint in (left.domain(), right.domain(), left.codomain(), right.codomain())
        ):
            raise TypeError(
                f"the two-leg diagram of {left} and {right} is not a diagram in {target_category}"
            )
        self._left, self._right = left, right
        self._cospan = cospan
        shape = PosetCategory(
            finite_ordered_set((0, 1, 2)),
            le=lambda source, target: (
                source == target
                or (target == 2 if cospan else source == 2)
            ),
        )
        super().__init__(shape, target_category)

    def _apply_object(self, obj):
        position = int(obj.value())
        if position == 0:
            return self._left.domain() if self._cospan else self._left.codomain()
        if position == 1:
            return self._right.domain() if self._cospan else self._right.codomain()
        return self._left.codomain() if self._cospan else self._left.domain()

    def _apply_morphism(self, arrow):
        if arrow.domain() is arrow.codomain():
            obj = self(arrow.domain())
            return _category_mor_parent(self.codomain(), obj, obj).identity()
        branch = int((arrow.domain() if self._cospan else arrow.codomain()).value())
        if branch == 0:
            return self._left
        if branch == 1:
            return self._right
        raise ValueError("a two-leg diagram has exactly two nonidentity morphisms")


class FiniteOrdinalMorphism(Morphism):
    r"""The unique arrow ``i -> j`` in a finite ordinal category when ``i <= j``."""

    def __init__(self, parent) -> None:
        Morphism.__init__(self, parent)

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return self.parent().ordinal_category().Mor(other.domain(), self.codomain()).unique()

    def __eq__(self, other) -> bool:
        return parent(other) is self.parent()

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(id(self.parent()))


class FiniteOrdinalMor(CategoricalMor):
    Element = FiniteOrdinalMorphism

    def ordinal_category(self):
        return self.base_category()

    def _cardinality_decision(self):
        return cardinal(1 if self.domain().position() <= self.codomain().position() else 0)

    @cached_method
    def unique(self):
        if self.cardinality() != cardinal(1):
            raise ValueError(
                f"there is no arrow {self.domain()} -> {self.codomain()} in a finite ordinal: arrows go only "
                "from smaller to larger elements"
            )
        return FiniteOrdinalMorphism(self)

    def _element_constructor_(self, value=None):
        if value is not None and value is not self.unique():
            raise ValueError(
                f"Mor({self.domain()}, {self.codomain()}) in a finite ordinal has at most one arrow, and "
                f"{value} is not it"
            )
        return self.unique()

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity arrow exists only on Mor(x, x), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self.unique()


class FiniteOrdinalMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = FiniteOrdinalMor


class FiniteOrdinalCategory(OwnedCategory):
    r"""The category attached to the finite total order ``0 < ... < n-1``."""

    _MorCategory = FiniteOrdinalMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, size: (cls, int(size)))
    def __classcall__(cls, size):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(size)
        return typecall(cls, size)

    class ParentMethods:
        def __init__(self, position, **rest) -> None:
            self._position = int(position)
            super().__init__(**rest)

        def position(self) -> int:
            return self._position

        def _repr_(self) -> str:
            return str(self.position())

    def __init__(self, size) -> None:
        size = int(size)
        if size < 0:
            raise ValueError(f"the finite ordinal category [n] needs n >= 0, but n = {size}")
        self._object_set = Sets.Δ[size - 1]
        self._objects = indexed_family(
            self._object_set,
            lambda position: _object_of(self, position=int(position)),
            name="Objects of a finite ordinal category",
        )
        super().__init__()

    def super_categories(self):
        return [OwnedObjects()]

    def object_set(self):
        return self._object_set

    def objects(self):
        return self._objects

    def __call__(self, position):
        return self._objects(self._object_set(position))

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two of its objects, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    def identity(self, obj):
        return self.Mor(obj, obj).identity()

    @cached_method
    def arrows(self):
        return finite_ordered_set(
            tuple(
                self.Mor(self(i), self(j)).unique()
                for i in self.object_set()
                for j in self.object_set()
                if int(i) <= int(j)
            )
        )


class FiniteSequenceDiagram(Functor):
    r"""A finite composable sequence, with all composites derived from its transitions."""

    def __init__(self, objects, transitions, target_category: Category) -> None:
        self._objects = tuple(objects)
        self._transitions = tuple(transitions)
        if len(self._transitions) != max(0, len(self._objects) - 1):
            raise ValueError(
                f"a sequence of {len(self._objects)} objects needs {max(0, len(self._objects) - 1)} maps between "
                f"consecutive objects, but {len(self._transitions)} were given"
            )
        if any(obj not in target_category for obj in self._objects):
            raise TypeError(
                f"every object of the sequence must lie in {target_category}, but the objects are {self._objects}"
            )
        for position, transition in enumerate(self._transitions):
            if (
                transition.domain() is not self._objects[position]
                or transition.codomain() is not self._objects[position + 1]
            ):
                raise ValueError(
                    f"the map at position {position} of the sequence must be a map {self._objects[position]} -> "
                    f"{self._objects[position + 1]}, but {transition} is a map {transition.domain()} -> "
                    f"{transition.codomain()}"
                )
        self._shape = FiniteOrdinalCategory(len(self._objects))
        super().__init__(self._shape, target_category)

    def objects(self):
        return indexed_family(
            self.domain().object_set(),
            lambda position: self._objects[int(position)],
            name="Objects of a finite sequence diagram",
        )

    def transitions(self):
        labels = Sets.Δ[len(self._transitions) - 1]
        return indexed_family(
            labels,
            lambda position: self._transitions[int(position)],
            name="Transitions of a finite sequence diagram",
        )

    def _apply_object(self, obj):
        return self._objects[obj.position()]

    def _apply_morphism(self, morphism):
        source = morphism.domain().position()
        target = morphism.codomain().position()
        if source == target:
            image = self._objects[source]
            return _category_mor_parent(self.codomain(), image, image).identity()
        composite = self._transitions[source]
        for position in range(source + 1, target):
            composite = self._transitions[position] * composite
        return composite


class _FiniteSequenceFunctorCategory(_FunctorCategory):
    r"""The canonical functor category on a finite ordinal, with its adjacent arrows."""

    def __call__(self, functor: Functor | tuple[Morphism, ...] | list[Morphism]):
        r"""Read a functor or its ordered family of consecutive arrows."""
        if isinstance(functor, (tuple, list)):
            transitions = tuple(functor)
            size = int(self.domain_category().object_set().cardinality())
            expected = max(0, size - 1)
            if len(transitions) != expected:
                raise ValueError(
                    f"a diagram on a finite ordinal with {size} objects needs {expected} adjacent arrows, "
                    f"but {len(transitions)} were given"
                )
            if size == 1:
                raise ValueError(
                    "an empty transition family does not specify the object of a one-object diagram; "
                    "supply the actual functor"
                )
            base = self.codomain_category()
            for transition in transitions:
                if not isinstance(transition, (Morphism, CategoricalArrow)) or not _category_accepts_morphism(
                    base, transition.domain(), transition.codomain(), transition
                ):
                    raise TypeError(
                        f"each transition must be a morphism in {base}, but got {transition}"
                    )
            objects = (
                (transitions[0].domain(), *(transition.codomain() for transition in transitions))
                if transitions else ()
            )
            functor = FiniteSequenceDiagram(objects, transitions, base)
        return super().__call__(functor)

    class ParentMethods:
        @cached_method
        def arrows(self):
            r"""Return adjacent arrows with their ordinal positions and repetitions."""
            functor = self.functor()
            shape = functor.domain()
            length = max(0, int(shape.object_set().cardinality()) - 1)
            return indexed_family(
                Sets.Δ[length - 1],
                lambda position: functor(
                    shape.Mor(shape(int(position)), shape(int(position) + 1)).unique()
                ),
                name="Adjacent arrows of a finite sequence",
            )


class ParallelPairMorphism(Morphism):
    r"""One arrow of the walking parallel-pair category ``0 ⇉ 1``."""

    def __init__(self, parent, name: str) -> None:
        Morphism.__init__(self, parent)
        self._name = name

    def name(self) -> str:
        return self._name

    def is_identity(self) -> bool:
        return self.domain() is self.codomain()

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        if self.is_identity():
            return other
        if other.is_identity():
            return self
        raise ValueError(
            f"the walking parallel pair has no composite {self} o {other} of two non-identity arrows"
        )

    def __eq__(self, other) -> bool:
        return parent(other) is self.parent() and other.name() == self.name()

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((id(self.parent()), self.name()))


class ParallelPairMor(CategoricalMor):
    Element = ParallelPairMorphism

    def __init__(self, family, domain, codomain) -> None:
        CategoricalMor.__init__(self, family, domain, codomain)

    def parallel_pair_category(self):
        return self.base_category()

    def _cardinality_decision(self):
        category = self.parallel_pair_category()
        if self.domain() is self.codomain():
            return cardinal(1)
        if self.domain() is category.source() and self.codomain() is category.target():
            return cardinal(2)
        return cardinal(0)

    def _element_constructor_(self, name=None):
        category = self.parallel_pair_category()
        if self.domain() is self.codomain():
            if name not in (None, "identity"):
                raise ValueError(
                    f"Mor({self.domain()}, {self.domain()}) in the walking parallel pair contains only the identity, "
                    f"but got {name!r}"
                )
            return ParallelPairMorphism(self, "identity")
        if self.domain() is category.source() and self.codomain() is category.target():
            if name not in ("left", "right"):
                raise ValueError(
                    f"the two parallel arrows 0 -> 1 are named 'left' and 'right', but got {name!r}"
                )
            return ParallelPairMorphism(self, name)
        raise ValueError(
            f"the walking parallel pair has no arrow {self.domain()} -> {self.codomain()}"
        )

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity arrow exists only on Mor(x, x), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self()


class ParallelPairMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ParallelPairMor


class ParallelPairCategory(OwnedCategory):
    r"""The walking parallel pair ``0 ⇉ 1``."""

    _MorCategory = ParallelPairMorCategoryConstruction

    class ParentMethods:
        def __init__(self, position, **rest) -> None:
            self._position = int(position)
            super().__init__(**rest)

        def position(self) -> int:
            return self._position

        def _repr_(self) -> str:
            return str(self.position())

    def __init__(self) -> None:
        self._positions = finite_ordered_set((0, 1))
        self._objects = indexed_family(
            self._positions,
            lambda position: _object_of(self, position=position),
            name="Objects of the walking parallel pair",
        )
        super().__init__()

    def super_categories(self):
        return [OwnedObjects()]

    def object_set(self):
        return self._positions

    def objects(self):
        return self._objects

    def source(self):
        return self._objects[0]

    def target(self):
        return self._objects[1]

    def __call__(self, position):
        return self._objects[int(position)]

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in the walking parallel pair needs two of its objects, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    @cached_method
    def left(self):
        return self.Mor(self.source(), self.target())("left")

    @cached_method
    def right(self):
        return self.Mor(self.source(), self.target())("right")

    def identity(self, obj):
        return self.Mor(obj, obj).identity()


class ParallelPairDiagram(Functor):
    r"""A diagram ``A ⇉ B`` retaining its two parallel arrows."""

    def __init__(self, left: Morphism, right: Morphism, target_category: Category) -> None:
        if left.domain() is not right.domain() or left.codomain() is not right.codomain():
            raise ValueError(
                f"a parallel pair f, g: X -> Y needs maps with one domain and one codomain, but {left} is "
                f"{left.domain()} -> {left.codomain()} and {right} is {right.domain()} -> {right.codomain()}"
            )
        self._left = left
        self._right = right
        self._shape = ParallelPairCategory()
        super().__init__(self._shape, target_category)

    def left(self):
        return self._left

    def right(self):
        return self._right

    def source_object(self):
        return self.left().domain()

    def target_object(self):
        return self.left().codomain()

    def _apply_object(self, obj):
        if obj is self.domain().source():
            return self.source_object()
        if obj is self.domain().target():
            return self.target_object()
        raise ValueError(f"{obj} is not an object of the walking parallel pair")

    def _apply_morphism(self, morphism):
        if morphism.is_identity():
            image = self(morphism.domain())
            return _category_mor_parent(self.codomain(), image, image).identity()
        if morphism.name() == "left":
            return self.left()
        if morphism.name() == "right":
            return self.right()
        raise ValueError(f"{morphism} is not an arrow of the walking parallel pair")


@cached_function(key=lambda left, right, target_category: (id(left), id(right), id(target_category)))
def _parallel_pair_diagram(left: Morphism, right: Morphism, target_category: Category) -> ParallelPairDiagram:
    r"""Return the selected diagram object for one represented parallel pair.

    Equalizers and coequalizers of the same two arrows have the same source
    diagram ``A ⇉ B``.  Retaining one diagram object lets a natural
    transformation of that diagram induce both universal maps without
    manufacturing a second, merely isomorphic indexing presentation.
    """
    return ParallelPairDiagram(left, right, target_category)


_MISSING_PARALLEL_FAMILY_LABEL = object()


class ParallelFamilyMorphism(Morphism):
    r"""One arrow of the walking category for an indexed parallel family."""

    def __init__(self, parent, label=_MISSING_PARALLEL_FAMILY_LABEL) -> None:
        Morphism.__init__(self, parent)
        self._label = label

    def is_identity(self) -> bool:
        return self.domain() is self.codomain()

    def label(self):
        if self.is_identity():
            raise ValueError(f"the identity {self} has no parallel-family label")
        return self._label

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        if self.is_identity():
            return other
        if other.is_identity():
            return self
        raise ValueError(
            f"the walking parallel-family category has no composite {self} o {other} of two non-identity arrows"
        )

    def __eq__(self, other) -> bool:
        if parent(other) is not self.parent():
            return False
        if self.is_identity():
            return True
        return (self.label() == other.label()) is True

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        # Labels of an owned set need not themselves be hashable.  Equal arrows
        # already have the same fixed Mor parent, so the parent identity is a
        # valid (deliberately coarse) hash.
        return hash(id(self.parent()))


class ParallelFamilyMor(CategoricalMor):
    r"""A fixed Mor in the walking category for an indexed parallel family."""

    Element = ParallelFamilyMorphism

    def parallel_family_category(self):
        return self.base_category()

    def _cardinality_decision(self):
        category = self.parallel_family_category()
        if self.domain() is self.codomain():
            return cardinal(1)
        if self.domain() is category.source() and self.codomain() is category.target():
            return cardinal(category.index_set().cardinality())
        return cardinal(0)

    def _element_constructor_(self, label=_MISSING_PARALLEL_FAMILY_LABEL):
        category = self.parallel_family_category()
        if self.domain() is self.codomain():
            if label is not _MISSING_PARALLEL_FAMILY_LABEL:
                raise ValueError(
                    f"Mor({self.domain()}, {self.domain()}) in the walking parallel-family category contains "
                    f"only the identity, but got the label {label!r}"
                )
            return ParallelFamilyMorphism(self)
        if self.domain() is category.source() and self.codomain() is category.target():
            if label is _MISSING_PARALLEL_FAMILY_LABEL:
                raise ValueError(
                    f"an arrow {self.domain()} -> {self.codomain()} in the walking parallel-family category "
                    "needs its family label"
                )
            return ParallelFamilyMorphism(self, category.index_set()(label))
        raise ValueError(
            f"the walking parallel-family category has no arrow {self.domain()} -> {self.codomain()}"
        )

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity arrow exists only on Mor(x, x), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self()


class ParallelFamilyMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ParallelFamilyMor


class ParallelFamilyCategory(OwnedCategory):
    r"""The walking category ``0 ⇉_I 1`` for a represented indexing set ``I``.

    Its nonidentity arrows are indexed by ``I`` itself.  The indexing set may
    be infinite or nonenumerable; finiteness belongs to a particular realization
    of a wide (co)equalizer, not to the diagram that defines it.
    """

    _MorCategory = ParallelFamilyMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, index_set: (cls, id(index_set)))
    def __classcall__(cls, index_set: Parent):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(index_set)
        return typecall(cls, index_set)

    class ParentMethods:
        def __init__(self, position, **rest) -> None:
            self._position = int(position)
            super().__init__(**rest)

        def position(self) -> int:
            return self._position

        def _repr_(self) -> str:
            return str(self.position())

    def __init__(self, index_set: Parent) -> None:
        if index_set not in Sets():
            raise TypeError(
                f"a parallel-family category is indexed by a set, but {index_set} is not a set"
            )
        self._index_set = index_set
        self._positions = finite_ordered_set((0, 1))
        self._objects = indexed_family(
            self._positions,
            lambda position: _object_of(self, position=position),
            name="Objects of the walking parallel-family category",
        )
        super().__init__()

    def _make_named_class_key(self, name):
        return id(self._index_set)

    def super_categories(self):
        return [OwnedObjects()]

    def index_set(self):
        return self._index_set

    def object_set(self):
        return self._positions

    def objects(self):
        return self._objects

    def source(self):
        return self._objects[0]

    def target(self):
        return self._objects[1]

    def __call__(self, position):
        return self._objects[int(position)]

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two of its objects, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    def arrow(self, label):
        return self.Mor(self.source(), self.target())(label)

    def identity(self, obj):
        return self.Mor(obj, obj).identity()


class ParallelFamilyDiagram(Functor):
    r"""A diagram ``A ⇉_I B`` retaining its indexed family of parallel arrows."""

    def __init__(self, morphisms: IndexedFamily, target_category: Category) -> None:
        if morphisms.cardinality() == cardinal(0):
            raise ValueError(
                "a parallel-family diagram needs a nonempty family: an empty family does not retain its "
                "common source and target"
            )
        reference = morphisms.value(morphisms.index_set().an_element())
        match reference:
            case Morphism() | CategoricalArrow():
                pass
            case _:
                raise TypeError(
                    f"a parallel-family diagram needs morphisms as its values, but the family contains {reference}"
                )
        if not _category_accepts_morphism(
            target_category,
            reference.domain(),
            reference.codomain(),
            reference,
        ):
            raise TypeError(
                f"a parallel-family diagram in {target_category} needs arrows of that category, but contains {reference}"
            )
        self._morphisms = morphisms
        self._reference = reference
        self._shape = ParallelFamilyCategory(morphisms.index_set())
        super().__init__(self._shape, target_category)

    def morphisms(self) -> IndexedFamily:
        return self._morphisms

    def reference(self) -> Morphism:
        return self._reference

    def source_object(self):
        return self.reference().domain()

    def target_object(self):
        return self.reference().codomain()

    def _apply_object(self, obj):
        if obj is self.domain().source():
            return self.source_object()
        if obj is self.domain().target():
            return self.target_object()
        raise ValueError(f"{obj} is not an object of the walking parallel-family category")

    def _apply_morphism(self, morphism):
        if morphism.is_identity():
            image = self(morphism.domain())
            return _category_mor_parent(self.codomain(), image, image).identity()
        image = self.morphisms().value(morphism.label())
        match image:
            case Morphism() | CategoricalArrow() if (
                image.domain() is self.source_object()
                and image.codomain() is self.target_object()
                and _category_accepts_morphism(
                    self.codomain(), image.domain(), image.codomain(), image
                )
            ):
                return image
            case _:
                raise ValueError(
                    f"the family defining {self} is not parallel in {self.codomain()}: the arrow at "
                    f"{morphism.label()!r} is {image}"
                )


@cached_function(key=lambda morphisms, target_category: (id(morphisms), id(target_category)))
def _parallel_family_diagram(
    morphisms: IndexedFamily,
    target_category: Category,
) -> ParallelFamilyDiagram:
    r"""Return the selected diagram object for one represented parallel family."""
    return ParallelFamilyDiagram(morphisms, target_category)


class RestrictedDiagram(Functor):
    r"""The precomposition ``D ∘ u`` retaining ``D`` and the indexing functor ``u``."""

    def __init__(self, diagram: Functor, indexing_functor: Functor) -> None:
        if indexing_functor.codomain() is not diagram.domain():
            raise ValueError(
                f"restricting the diagram {diagram} along {indexing_functor} needs a functor into "
                f"{diagram.domain()}, but it ends at {indexing_functor.codomain()}"
            )
        self._diagram = diagram
        self._indexing_functor = indexing_functor
        super().__init__(indexing_functor.domain(), diagram.codomain())

    def original_diagram(self):
        return self._diagram

    def indexing_functor(self):
        return self._indexing_functor

    def _apply_object(self, obj):
        return self.original_diagram()(self.indexing_functor()(obj))

    def _apply_morphism(self, morphism):
        return self.original_diagram()(self.indexing_functor()(morphism))


class SelectedLimitConstruction(SageObject):
    r"""A selected universal cone over one represented diagram.

    The cone is an object of ``Cones(D)`` built by that category's entry;
    this record retains it with the rule factoring every cone through it.
    """

    def __init__(self, diagram, universal_cone, factorizer) -> None:
        if universal_cone.diagram() is not diagram:
            raise ValueError(
                f"the limit cone {universal_cone} lies over {universal_cone.diagram()}, not over the diagram "
                f"{diagram} of the limit"
            )
        self._diagram = diagram
        self._universal_cone = universal_cone
        self._factorizer = factorizer

    def diagram(self):
        return self._diagram

    def cone(self):
        return self._universal_cone

    def object(self):
        return self.cone().apex()

    apex = object

    def structure_morphism(self, index):
        return self.cone().structure_morphism(index)

    def factor(self, cone):
        if cone.diagram() is not self.diagram():
            raise ValueError(
                f"cannot factor the cone {cone} through the limit of {self.diagram()}: it is a cone over "
                f"{cone.diagram()}"
            )
        factor = self._factorizer(cone)
        match factor:
            case ConeMorphism():
                match factor.domain() is cone, factor.codomain() is self.cone():
                    case True, True:
                        return factor
                    case _:
                        raise ValueError(
                            f"the factorization of the cone {cone} through the limit must be a morphism of cones "
                            f"{cone} -> {self.cone()}, but it is {factor}"
                        )
            case _:
                return _ConeCategory(self.diagram()).Mor(cone, self.cone())(factor)

    def induced_map(self, transformation, target_construction):
        r"""Return the map on selected limits induced by ``D -> E``."""
        if transformation.source() is not self.diagram():
            raise ValueError(
                f"the map of limits induced by {transformation} needs it to start at the diagram "
                f"{self.diagram()}, but it starts at {transformation.source()}"
            )
        if transformation.target() is not target_construction.diagram():
            raise ValueError(
                f"the map of limits induced by {transformation} needs it to end at the diagram "
                f"{target_construction.diagram()}, but it ends at {transformation.target()}"
            )
        induced_cone = _ConeCategory(target_construction.diagram()).cone(
            self.object(),
            lambda index: (
                transformation.component(index) * self.structure_morphism(index)
            ),
        )
        return target_construction.factor(induced_cone).apex_map()


class SelectedColimitConstruction(SageObject):
    r"""A selected universal cocone under one represented diagram.

    The cocone is an object of ``Cocones(D)`` built by that category's entry;
    this record retains it with the rule factoring it through every cocone.
    """

    def __init__(self, diagram, universal_cocone, factorizer) -> None:
        if universal_cocone.diagram() is not diagram:
            raise ValueError(
                f"the colimit cocone {universal_cocone} lies under {universal_cocone.diagram()}, not under the "
                f"diagram {diagram} of the colimit"
            )
        self._diagram = diagram
        self._universal_cocone = universal_cocone
        self._factorizer = factorizer

    def diagram(self):
        return self._diagram

    def cocone(self):
        return self._universal_cocone

    def object(self):
        return self.cocone().apex()

    apex = object

    def costructure_morphism(self, index):
        return self.cocone().costructure_morphism(index)

    def factor(self, cocone):
        if cocone.diagram() is not self.diagram():
            raise ValueError(
                f"cannot factor the cocone {cocone} through the colimit of {self.diagram()}: it is a cocone "
                f"under {cocone.diagram()}"
            )
        apex_map = self._factorizer(cocone)
        return _CoconeCategory(self.diagram()).Mor(self.cocone(), cocone)(apex_map)

    def induced_map(self, transformation, target_construction):
        r"""Return the map on selected colimits induced by ``D -> E``."""
        if transformation.source() is not self.diagram():
            raise ValueError(
                f"the map of colimits induced by {transformation} needs it to start at the diagram "
                f"{self.diagram()}, but it starts at {transformation.source()}"
            )
        if transformation.target() is not target_construction.diagram():
            raise ValueError(
                f"the map of colimits induced by {transformation} needs it to end at the diagram "
                f"{target_construction.diagram()}, but it ends at {transformation.target()}"
            )
        induced_cocone = _CoconeCategory(self.diagram()).cocone(
            target_construction.object(),
            lambda index: (
                target_construction.costructure_morphism(index)
                * transformation.component(index)
            ),
        )
        return self.factor(induced_cocone).apex_map()


def _commutes_with_diagram(source, target, apex_map, cocone=False):
    from sage_extensions.logic import AtomicProposition, conjunction

    shape = source.diagram().domain()
    object_set = shape.object_set()
    if cardinal(object_set.cardinality()).is_finite() is not True:
        return AtomicProposition("commutes_with_diagram", source, target, apex_map)

    def equation(index):
        if cocone:
            left = apex_map * source.costructure_morphism(index)
            right = target.costructure_morphism(index)
        else:
            left = target.structure_morphism(index) * apex_map
            right = source.structure_morphism(index)
        return left == right

    return conjunction(equation(index) for index in shape.objects())


def _apex_morphism_equal(left, right):
    """Equality of cone or cocone morphisms in one fixed Mor parent."""
    if left is right:
        return True
    if parent(right) is not left.parent():
        return False
    return left.apex_map() == right.apex_map()


class ConeMorphism(Morphism):
    r"""A morphism of cones, determined by its apex map."""

    def __init__(self, parent: ConeMor, apex_map: Morphism, *, verify: bool = False) -> None:
        Morphism.__init__(self, parent)
        if apex_map.domain() is not self.domain().apex():
            raise ValueError(
                f"a morphism of cones {self.domain()} -> {self.codomain()} is a map of apexes starting at "
                f"{self.domain().apex()}, but {apex_map} starts at {apex_map.domain()}"
            )
        if apex_map.codomain() is not self.codomain().apex():
            raise ValueError(
                f"a morphism of cones {self.domain()} -> {self.codomain()} is a map of apexes ending at "
                f"{self.codomain().apex()}, but {apex_map} ends at {apex_map.codomain()}"
            )
        if not _category_accepts_morphism(
            parent.cone_category().target_category(),
            self.domain().apex(),
            self.codomain().apex(),
            apex_map,
        ):
            raise ValueError(
                f"the map of apexes {apex_map} is not a morphism {self.domain().apex()} -> "
                f"{self.codomain().apex()} of the category the diagram takes values in"
            )
        self._apex_map = apex_map
        if verify:
            self.validate_commutation()

    def apex_map(self) -> Morphism:
        return self._apex_map

    def commutation_decision(self):
        return _commutes_with_diagram(
            self.domain(), self.codomain(), self.apex_map()
        )

    def validate_commutation(self):
        decision = self.commutation_decision()
        if decision is False:
            raise ValueError(
                f"{self.apex_map()} is not a morphism of cones {self.domain()} -> {self.codomain()}: "
                "it does not commute with the legs of the cones"
            )
        return decision

    def __eq__(self, other: Any) -> bool | Predicate:
        return _apex_morphism_equal(self, other)

    def __ne__(self, other: Any) -> bool | Predicate:
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self) -> int:
        return hash(id(self.parent()))

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        # Each leg satisfies r_i g = q_i and q_i f = p_i, hence r_i(gf)=p_i.
        parent = self.parent().cone_category().Mor(other.domain(), self.codomain())
        return parent.element_class(
            parent, self.apex_map() * other.apex_map(), verify=False
        )


class CoconeMorphism(Morphism):
    r"""A morphism of cocones, determined by its apex map."""

    def __init__(self, parent: CoconeMor, apex_map: Morphism, *, verify: bool = False) -> None:
        Morphism.__init__(self, parent)
        if apex_map.domain() is not self.domain().apex():
            raise ValueError(
                f"a morphism of cocones {self.domain()} -> {self.codomain()} is a map of apexes starting at "
                f"{self.domain().apex()}, but {apex_map} starts at {apex_map.domain()}"
            )
        if apex_map.codomain() is not self.codomain().apex():
            raise ValueError(
                f"a morphism of cocones {self.domain()} -> {self.codomain()} is a map of apexes ending at "
                f"{self.codomain().apex()}, but {apex_map} ends at {apex_map.codomain()}"
            )
        if not _category_accepts_morphism(
            parent.cocone_category().target_category(),
            self.domain().apex(),
            self.codomain().apex(),
            apex_map,
        ):
            raise ValueError(
                f"the map of apexes {apex_map} is not a morphism {self.domain().apex()} -> "
                f"{self.codomain().apex()} of the category the diagram takes values in"
            )
        self._apex_map = apex_map
        if verify:
            self.validate_commutation()

    def apex_map(self) -> Morphism:
        return self._apex_map

    def commutation_decision(self):
        return _commutes_with_diagram(
            self.domain(), self.codomain(), self.apex_map(), cocone=True
        )

    def validate_commutation(self):
        decision = self.commutation_decision()
        if decision is False:
            raise ValueError(
                f"{self.apex_map()} is not a morphism of cocones {self.domain()} -> {self.codomain()}: "
                "it does not commute with the legs of the cocones"
            )
        return decision

    def __eq__(self, other: Any) -> bool | Predicate:
        return _apex_morphism_equal(self, other)

    def __ne__(self, other: Any) -> bool | Predicate:
        from sage_extensions.logic import negation

        return negation(self == other)

    def __hash__(self) -> int:
        return hash(id(self.parent()))

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        # Dually, g q_i = r_i and f p_i = q_i imply (gf)p_i = r_i.
        parent = self.parent().cocone_category().Mor(other.domain(), self.codomain())
        return parent.element_class(
            parent, self.apex_map() * other.apex_map(), verify=False
        )


class ConeMor(CategoricalMor):
    Element = ConeMorphism

    def __init__(
        self,
        family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(
            self, family, domain, codomain
        )

    def cone_category(self) -> _ConeCategory:
        return self.base_category()

    def _element_constructor_(self, apex_map):
        match apex_map:
            case ConeMorphism():
                if apex_map.parent() is self:
                    return apex_map
                raise TypeError(f"{apex_map} belongs to another Mor; apply the functor between the categories")
        return self.element_class(self, apex_map)

    def _from_commuting_apex_map(self, apex_map):
        r"""Construct from an apex map whose cone equations are structural."""
        return self.element_class(self, apex_map, verify=False)

    @object_level
    def identity(self) -> ConeMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(C, C), but this is Mor({self.domain()}, {self.codomain()})"
            )
        apex = self.domain().apex()
        return self.element_class(
            self,
            _category_mor_parent(self.cone_category().target_category(), apex, apex).identity(),
            verify=False,
        )


class CoconeMor(CategoricalMor):
    Element = CoconeMorphism

    def __init__(
        self,
        family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(
            self, family, domain, codomain
        )

    def cocone_category(self) -> _CoconeCategory:
        return self.base_category()

    def _element_constructor_(self, apex_map):
        match apex_map:
            case CoconeMorphism():
                if apex_map.parent() is self:
                    return apex_map
                raise TypeError(f"{apex_map} belongs to another Mor; apply the functor between the categories")
        return self.element_class(self, apex_map)

    @object_level
    def identity(self) -> CoconeMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(C, C), but this is Mor({self.domain()}, {self.codomain()})"
            )
        apex = self.domain().apex()
        return self.element_class(
            self,
            _category_mor_parent(self.cocone_category().target_category(), apex, apex).identity(),
            verify=False,
        )


class ConeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ConeMor


class CoconeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = CoconeMor


class _ConeCategory(OwnedCategory):
    r"""The category of cones over one represented diagram.

    Unverified specimens test nonidentity maps of cones and cocones, including
    the identity on an object with nontrivial legs::

        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: labels = finite_ordered_set(("j",))
        sage: index = DiscreteCategory(labels)
        sage: points = finite_ordered_set(("a", "b"))
        sage: one = finite_ordered_set(("*",))
        sage: diagram = Cat().Mor(index, Sets()).constant_functor(one)
        sage: category = diagram.Cones()
        sage: leg = Sets().Mor(points, one)(lambda point: "*")
        sage: cone = category.cone(points, lambda obj: leg)
        sage: Mor = category.Mor(cone, cone)
        sage: Mor is category.MorCategory().Of(cone, cone)
        True
        sage: swap = Sets().Mor(points, points)(lambda point: "b" if point == "a" else "a")
        sage: Mor(swap) * Mor(swap) == Mor.identity()
        True
        sage: cocones = diagram.Cocones()
        sage: leg = Sets().Mor(one, points)(lambda point: "a")
        sage: cocone = cocones.cocone(points, lambda obj: leg)
        sage: Mor = cocones.Mor(cocone, cocone)
        sage: Mor is cocones.MorCategory().Of(cocone, cocone)
        True
        sage: collapse = Mor(Sets().Mor(points, points)(lambda point: "a"))
        sage: Mor.identity() * collapse == collapse
        True
        sage: collapse * collapse == collapse
        True

    Unverified specimen: even an empty cone diagram does not make a
    non-morphism into a permitted apex map::

        sage: injections = Sets().WideSubcategory(Sets().MonomorphismArrowCategory())
        sage: empty_shape = DiscreteCategory(finite_ordered_set(()))
        sage: diagram = Cat().Mor(empty_shape, injections).constant_functor(points)
        sage: category = diagram.Cones()
        sage: cone = category.cone(points, lambda obj: injections.identity(points))
        sage: Mor = category.Mor(cone, cone)
        sage: Mor(swap).apex_map() is swap
        True
        sage: Mor(Sets().Mor(points, points)(lambda point: "a"))
        Traceback (most recent call last):
        ...
        ValueError: the apex map is not a morphism of the diagram's target category
    """

    _MorCategory = ConeMorCategoryConstruction

    class ParentMethods:
        def __init__(
            self,
            apex: Parent,
            transformation: Morphism,
            **rest,
        ) -> None:
            self._apex = apex
            self._transformation = transformation
            super().__init__(**rest)

        def cone_category(self) -> _ConeCategory:
            return self.category()

        def diagram(self) -> Functor:
            return self.cone_category().diagram()

        def apex(self) -> ObjectOfCategory:
            return self._apex

        def transformation(self) -> Morphism:
            return self._transformation

        def structure_morphism(self, index: Parent) -> Morphism:
            return self.transformation().component(index)

        def structure_morphisms(self) -> IndexedFamily:
            domain = self.diagram().domain()
            return indexed_family(
                domain.object_set(),
                lambda label: self.structure_morphism(domain(label)),
                name=f"Structure morphisms of {self}",
            )

        def _repr_(self) -> str:
            return f"Cone with apex {self.apex()} over {self.diagram()}"

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        super().__init__()

    def _make_named_class_key(self, name):
        return self._diagram

    def diagram(self) -> Functor:
        return self._diagram

    def target_category(self) -> Category:
        return self.diagram().codomain()

    def super_categories(self):
        return [OwnedObjects()]

    def cone(
        self,
        apex: Parent,
        components: Callable[[Parent], Morphism],
    ) -> ObjectOfCategory:

        constant = Cat().Mor(
            self.diagram().domain(), self.target_category()
        ).constant_functor(apex)
        transformation = NaturalTransformation(
            constant, self.diagram(), components
        ).morphism()
        return _object_of(self, apex=apex, transformation=transformation)

    def Mor(self, domain: Parent, codomain: Parent) -> ConeMor:
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two cones over its diagram, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)



class _CoconeCategory(OwnedCategory):
    r"""The category of cocones under one represented diagram."""

    _MorCategory = CoconeMorCategoryConstruction

    class ParentMethods:
        def __init__(
            self,
            apex: Parent,
            transformation: Morphism,
            **rest,
        ) -> None:
            self._apex = apex
            self._transformation = transformation
            super().__init__(**rest)

        def cocone_category(self) -> _CoconeCategory:
            return self.category()

        def diagram(self) -> Functor:
            return self.cocone_category().diagram()

        def apex(self) -> ObjectOfCategory:
            return self._apex

        def transformation(self) -> Morphism:
            return self._transformation

        def costructure_morphism(self, index: Parent) -> Morphism:
            return self.transformation().component(index)

        def costructure_morphisms(self) -> IndexedFamily:
            domain = self.diagram().domain()
            return indexed_family(
                domain.object_set(),
                lambda label: self.costructure_morphism(domain(label)),
                name=f"Costructure morphisms of {self}",
            )

        def _repr_(self) -> str:
            return f"Cocone with apex {self.apex()} under {self.diagram()}"

    def __init__(self, diagram: Functor) -> None:
        self._diagram = diagram
        super().__init__()

    def _make_named_class_key(self, name):
        return self._diagram

    def diagram(self) -> Functor:
        return self._diagram

    def target_category(self) -> Category:
        return self.diagram().codomain()

    def super_categories(self):
        return [OwnedObjects()]

    def cocone(
        self,
        apex: Parent,
        components: Callable[[Parent], Morphism],
    ) -> ObjectOfCategory:

        constant = Cat().Mor(
            self.diagram().domain(), self.target_category()
        ).constant_functor(apex)
        transformation = NaturalTransformation(
            self.diagram(), constant, components
        ).morphism()
        return _object_of(self, apex=apex, transformation=transformation)

    def Mor(self, domain: Parent, codomain: Parent) -> CoconeMor:
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two cocones under its diagram, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)



class _SpanCategory(_ConeCategory):
    r"""Spans in one category, over the shape ``. <- . -> .``.

    That shape needs no new vocabulary.  A span :math:`A\leftarrow C\to B` is
    an apex with one arrow to each of two objects, which is exactly a cone
    over the discrete diagram on those two, so the cone category already owns
    it and this is that category read as spans.

    A span is an object here rather than a pair of arguments, so it has an
    apex, two legs, a diagram, and its own colimit.  The colimit is computed
    in the category the span lives in, which is where a pushout belongs and
    which is what lets a category with a construction of its own supply it.
    """

    def super_categories(self):
        return [_ConeCategory(self.diagram())]

    class ParentMethods:
        def target_category(self) -> Category:
            r"""The category the span lives in."""
            return self.cone_category().target_category()

        def left_leg(self) -> Morphism:
            return self.structure_morphism(self.diagram().domain()(0))

        def right_leg(self) -> Morphism:
            return self.structure_morphism(self.diagram().domain()(1))

        def pushout(self) -> ObjectOfCategory:
            r"""Return the pushout of this span, the colimit of its diagram."""
            return self.target_category().pushout(self.left_leg(), self.right_leg())

        def _repr_(self) -> str:
            return f"Span {self.left_leg().codomain()} <- {self.apex()} -> {self.right_leg().codomain()}"


class _ProductConeCategory(_ConeCategory):
    r"""Selected product cones over one represented discrete diagram."""

    def super_categories(self):
        return [_ConeCategory(self.diagram())]


class _CoproductCoconeCategory(_CoconeCategory):
    r"""Selected coproduct cocones under one represented discrete diagram."""

    def super_categories(self):
        return [_CoconeCategory(self.diagram())]


class _LimitsOfCategory(OwnedCategoryBase):
    def __init__(self, index_category: Category, target_category: Category) -> None:
        self._index_category = index_category
        self._target_category = target_category
        super().__init__()

    def _make_named_class_key(self, name):
        return self._index_category, self._target_category

    def index_category(self):
        return self._index_category

    def target_category(self):
        return self._target_category

    def super_categories(self):
        return [OwnedObjects()]

    def _finite_shape_data(self, diagram):
        if diagram.domain() is not self.index_category():
            raise ValueError(
                f"the diagram {diagram} must be indexed by {self.index_category()}, but it is indexed by "
                f"{diagram.domain()}"
            )
        if diagram.codomain() is not self.target_category():
            raise ValueError(
                f"the diagram {diagram} must take values in {self.target_category()}, but it takes values in "
                f"{diagram.codomain()}"
            )
        shape = self.index_category()
        # This is the computational frontier of the finite product/equalizer
        # realization, not a test for mathematical category structure.  Its
        # input is a represented finite shape, whose selected representation
        # supplies these owned families.  Do not probe an arbitrary category
        # for optional methods and silently change algorithms when they are
        # absent.
        object_set = shape.object_set()
        objects = shape.objects()
        assert cardinal(object_set.cardinality()).is_finite(), (
            f"this limit is computed from products and equalizers only over a finite index category, but "
            f"{shape} has infinitely many objects"
        )
        arrows = shape.arrows()
        assert cardinal(arrows.cardinality()).is_finite(), (
            f"this limit is computed from products and equalizers only over a finite index category, but "
            f"{shape} has infinitely many arrows"
        )
        # A diagram's arrow collection is an indexed family, not itself a set.
        # The finite products below index their factors by actual arrows.
        return object_set, objects, finite_ordered_set(tuple(arrows))

    @staticmethod
    def _extremal_shape_object(objects, arrows, *, terminal: bool):
        r"""Return an initial/terminal object with its unique arrows, if represented.

        A diagram indexed by a category with a terminal object has colimit the
        value at that object; dually an initial object computes the limit.
        Detecting this before a product/equalizer or coproduct/coequalizer
        reduction matters when the target subcategory has the required
        extremal colimit but does not have arbitrary coequalizers.
        """
        shape_objects = tuple(objects)
        shape_arrows = tuple(arrows)
        for candidate in shape_objects:
            selected = {}
            for obj in shape_objects:
                source, target = (obj, candidate) if terminal else (candidate, obj)
                matches = tuple(
                    arrow
                    for arrow in shape_arrows
                    if arrow.domain() is source and arrow.codomain() is target
                )
                if len(matches) != 1:
                    break
                selected[obj] = matches[0]
            else:
                return candidate, selected
        return None

    @cached_method(key=lambda self, diagram: id(diagram))
    def construction(self, diagram):
        r"""Return the ordinary categorical limit on a finite represented shape.

        This is a strict 1-categorical limit construction by products and an
        equalizer.  It neither represents nor substitutes for a homotopy limit;
        a homotopical construction requires its own category and coherence.
        """
        object_set, objects, arrows = self._finite_shape_data(diagram)
        extremal = self._extremal_shape_object(objects, arrows, terminal=False)
        if extremal is not None:
            initial, arrows_from_initial = extremal
            apex = diagram(initial)
            universal_cone = (diagram).Cones().cone(
                apex,
                lambda index: diagram(arrows_from_initial[index]),
            )

            def factorizer(cone):
                return cone.structure_morphism(initial)

            return SelectedLimitConstruction(diagram, universal_cone, factorizer)

        target = self.target_category()
        object_factors = indexed_family(
            object_set,
            lambda label: diagram(objects.value(label)),
            name="Object factors of a finite limit",
        )
        product_objects = target.product_construction(object_factors)
        arrow_factors = indexed_family(
            arrows,
            lambda arrow: diagram(arrow.codomain()),
            name="Arrow-target factors of a finite limit",
        )
        product_arrows = target.product_construction(arrow_factors)

        def object_label(obj):
            for label in object_set:
                if objects.value(label) is obj:
                    return label
            raise ValueError(f"{obj} is not an object of the index category {diagram.domain()}")

        p_shape = product_objects.diagram().domain()
        product_arrows.diagram().domain()

        def compatibility_map(use_diagram_arrow):
            cone = (product_arrows.diagram()).Cones().cone(
                product_objects.object(),
                lambda q_index: (
                    diagram(q_index.value())
                    * product_objects.structure_morphism(
                        p_shape(object_label(q_index.value().domain()))
                    )
                    if use_diagram_arrow
                    else product_objects.structure_morphism(
                        p_shape(object_label(q_index.value().codomain()))
                    )
                ),
            )
            return product_arrows.factor(cone).apex_map()

        target_projection = compatibility_map(False)
        arrow_projection = compatibility_map(True)
        equalizer = target.equalizer_construction(target_projection, arrow_projection)
        equalizer_shape = equalizer.diagram().domain()
        into_product = equalizer.structure_morphism(equalizer_shape.source())
        universal_cone = (diagram).Cones().cone(
            equalizer.object(),
            lambda index: (
                product_objects.structure_morphism(p_shape(object_label(index)))
                * into_product
            ),
        )

        def factorizer(cone):
            product_cone = (product_objects.diagram()).Cones().cone(
                cone.apex(),
                lambda index: cone.structure_morphism(objects.value(index.value())),
            )
            into_product_from_apex = product_objects.factor(product_cone).apex_map()
            equalizer_cone = (equalizer.diagram()).Cones().cone(
                cone.apex(),
                lambda index: (
                    into_product_from_apex
                    if index is equalizer_shape.source()
                    else target_projection * into_product_from_apex
                ),
            )
            return equalizer.factor(equalizer_cone).apex_map()

        return SelectedLimitConstruction(diagram, universal_cone, factorizer)

    def object(self, diagram):
        return self.construction(diagram).object()

    @cached_method
    def defining_functor(self):
        r"""Return the functor ``[J,C] -> C`` selected by these limits."""
        from sage_extensions.categories.abstract_categories.functors import (
            _limit_functor,
        )

        return _limit_functor(self.target_category(), self.index_category())


class _ColimitsOfCategory(_LimitsOfCategory):
    @cached_method(key=lambda self, diagram: id(diagram))
    def construction(self, diagram):
        r"""Return the selected colimit, using coproducts and a coequalizer on finite shapes."""
        object_set, objects, arrows = self._finite_shape_data(diagram)
        extremal = self._extremal_shape_object(objects, arrows, terminal=True)
        if extremal is not None:
            terminal, arrows_to_terminal = extremal
            apex = diagram(terminal)
            universal_cocone = (diagram).Cocones().cocone(
                apex,
                lambda index: diagram(arrows_to_terminal[index]),
            )

            def factorizer(cocone):
                return cocone.costructure_morphism(terminal)

            return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

        target = self.target_category()
        object_cofactors = indexed_family(
            object_set,
            lambda label: diagram(objects.value(label)),
            name="Object cofactors of a finite colimit",
        )
        coproduct_objects = target.coproduct_construction(object_cofactors)
        arrow_cofactors = indexed_family(
            arrows,
            lambda arrow: diagram(arrow.domain()),
            name="Arrow-source cofactors of a finite colimit",
        )
        coproduct_arrows = target.coproduct_construction(arrow_cofactors)

        def object_label(obj):
            for label in object_set:
                if objects.value(label) is obj:
                    return label
            raise ValueError(f"{obj} is not an object of the index category {diagram.domain()}")

        coproduct_arrows.diagram().domain()
        b_shape = coproduct_objects.diagram().domain()

        def compatibility_map(use_diagram_arrow):
            cocone = (coproduct_arrows.diagram()).Cocones().cocone(
                coproduct_objects.object(),
                lambda a_index: (
                    coproduct_objects.costructure_morphism(
                        b_shape(object_label(a_index.value().codomain()))
                    )
                    * diagram(a_index.value())
                    if use_diagram_arrow
                    else coproduct_objects.costructure_morphism(
                        b_shape(object_label(a_index.value().domain()))
                    )
                ),
            )
            return coproduct_arrows.factor(cocone).apex_map()

        source_injection = compatibility_map(False)
        arrow_injection = compatibility_map(True)
        coequalizer = target.coequalizer_construction(source_injection, arrow_injection)
        coequalizer_shape = coequalizer.diagram().domain()
        from_coproduct = coequalizer.costructure_morphism(coequalizer_shape.target())
        universal_cocone = (diagram).Cocones().cocone(
            coequalizer.object(),
            lambda index: (
                from_coproduct
                * coproduct_objects.costructure_morphism(
                    b_shape(object_label(index))
                )
            ),
        )

        def factorizer(cocone):
            object_cocone = (coproduct_objects.diagram()).Cocones().cocone(
                cocone.apex(),
                lambda index: cocone.costructure_morphism(objects.value(index.value())),
            )
            from_objects = coproduct_objects.factor(object_cocone).apex_map()
            coequalizer_cocone = (coequalizer.diagram()).Cocones().cocone(
                cocone.apex(),
                lambda index: (
                    from_objects * source_injection
                    if index is coequalizer_shape.source()
                    else from_objects
                ),
            )
            return coequalizer.factor(coequalizer_cocone).apex_map()

        return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

    @cached_method
    def defining_functor(self):
        r"""Return the functor ``[J,C] -> C`` selected by these colimits."""
        from sage_extensions.categories.abstract_categories.functors import (
            _colimit_functor,
        )

        return _colimit_functor(self.target_category(), self.index_category())


class _ProductsOfCategory(_LimitsOfCategory):
    pass


class _CoproductsOfCategory(_ColimitsOfCategory):
    pass


def _discrete_common_object_of_finite_family(category, factors, *, construction: str):
    r"""Return the forced apex of a finite discrete (co)product, when it exists."""
    family = _finite_factor_family(
        factors,
        name=f"{construction.capitalize()} factors",
    )
    if any(factor not in category for factor in family):
        raise TypeError(
            f"a {construction} in {category} needs every factor to be one of its objects, but the factors are {family}"
        )
    labels = tuple(family.index_set())
    if labels:
        apex = family.value(labels[0])
        for label in labels[1:]:
            factor = family.value(label)
            if factor is not apex:
                raise ValueError(
                    f"the {construction} of {family} does not exist in {category}: a discrete category has a morphism "
                    f"between two objects only when they are the same object, but the factors include {apex} and {factor}"
                )
        return family, apex

    object_set = category.object_set()
    if cardinal(object_set.cardinality()) != cardinal(1):
        extremum = "terminal" if construction == "product" else "initial"
        raise ValueError(
            f"the empty {construction} does not exist in {category}: it would be a {extremum} object, and a discrete "
            f"category has a {extremum} object exactly when it has one object"
        )
    return family, category(object_set.an_element())


def _discrete_product_construction(category, factors):
    r"""Return the selected finite product in a represented discrete category."""
    family, product = _discrete_common_object_of_finite_family(
        category,
        factors,
        construction="product",
    )
    diagram = _discrete_diagram(family, category)
    universal_cone = diagram.ProductCones().cone(
        product,
        lambda index: category.Mor(product, diagram(index)).identity(),
    )

    def factorizer(cone):
        return category.Mor(cone.apex(), product).identity()

    return SelectedLimitConstruction(diagram, universal_cone, factorizer)


def _discrete_coproduct_construction(category, factors):
    r"""Return the selected finite coproduct in a represented discrete category."""
    family, coproduct = _discrete_common_object_of_finite_family(
        category,
        factors,
        construction="coproduct",
    )
    diagram = _discrete_diagram(family, category)
    universal_cocone = diagram.CoproductCocones().cocone(
        coproduct,
        lambda index: category.Mor(diagram(index), coproduct).identity(),
    )

    def factorizer(cocone):
        return category.Mor(coproduct, cocone.apex()).identity()

    return SelectedColimitConstruction(diagram, universal_cocone, factorizer)


def _require_parallel_discrete_pair(category, left_morphism, right_morphism) -> None:
    if (
        left_morphism.domain() is not right_morphism.domain()
        or left_morphism.codomain() is not right_morphism.codomain()
    ):
        raise ValueError(
            f"a parallel pair in {category} needs common endpoints, but {left_morphism} is "
            f"{left_morphism.domain()} -> {left_morphism.codomain()} and {right_morphism} is "
            f"{right_morphism.domain()} -> {right_morphism.codomain()}"
        )
    mor = category.Mor(left_morphism.domain(), left_morphism.codomain())
    if parent(left_morphism) is not mor or parent(right_morphism) is not mor:
        raise TypeError(
            f"an equalizer or coequalizer in {category} needs a parallel pair of its morphisms, but got "
            f"{left_morphism} and {right_morphism}"
        )


def _discrete_equalizer_construction(category, left_morphism, right_morphism):
    r"""Return the selected equalizer of a represented discrete parallel pair."""
    _require_parallel_discrete_pair(category, left_morphism, right_morphism)
    equalizer = left_morphism.domain()
    diagram = _parallel_pair_diagram(left_morphism, right_morphism, category)
    universal_cone = diagram.Cones().cone(
        equalizer,
        lambda index: category.Mor(equalizer, diagram(index)).identity(),
    )

    def factorizer(cone):
        return category.Mor(cone.apex(), equalizer).identity()

    return SelectedLimitConstruction(diagram, universal_cone, factorizer)


def _discrete_coequalizer_construction(category, left_morphism, right_morphism):
    r"""Return the selected coequalizer of a represented discrete parallel pair."""
    _require_parallel_discrete_pair(category, left_morphism, right_morphism)
    coequalizer = left_morphism.codomain()
    diagram = _parallel_pair_diagram(left_morphism, right_morphism, category)
    universal_cocone = diagram.Cocones().cocone(
        coequalizer,
        lambda index: category.Mor(diagram(index), coequalizer).identity(),
    )

    def factorizer(cocone):
        return category.Mor(coequalizer, cocone.apex()).identity()

    return SelectedColimitConstruction(diagram, universal_cocone, factorizer)


def _nonempty_discrete_morphism_family_reference(category, morphisms):
    r"""Return one arrow of a nonempty represented parallel family in a discrete category."""
    if morphisms.cardinality() == cardinal(0):
        raise ValueError(
            f"a wide equalizer or coequalizer in {category} needs a nonempty family of parallel morphisms"
        )
    reference = morphisms.value(morphisms.index_set().an_element())
    mor = category.Mor(reference.domain(), reference.codomain())
    if parent(reference) is not mor:
        raise TypeError(
            f"a wide equalizer or coequalizer in {category} needs a family of its morphisms, but the family contains {reference}"
        )
    return reference


def _factor_family(factors, *, name="Selected factors"):
    r"""Return the indexed family a construction is taken over.

    A construction is taken over an index set, so its datum is the family and
    never an arity.  A bare sequence is syntactic ingress: it denotes the
    family on the canonical labels ``Sets.Δ[n-1]``, and this is the one
    boundary at which that normalization happens.
    """
    match factors:
        case IndexedFamily():
            return factors
    values = tuple(factors)
    labels = Sets.Δ[len(values) - 1]
    return indexed_family(
        labels,
        lambda label: values[int(labels.ranking_map()(label))],
        name=name,
    )


def _finite_factor_family(factors, *, name="Selected factors"):
    r"""Return the family, where the construction is represented over finite index sets."""
    family = _factor_family(factors, name=name)
    if not family.cardinality().is_finite():
        raise TypeError(
            f"products and coproducts are computed here only for finitely many factors, but {name} has "
            f"cardinality {family.cardinality()}"
        )
    if family.index_set() not in EnumeratedSets():
        raise TypeError(
            f"{name} has finite cardinality but no selected enumeration of its factor indices"
        )
    return family


def _two_factors_of(factors, *, name="Selected factors"):
    r"""Return the two factors, where the construction is represented binary.

    A backend that takes exactly two objects cannot answer over a larger
    index set.  Folding it would return an object satisfying the same
    universal property, but a different one: its projections and injections
    are composites through a nest, so there is no arrow to or from the factor
    at a given index.  A site with such a backend names that hypothesis here
    rather than folding.
    """
    family = _factor_family(factors, name=name)
    assert family.cardinality() == cardinal(2), (
        f"this construction takes exactly two factors, but {name.lower()} has {family.cardinality()}"
    )
    if family.index_set() not in EnumeratedSets():
        raise TypeError(f"{name} needs an enumeration to select its two factors")
    labels = tuple(family.index_set())
    return family[labels[0]], family[labels[1]]


def _discrete_diagram(factors, target_category=None):
    family = _factor_family(factors)
    if family.cardinality() == cardinal(0):
        if target_category is None:
            raise ValueError(
                "an empty diagram has no object to read its target category from; give the target category"
            )
        target = target_category
    else:
        if target_category is not None:
            target = target_category
        elif family.constant_value() is not None:
            target = family.constant_value().category()
        elif family.selected_diagram() is not None:
            target = family.selected_diagram().codomain()
        else:
            if not family.cardinality().is_finite() or family.index_set() not in EnumeratedSets():
                raise TypeError(
                    "the codomain of a nonconstant diagram without finite enumerated indices "
                    "requires a selected category-valued diagram or an explicit target category"
                )
            target = Cat().join(tuple(obj.category() for obj in family))

    index = DiscreteCategory(family.index_set())
    if not family.cardinality().is_finite() or family.index_set() not in EnumeratedSets():
        selected = family.selected_diagram()
        if selected is not None:
            if selected.domain() is not index or selected.codomain() is not target:
                raise ValueError("the selected factor diagram does not have the requested exact endpoints")
            return selected
        constant = family.constant_value()
        if constant is not None:
            if constant not in target:
                raise ValueError("the selected constant factor is outside the diagram's target category")
            return Cat().Mor(index, target).constant_functor(constant)
        raise TypeError(
            "an unenumerated nonconstant factor family does not supply a verified discrete diagram"
        )
    return Cat().Mor(index, target).discrete_diagram(family)


__all__ = [
    "CoconeMorphism",
    "ConeMorphism",
    "DirectedSystem",
    "FiniteOrdinalCategory",
    "FiniteSequenceDiagram",
    "InverseSystem",
    "ParallelFamilyCategory",
    "ParallelFamilyDiagram",
    "ParallelPairCategory",
    "ParallelPairDiagram",
    "PosetCategory",
    "RestrictedDiagram",
    "SelectedColimitConstruction",
    "SelectedLimitConstruction",
]
