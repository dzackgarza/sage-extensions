r"""Induction, restriction and coinduction along a subgroup ``H <= G``.

These are scalar extension, restriction and coextension along the ring
morphism ``R[H] -> R[G]`` that the group-algebra functor assigns to the
inclusion.  Since ``R[G]`` is free as a right ``R[H]``-module on a transversal
``T`` of the left cosets ``G/H``, ``R[G] tensor_{R[H]} M`` is the direct sum of
one copy of ``M`` per coset, ``g`` acting through ``g t = t' h``; dually
``Hom_{R[H]}(R[G], M)`` is a function on a right transversal (Serre, *Linear
Representations of Finite Groups*, §3.3 and §7.1).  The functors here are the
scalar-change functors of ``scalar_change`` specialized to that hypothesis,
with the transversal as the represented datum.
"""

from sage_extensions.categories.algebras.group_algebras import GroupAlgebras
from sage_extensions.categories.functors.scalar_change import (
    _BaseChangeAdjunction,
    _CoextensionOfScalarsFunctor,
    _RestrictionCoextensionAdjunction,
    _RestrictionOfScalarsFunctor,
    _ScalarExtensionFunctor,
)
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
    _relation_morphism,
)
from sage_extensions.categories.rings.ring_foundation import _owned_ring
from sage_extensions.categories.sets.finite_ordered_sets import FiniteOrderedSets
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import Sets


def _is_group_algebra_map_of_subgroup_inclusion(ring_map) -> bool:
    r"""Decide whether ``ring_map`` is ``R[H] -> R[G]`` for a subgroup ``H <= G``.

    Both endpoints must be group algebras over one ring, ``H`` must have been
    constructed inside ``G``, and the map must agree with the inclusion on the
    chosen generators of ``H``; two algebra morphisms out of ``R[H]`` agreeing
    there agree everywhere.
    """
    source = _owned_ring(ring_map.domain())
    target = _owned_ring(ring_map.codomain())
    ring = source.base_ring()
    if source not in GroupAlgebras(ring) or target not in GroupAlgebras(ring):
        return False
    subgroup, supergroup = source.group(), target.group()
    if subgroup.supergroup() is not supergroup:
        return False
    inclusion = subgroup.inclusion()
    return all(
        ring_map(source.module_generator(generator))
        == target.module_generator(inclusion(generator))
        for generator in subgroup.group_generators()
    )


def _subgroup_data(ring_map):
    assert ring_map.is_group_algebra_subgroup_inclusion(), (
        f"{ring_map} is not the group-algebra map of a subgroup inclusion"
    )
    subgroup = _owned_ring(ring_map.domain()).group()
    supergroup = _owned_ring(ring_map.codomain()).group()
    assert supergroup.is_finite() is True, (
        f"induction and coinduction along {ring_map} are computed from coset representatives, which "
        f"needs the group {supergroup} to be finite, but it is not known to be finite"
    )
    return subgroup, supergroup, subgroup.inclusion()


def _transport_element(element, source, target):
    r"""Transport one framed vector across equal selected module labels."""
    coordinates = source.framing_morphism().lift(element)
    return target.linear_combination(
        {label: coordinates(label) for label in coordinates.support().domain()}
    )


def _equivariant_mor(domain, codomain, images):
    r"""Construct a group-module map whose equivariance is structural."""
    return domain.Mor(codomain)._from_equivariant_images(images)


def _coset_sum_labels(representatives, source_labels):
    return Sets().product(
        indexed_family(
            Sets.Δ[1],
            lambda index: representatives if int(index) == 0 else source_labels,
        )
    )


def _coset_label(labels, representative, source_label):
    return labels(
        lambda index: representative if int(index) == 0 else source_label
    )


def _finite_coset_sum(module, representatives):
    r"""Return the finite direct sum of copies of ``module`` indexed by cosets.

    The framing is the actual product of the representative set with the source
    framing.  The relation morphism is the coset-indexed sum of copies of the
    relation morphism ``r`` of ``module``: the relation ``(g, k)`` is
    ``r(e_k)`` placed in the copy indexed by ``g``.
    """
    module = module.unformed_module()
    source_labels = module.module_generating_set()
    labels = _coset_sum_labels(representatives, source_labels)
    source_relations = _relation_morphism(module)
    source_relation_labels = source_relations.domain().module_generating_set()
    if source_relation_labels.cardinality() == 0:
        return module.base_ring().free_module(labels)

    ring = module.base_ring()
    generators = ring._fresh_free_module_on(labels)
    relation_source = ring._fresh_free_module_on(
        _coset_sum_labels(representatives, source_relation_labels)
    )

    def relation(relation_label):
        image = source_relations(
            source_relations.domain().module_generator(relation_label.component(1))
        ).to_vector()
        return generators.linear_combination(
            {
                _coset_label(labels, relation_label.component(0), source_label): image(source_label)
                for source_label in image.support().domain()
            }
        )

    presentation = relation_source.module_category().Mor(relation_source, generators)(relation)
    return presentation.cokernel()


class _RestrictionOfActingGroupFunctor(_RestrictionOfScalarsFunctor):
    r"""``Res_H^G : Modules(R[G]) -> Modules(R[H])``, restriction along ``R[H] -> R[G]``."""

    def __init__(self, ring_map) -> None:
        super().__init__(ring_map)
        self._subgroup, self._supergroup, self._inclusion = _subgroup_data(ring_map)

    def subgroup(self):
        return self._subgroup

    def supergroup(self):
        return self._supergroup

    def inclusion(self):
        return self._inclusion

    def _apply_object(self, group_module):
        coefficient_module = group_module.unformed_module()
        return self.codomain()(
            coefficient_module,
            lambda subgroup_element, vector: group_module.action_of(
                self.inclusion()(subgroup_element)
            )(
                vector
            ),
        )

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return _equivariant_mor(source, target,
            {
                label: _transport_element(
                    morphism(morphism.domain().module_generator(label)),
                    morphism.codomain(),
                    target,
                )
                for label in morphism.domain().module_generating_set()
            }
        )

    def _repr_(self):
        return f"Restriction from {self.supergroup()} to {self.subgroup()}"


class _InductionFunctor(_ScalarExtensionFunctor):
    r"""``Ind_H^G : Modules(R[H]) -> Modules(R[G])``, scalar extension along ``R[H] -> R[G]``."""

    def __init__(self, ring_map) -> None:
        super().__init__(ring_map)
        self._subgroup, self._supergroup, self._inclusion = _subgroup_data(ring_map)
        self._left_cosets = self._supergroup.left_cosets(self._subgroup)
        self._representatives = FiniteOrderedSets().from_indexed(
            self._left_cosets,
            lambda coset: coset[0],
            name="Left-coset representatives",
        )

    def subgroup(self):
        return self._subgroup

    def supergroup(self):
        return self._supergroup

    def inclusion(self):
        return self._inclusion

    def representatives(self):
        return self._representatives

    def identity_representative(self):
        identity = self.supergroup().one()
        for representative in self.representatives():
            if identity in next(
                coset for coset in self._left_cosets if coset[0] == representative
            ):
                return representative
        raise AssertionError(
            "no left coset of the subgroup contains the identity, so the cosets were computed wrongly"
        )

    def _decompose_left(self, group_element):
        for coset in self._left_cosets:
            if group_element in coset:
                representative = coset[0]
                subgroup_element = self.subgroup()(
                    representative**-1 * group_element
                )
                return representative, subgroup_element
        raise AssertionError(
            f"{group_element} lies in no left coset of the subgroup, so the cosets do not partition the group"
        )

    def _apply_object(self, group_module):
        module = _finite_coset_sum(group_module, self.representatives())
        zero = group_module.coefficient_ring().zero()

        def action(group_element, vector):
            output_coefficients = {}
            coordinates = module.framing_morphism().lift(vector)
            for pair in coordinates.support().domain():
                coefficient = coordinates(pair)
                representative = pair.component(0)
                label = pair.component(1)
                target_representative, subgroup_element = self._decompose_left(
                    group_element * representative
                )
                acted = group_module.act(
                    subgroup_element, group_module.module_generator(label)
                )
                acted_coordinates = group_module.framing_morphism().lift(acted)
                for target_label in acted_coordinates.support().domain():
                    acted_coefficient = acted_coordinates(target_label)
                    target_label_pair = _coset_label(
                        module.module_generating_set(),
                        target_representative,
                        target_label,
                    )
                    output_coefficients[target_label_pair] = (
                        output_coefficients.get(target_label_pair, zero)
                        + coefficient * acted_coefficient
                    )
            return module.linear_combination(output_coefficients)

        return self.codomain()(module, action)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        images = {}
        for representative in self.representatives():
            for label in morphism.domain().module_generating_set():
                image = morphism(morphism.domain().module_generator(label))
                coordinates = morphism.codomain().framing_morphism().lift(image)
                images[_coset_label(
                    source.module_generating_set(), representative, label
                )] = target.linear_combination(
                    {
                        _coset_label(
                            target.module_generating_set(),
                            representative,
                            target_label,
                        ): coordinates(target_label)
                        for target_label in coordinates.support().domain()
                    }
                )
        return _equivariant_mor(source, target, images)

    def _repr_(self):
        return f"Induction from {self.subgroup()} to {self.supergroup()}"


class _CoinductionFunctor(_CoextensionOfScalarsFunctor):
    r"""``Coind_H^G : Modules(R[H]) -> Modules(R[G])``, coextension along ``R[H] -> R[G]``."""

    def __init__(self, ring_map) -> None:
        super().__init__(ring_map)
        self._subgroup, self._supergroup, self._inclusion = _subgroup_data(ring_map)
        self._right_cosets = self._supergroup.right_cosets(self._subgroup)
        right_section = self._right_cosets.right_coset_section()
        self._representatives = FiniteOrderedSets().from_indexed(
            self._right_cosets,
            lambda point: right_section(point),
            name="Right-coset representatives",
        )

    def subgroup(self):
        return self._subgroup

    def supergroup(self):
        return self._supergroup

    def inclusion(self):
        return self._inclusion

    def representatives(self):
        return self._representatives

    def identity_representative(self):
        r"""The representative of the right coset ``H``, the image of the base point."""
        return self._right_cosets.right_coset_section()(self._right_cosets.base_point())

    def _decompose_right(self, group_element):
        r"""``g = h r`` with ``r`` the representative of ``Hg``: ``h = g t_p`` for ``p = g^-1 H``."""
        point = self._right_cosets.right_coset_projection()(group_element)
        representative = self._right_cosets.right_coset_section()(point)
        return self.subgroup()(group_element * ~representative), representative

    def _apply_object(self, group_module):
        module = _finite_coset_sum(group_module, self.representatives())

        def value_at(vector, representative):
            coordinates = module.framing_morphism().lift(vector)
            module_labels = module.module_generating_set()
            return group_module.linear_combination(
                {
                    label: coordinates(_coset_label(module_labels, representative, label))
                    for label in group_module.module_generating_set()
                }
            )

        def action(group_element, vector):
            output_coefficients = {}
            for representative in self.representatives():
                subgroup_element, source_representative = self._decompose_right(
                    representative * group_element
                )
                acted = group_module.act(
                    subgroup_element, value_at(vector, source_representative)
                )
                acted_coordinates = group_module.framing_morphism().lift(acted)
                for label in acted_coordinates.support().domain():
                    output_coefficients[
                        _coset_label(
                            module.module_generating_set(),
                            representative,
                            label,
                        )
                    ] = acted_coordinates(label)
            return module.linear_combination(output_coefficients)

        return self.codomain()(module, action)

    def value_at(self, source, coinduced, vector, representative):
        coordinates = coinduced.framing_morphism().lift(vector)
        labels = coinduced.module_generating_set()
        return source.linear_combination(
            {
                label: coordinates(_coset_label(labels, representative, label))
                for label in source.module_generating_set()
            }
        )

    def element_from_values(self, source, coinduced, value_function):
        coefficients = {}
        for representative in self.representatives():
            value = value_function(representative)
            coordinates = source.framing_morphism().lift(value)
            for label in coordinates.support().domain():
                coefficients[
                    _coset_label(
                        coinduced.module_generating_set(),
                        representative,
                        label,
                    )
                ] = coordinates(label)
        return coinduced.linear_combination(coefficients)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        images = {}
        for representative in self.representatives():
            for label in morphism.domain().module_generating_set():
                coordinates = morphism.codomain().framing_morphism().lift(
                    morphism(morphism.domain().module_generator(label))
                )
                images[_coset_label(
                    source.module_generating_set(), representative, label
                )] = target.linear_combination(
                    {
                        _coset_label(
                            target.module_generating_set(),
                            representative,
                            target_label,
                        ): coordinates(target_label)
                        for target_label in coordinates.support().domain()
                    }
                )
        return _equivariant_mor(source, target, images)

    def _repr_(self):
        return f"Coinduction from {self.subgroup()} to {self.supergroup()}"


class _InductionRestrictionAdjunction(_BaseChangeAdjunction):
    r"""``Ind_H^G ⊣ Res_H^G``, the base-change adjunction along ``R[H] -> R[G]``."""

    _extension_functor = _InductionFunctor
    _restriction_functor = _RestrictionOfActingGroupFunctor

    def _unit_component(self, group_module):
        induced = self.left_adjoint()(group_module)
        restricted = self.right_adjoint()(induced)
        representative = self.left_adjoint().identity_representative()
        return _equivariant_mor(group_module, restricted,
            {
                label: _transport_element(
                    induced.module_generator(_coset_label(induced.module_generating_set(), representative, label)),
                    induced,
                    restricted,
                )
                for label in group_module.module_generating_set()
            }
        )

    def _counit_component(self, group_module):
        restricted = self.right_adjoint()(group_module)
        induced = self.left_adjoint()(restricted)
        return _equivariant_mor(induced, group_module,
            {
                _coset_label(induced.module_generating_set(), representative, label): group_module.act(
                    representative, group_module.module_generator(label)
                )
                for representative in self.left_adjoint().representatives()
                for label in group_module.module_generating_set()
            }
        )


class _RestrictionCoinductionAdjunction(_RestrictionCoextensionAdjunction):
    r"""``Res_H^G ⊣ Coind_H^G``, the restriction/coextension adjunction along ``R[H] -> R[G]``."""

    _restriction_functor = _RestrictionOfActingGroupFunctor
    _coextension_functor = _CoinductionFunctor

    def _unit_component(self, group_module):
        restricted = self.left_adjoint()(group_module)
        coinduced = self.right_adjoint()(restricted)
        return _equivariant_mor(group_module, coinduced,
            {
                label: self.right_adjoint().element_from_values(
                    restricted,
                    coinduced,
                    lambda representative, label=label: _transport_element(
                        group_module.act(
                            representative,
                            group_module.module_generator(label),
                        ),
                        group_module,
                        restricted,
                    ),
                )
                for label in group_module.module_generating_set()
            }
        )

    def _counit_component(self, group_module):
        coinduced = self.right_adjoint()(group_module)
        restricted = self.left_adjoint()(coinduced)
        representative = self.right_adjoint().identity_representative()
        return _equivariant_mor(restricted, group_module,
            {
                label: self.right_adjoint().value_at(
                    group_module,
                    coinduced,
                    coinduced.module_generator(label),
                    representative,
                )
                for label in restricted.module_generating_set()
            }
        )


__all__ = [
]
