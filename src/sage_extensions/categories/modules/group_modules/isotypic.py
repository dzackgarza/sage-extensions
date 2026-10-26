r"""Isotypic components of finite characteristic-zero group modules."""

from __future__ import annotations

from dataclasses import dataclass

from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ

from sage_extensions.categories.abstract_categories.direct_sum_objects import DirectSumObjects
from sage_extensions.categories.modules.framed.framed_free_modules import (
    _module_subobject_spanning_with_structure,
    _span_basis_elements,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_rationals,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family


@dataclass(frozen=True)
class IsotypicCharacter:
    r"""A coefficient-field irreducible character or a rational Galois orbit."""

    characters: tuple

    def degree(self):
        return sum(character.degree() for character in self.characters)

    def is_trivial(self) -> bool:
        return all(
            all(value == 1 for value in character.values())
            for character in self.characters
        )

    def __call__(self, group_element):
        return sum(character(group_element) for character in self.characters)

    def _repr_(self):
        if len(self.characters) == 1:
            return repr(self.characters[0])
        return "Rational character orbit of " + ", ".join(
            repr(character) for character in self.characters
        )

    __repr__ = _repr_


class IsotypicDecompositions(OwnedCategoryOverBaseRing):
    r"""Submodules of an ``R``-module equipped with their selected isotypic summands."""

    def super_categories(self):
        return [DirectSumObjects(Modules(self.base_ring()))]

    class ParentMethods:
        _derived_construction_parameters = frozenset({"summands"})

        def __init__(self, isotypic_characters, isotypic_components, **rest) -> None:
            characters = tuple(isotypic_characters)
            components = tuple(isotypic_components)
            if len(characters) != len(components):
                raise ValueError(
                    f"an isotypic decomposition needs one component per character, but {len(characters)} "
                    f"characters {characters} were given with {len(components)} components"
                )
            self._preamble_isotypic_characters = characters
            self._preamble_isotypic_components = components
            index_set = finite_ordered_set(characters)
            super().__init__(
                summands=indexed_family(
                    index_set,
                    lambda character: components[int(index_set.ranking_map()(character))],
                    name="Isotypic summands",
                ),
                **rest,
            )

        def isotypic_characters(self):
            return finite_ordered_set(self._preamble_isotypic_characters)

        def isotypic_component(self, character):
            labels = self.isotypic_characters()
            for position, candidate in enumerate(labels):
                if candidate == character or character in candidate.characters:
                    return self._preamble_isotypic_components[position]
            raise ValueError(
                f"{character!r} is not a character of the isotypic decomposition {self}; its characters are {labels}"
            )

        def trivial_component(self):
            for character in self.isotypic_characters():
                if character.is_trivial():
                    return self.isotypic_component(character)
            raise ValueError(
                f"the isotypic decomposition {self} has no trivial component: none of its characters "
                f"{self.isotypic_characters()} is the trivial character"
            )

        def nontrivial_components(self):
            return finite_ordered_set(
                tuple(
                    component
                    for character, component in zip(
                        self._preamble_isotypic_characters,
                        self._preamble_isotypic_components,
                        strict=True,
                    )
                    if not character.is_trivial()
                )
            )


def _character_rows(group):
    characters = tuple(group.irreducible_characters())
    rows = tuple(tuple(character.values()) for character in characters)
    return characters, rows


def _galois_orbits_of_irreducible_characters(group):
    r"""Return rational central-character orbits of the complex irreducibles."""
    characters, rows = _character_rows(group)
    if not characters:
        return tuple()
    field = group.character_table().base_ring()
    automorphisms = tuple(field.galois_group())
    if not automorphisms:
        return tuple(IsotypicCharacter((character,)) for character in characters)

    unused = set(range(len(characters)))
    result = []
    while unused:
        seed = min(unused)
        orbit_rows = set()
        for automorphism in automorphisms:
            orbit_rows.add(
                tuple(automorphism(field(value)) for value in rows[seed])
            )
        orbit = tuple(
            index for index, row in enumerate(rows) if tuple(row) in orbit_rows
        )
        for index in orbit:
            unused.discard(index)
        result.append(IsotypicCharacter(tuple(characters[index] for index in orbit)))
    return tuple(result)


def _split_irreducible_characters(module):
    r"""Return the correct public character index for the coefficient ring."""
    ring = _engine_ring(module.coefficient_ring())
    group = module.group()
    if ring in (SageZZ, SageQQ):
        return _galois_orbits_of_irreducible_characters(group)
    assert ring.is_field() and ring.characteristic() == 0, (
        f"cannot decompose {module} into isotypic components: the projectors by ordinary characters of "
        f"{group} need a field of characteristic 0, but the coefficient ring is {module.coefficient_ring()}"
    )
    characters = tuple(group.irreducible_characters())
    for character in characters:
        for value in character.values():
            if value not in ring:
                raise AssertionError(
                    f"cannot decompose {module} into isotypic components: {module.coefficient_ring()} is not a "
                    f"splitting field for {group}, since the value {value} of the irreducible character "
                    f"{character} does not lie in it"
                )
    return tuple(IsotypicCharacter((character,)) for character in characters)


def _central_projector(module, character: IsotypicCharacter):
    r"""Return the central idempotent as an owned matrix endomorphism."""
    group = module.group()
    coefficient_module = module.unformed_module()
    base_ring = module.coefficient_ring()
    engine_ring = _engine_ring(base_ring)

    computation_ring = _owned_rationals() if engine_ring is SageZZ else base_ring
    rank = int(coefficient_module.module_rank())
    labels = tuple(coefficient_module.module_generating_set())
    matrices = computation_ring.matrix_space(rank)
    projector = matrices.zero()
    order = computation_ring(int(group.order()))
    computation_engine = _engine_ring(computation_ring)

    for group_element in group:
        backend_coefficient = sum(
            irreducible.degree() * irreducible(group_element**-1)
            for irreducible in character.characters
        )
        # A Galois-orbit sum of character values is rational, so it lands in
        # the computation ring through the value field's engine.
        coefficient = _owned_engine_element(computation_ring,
            computation_engine(
                _engine_element(backend_coefficient.parent(), backend_coefficient)
            )
        ) / order
        source = module.action_of(group_element)
        transported = matrices.from_rows(
            [
                [
                    _owned_engine_element(computation_ring,
                        computation_engine(
                            _engine_element(base_ring, source[labels[row], labels[column]])
                        )
                    )
                    for column in range(rank)
                ]
                for row in range(rank)
            ]
        )
        projector += coefficient * transported
    return projector


def _kernel_subobject_of_matrix(module, matrix):
    coefficient_module = module.unformed_module()
    labels = tuple(coefficient_module.module_generating_set())
    images = {
        source_label: coefficient_module.linear_combination(
            {
                target_label: matrix[target_index, source_index]
                for target_index, target_label in enumerate(labels)
                if matrix[target_index, source_index]
            }
        )
        for source_index, source_label in enumerate(labels)
    }
    return coefficient_module.module_category().Mor(coefficient_module, coefficient_module)(images).kernel()


def _isotypic_component(module, character):
    r"""Return ``M ∩ V_character`` as a subobject of ``M``."""
    characters = _split_irreducible_characters(module)
    selected = next(
        (
            candidate
            for candidate in characters
            if candidate == character or character in candidate.characters
        ),
        None,
    )
    if selected is None:
        raise ValueError(
            f"{character!r} is not an irreducible character of {module.group()} over "
            f"{module.coefficient_ring()}, so {module} has no isotypic component for it"
        )
    projector = _central_projector(module, selected)
    coefficient_module = module.unformed_module()
    base_ring = module.coefficient_ring()
    relation = projector - projector.parent().identity()
    if _engine_ring(base_ring) is SageZZ:
        integers = base_ring
        denominator = integers.one()
        for row_label in relation.parent().row_index_set():
            for column_label in relation.parent().column_index_set():
                denominator = denominator.lcm(
                    relation[row_label, column_label].denominator()
                )
        cleared = denominator * relation

        relation = integers.matrix_space(int(coefficient_module.module_rank())).from_rows(
            [
                [
                    cleared[row, column].numerator()
                    for column in range(int(coefficient_module.module_rank()))
                ]
                for row in range(int(coefficient_module.module_rank()))
            ]
        )
    return _kernel_subobject_of_matrix(module, relation)


def _isotypic_decomposition(module):
    r"""Return ``⊕ M_chi -> M`` over the characters present in ``M``."""
    coefficient_module = module.unformed_module()
    characters = tuple(module.isotypic_characters())
    components = tuple(module.isotypic_component(character) for character in characters)
    spanning = tuple(
        component.inclusion()(generator)
        for component in components
        for generator in component.module_generators()
    )
    basis = _span_basis_elements(coefficient_module, spanning)
    return _module_subobject_spanning_with_structure(
        coefficient_module,
        basis,
        extra_categories=(IsotypicDecompositions(coefficient_module.base_ring()),),
        extra_construction_data={
            "isotypic_characters": characters,
            "isotypic_components": components,
        },
    )


__all__ = [
    "IsotypicCharacter",
    "IsotypicDecompositions",
]
