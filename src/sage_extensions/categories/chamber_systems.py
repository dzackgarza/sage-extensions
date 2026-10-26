r"""Owned finite chamber systems.

A chamber system over a type set ``I`` is a set of chambers equipped, for each
``i in I``, with an equivalence relation of ``i``-adjacency.  Morphisms here
preserve the type set and every typed adjacency relation.  This is the standard
notion used for buildings; see Abramenko--Brown, *Buildings*, Section 1.4.
"""

from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.logic import negation
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class _FiniteChamberSystemEngine:
    r"""Private realization of a finite chamber system by typed adjacencies."""

    def __init__(self, chambers, type_set, adjacent_pairs, **rest) -> None:
        self._chambers = finite_ordered_set(chambers)
        self._chamber_pair_space = self._chambers**2
        self._type_set = finite_ordered_set(type_set)
        self._adjacent_pairs = {
            type_: finite_ordered_set(pairs)
            for type_, pairs in adjacent_pairs.items()
        }
        super().__init__(facade=True, **rest)

    def chambers(self):
        return self._chambers

    def type_set(self):
        return self._type_set

    def __contains__(self, chamber) -> bool:
        return chamber in self.chambers()

    is_parent_of = __contains__

    def _element_constructor_(self, chamber):
        return self.chambers()(chamber)

    def __iter__(self):
        return iter(self.chambers())

    def cardinality(self):
        return self.chambers().cardinality()

    def is_adjacent(self, left, type_, right) -> bool:
        type_ = self.type_set()(type_)
        return self._chamber_pair_space((left, right)) in self._adjacent_pairs[type_]


class ChamberSystemMorphism:
    r"""A type-preserving map of chambers preserving every adjacency."""

    def __init__(self, parent, set_morphism) -> None:
        self._set_morphism = set_morphism
        super().__init__(parent, set_morphism)

    def underlying_set_morphism(self):
        return self._set_morphism

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return self.parent()._from_chamber_map(
            self.underlying_set_morphism() * other.underlying_set_morphism()
        )

    def __eq__(self, other):
        if element_parent(other) is not self.parent():
            return False
        return other.underlying_set_morphism() == self.underlying_set_morphism()

    def __ne__(self, other):
        return negation(self == other)

    __hash__ = None


class ChamberSystemMor(CategoricalMor):
    ElementMethods = ChamberSystemMorphism

    def _verify(self, morphism) -> None:
        if self.domain().type_set() != self.codomain().type_set():
            raise ValueError(
                f"there are no morphisms of chamber systems from {self.domain()} to "
                f"{self.codomain()}: a morphism preserves types, but the type sets "
                f"{self.domain().type_set()} and {self.codomain().type_set()} differ"
            )
        for type_ in self.domain().type_set():
            for left in self.domain().chambers():
                for right in self.domain().chambers():
                    if self.domain().is_adjacent(left, type_, right) and not self.codomain().is_adjacent(
                        morphism(left), type_, morphism(right)
                    ):
                        raise ValueError(
                            f"{morphism} is not a morphism of chamber systems: the chambers "
                            f"{left} and {right} are {type_}-adjacent in {self.domain()}, but "
                            f"their images {morphism(left)} and {morphism(right)} are not "
                            f"{type_}-adjacent in {self.codomain()}"
                        )

    def _element_constructor_(self, datum):
        if element_parent(datum) is self:
            return datum
        set_morphism = Sets().Mor(self.domain(), self.codomain())(datum)
        morphism = self.element_class(self, set_morphism)
        self._verify(morphism)
        return morphism

    def _from_chamber_map(self, set_morphism):
        return self.element_class(self, set_morphism)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism from {self.domain()} to {self.codomain()}: "
                f"an identity needs its domain and codomain to be the same chamber system"
            )
        return self._from_chamber_map(
            Sets().Mor(self.domain(), self.domain()).identity()
        )


class ChamberSystemMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ChamberSystemMor


class ChamberSystems(OwnedCategory):
    r"""Chamber systems with type-preserving adjacency-preserving morphisms."""

    _MorCategory = ChamberSystemMorCategoryConstruction

    def super_categories(self):
        return [Sets()]

    @classmethod
    def _repr_object_names(cls):
        return "chamber systems"

    def an_object(self):
        return self.from_adjacencies(
            (0, 1),
            ("s",),
            {"s": ((0, 0), (0, 1), (1, 0), (1, 1))},
        )

    def from_adjacencies(self, chambers, type_set, adjacent_pairs):
        chambers = finite_ordered_set(chambers)
        chamber_pair_space = chambers**2
        type_set = finite_ordered_set(type_set)
        normalized = {
            type_: finite_ordered_set(
                tuple(chamber_pair_space(pair) for pair in adjacent_pairs[type_])
            )
            for type_ in type_set
        }
        for type_ in type_set:
            relation = normalized[type_]
            if any(
                pair[0] not in chambers or pair[1] not in chambers
                for pair in relation
            ):
                raise ValueError(
                    f"the {type_}-adjacency relation {relation} is not a relation on the "
                    f"chambers {chambers}: some pair contains an element that is not a chamber"
                )
            if any(
                chamber_pair_space((chamber, chamber)) not in relation
                for chamber in chambers
            ):
                raise ValueError(
                    f"the {type_}-adjacency relation {relation} on {chambers} is not "
                    f"reflexive: adjacency of each type must be an equivalence relation"
                )
            if any(
                chamber_pair_space((right, left)) not in relation
                for left, right in relation
            ):
                raise ValueError(
                    f"the {type_}-adjacency relation {relation} on {chambers} is not "
                    f"symmetric: adjacency of each type must be an equivalence relation"
                )
            if any(
                chamber_pair_space((left, right)) in relation
                and chamber_pair_space((right, third)) in relation
                and chamber_pair_space((left, third)) not in relation
                for left in chambers
                for right in chambers
                for third in chambers
            ):
                raise ValueError(
                    f"the {type_}-adjacency relation {relation} on {chambers} is not "
                    f"transitive: adjacency of each type must be an equivalence relation"
                )
        return _object_of(
            self,
            _engine=(self, _FiniteChamberSystemEngine, None),
            chambers=chambers,
            type_set=type_set,
            adjacent_pairs=normalized,
        )


__all__ = ["ChamberSystems"]
