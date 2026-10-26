r"""Quotients of glued schemes by a finite group acting on a stable finite affine atlas.

Let ``G`` be a finite group and ``X`` a scheme over ``R`` glued from affine
charts ``U_i`` along isomorphisms ``phi_ij : U_ij -> U_ji``.  A left action of
``G`` on ``X`` that preserves every chart is the same datum as a left action
on each ``U_i`` (an object of ``AffineGSchemes(G, R)``) for which every
``phi_ij`` is ``G``-equivariant.  The quotient ``X/G`` then exists and is
glued from the affine quotients ``U_i/G = Spec(O(U_i)^G)`` along the
descended overlap isomorphisms ``U_ij/G -> U_ji/G`` (SGA 1, Exp. V, Prop. 1.8
and Cor. 1.4, applied to a ``G``-stable affine cover).  Those descended
transitions are determined by the action; they are supplied as data because
expressing an invariant rational function in the invariant algebra of the
other chart is computed automatically only in the ``C_2`` case below.

:class:`FiniteGluedInvariantQuotient` is the construction.  Every object it
produces is an object of ``Schemes(R)`` built by that category's gluing entry:
the source ``X`` and the quotient ``X/G``.  Every arrow is built by the Mor of
its glued domain from local maps: the action ``g: X -> X``, the quotient
morphism ``X -> X/G`` and the factorization of an invariant morphism.  For an
affine target an invariant morphism out of ``X`` factors uniquely through
``X/G``: existence is chartwise, by the affine quotient's universal property,
and uniqueness follows chartwise from that same property and globally from
maps out of a gluing.
"""

from itertools import combinations

from sage.misc.cachefunc import cached_method
from sage.structure.sage_object import SageObject

from sage_extensions.categories.group.groups import (
    FiniteGroups,
)
from sage_extensions.categories.schemes.schemes import (
    AffineGSchemes,
    Schemes,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.lexicon.set_theory import SetObject


def _reversed_isomorphism(transition):
    r"""``phi^{-1}`` read as an arrow of ``Core(Sch/R)`` from the codomain of ``phi``."""
    schemes = Schemes(transition.codomain().scheme_base_ring())
    return schemes.Core().Mor(transition.codomain(), transition.domain())(
        transition.inverse().forward(),
        transition.forward(),
    )


class FiniteGluedInvariantQuotient(SageObject):
    r"""The quotient of a finite equivariant affine gluing by a finite group.

    The input is a finite indexed family of affine ``G``-schemes on the charts,
    the source-overlap isomorphisms, and their descended quotient-overlap
    isomorphisms, indexed by the chart pairs.  The construction verifies that
    every source transition is ``G``-equivariant and that every descended
    transition closes its quotient descent square, then glues the source and
    quotient atlases in ``Schemes(R)``.  A glued source already constructed on
    the same charts and transitions is used as the source.
    """

    def __init__(
        self,
        base_ring,
        acting_group,
        acted_charts,
        source_transitions,
        quotient_transitions,
        source_scheme=None,
        *,
        quotient_scheme_engine=None,
        quotient_scheme_data=None,
    ) -> None:
        assert acting_group in FiniteGroups(), (
            f"the quotient of a glued scheme by {acting_group} is constructed only for a finite "
            f"group, but {acting_group} is not known to be finite; it is in {acting_group.category()}"
        )
        assert acting_group.has_selected_finite_group_generating_set(), (
            f"equivariance of the gluing maps is checked on a finite generating set of the group, "
            f"but {acting_group} was given without one; it is in {acting_group.category()}"
        )
        assert acted_charts.cardinality().is_finite() is True, (
            f"the quotient by {acting_group} is glued only from finitely many affine charts, but "
            f"{acting_group} acts on {acted_charts.cardinality()} charts"
        )
        self._base_ring = base_ring
        self._group = acting_group
        self._chart_index_set = finite_ordered_set(acted_charts.index_set())
        self._acted_charts = acted_charts
        for index in self.chart_index_set():
            assert acted_charts[index] in AffineGSchemes(acting_group, base_ring), (
                f"chart {index} must be an affine scheme over {base_ring} with an action of "
                f"{acting_group}, but it is {acted_charts[index]}, in {acted_charts[index].category()}"
            )
        assert int(self.chart_index_set().cardinality().finite_value()) > 0, (
            f"the quotient by {acting_group} is glued from affine charts, but no charts were given"
        )
        self._pair_index_set = finite_ordered_set(tuple(combinations(tuple(self.chart_index_set()), 2)))
        assert tuple(source_transitions.index_set()) == tuple(self._pair_index_set), (
            f"the gluing maps of the charts must be indexed by the pairs of charts "
            f"{tuple(self._pair_index_set)}, but they are indexed by {tuple(source_transitions.index_set())}"
        )
        assert tuple(quotient_transitions.index_set()) == tuple(self._pair_index_set), (
            f"the gluing maps of the quotient charts must be indexed by the pairs of charts "
            f"{tuple(self._pair_index_set)}, but they are indexed by {tuple(quotient_transitions.index_set())}"
        )
        self._source_transitions = source_transitions
        self._quotient_transitions = quotient_transitions
        self._quotient_scheme_engine = quotient_scheme_engine
        self._quotient_scheme_data = dict(quotient_scheme_data or {})
        match source_scheme:
            case None:
                self._source_scheme = Schemes(base_ring).glue_affine_atlas(self.source_charts(), source_transitions)
            case _:
                datum = source_scheme.gluing_datum()
                assert source_scheme.scheme_base_ring() is base_ring, (
                    f"the glued scheme {source_scheme} lies over {source_scheme.scheme_base_ring()}, "
                    f"but its quotient by {acting_group} is taken over {base_ring}"
                )
                assert tuple(datum.chart_indices()) == tuple(self.chart_index_set()), (
                    f"the glued scheme {source_scheme} has charts {tuple(datum.chart_indices())}, "
                    f"but the acted charts are {tuple(self.chart_index_set())}"
                )
                assert all(
                    (datum.transition_between(left, right).forward()
                     == self.source_transition_between(left, right).forward()) is True
                    for left, right in self.pair_index_set()
                ), (
                    f"the glued scheme {source_scheme} is glued along different maps of overlaps "
                    "than the given gluing maps of the acted charts"
                )
                assert all(datum.chart(index) is self.source_chart(index) for index in self.chart_index_set()), (
                    f"the charts of the glued scheme {source_scheme} are not the given affine "
                    f"schemes with an action of {acting_group}"
                )
                self._source_scheme = source_scheme
        self._verify_source_transition_equivariance()
        self._verify_quotient_descent_squares()

    def base_ring(self) -> ObjectOfCategory:
        return self._base_ring

    def acting_group(self) -> ObjectOfCategory:
        return self._group

    def chart_index_set(self) -> SetObject:
        return self._chart_index_set

    chart_indices = chart_index_set

    def pair_index_set(self) -> SetObject:
        return self._pair_index_set

    def normalize_chart_index(self, index):
        return self.chart_index_set()(index)

    def acted_charts(self):
        r"""The affine ``G``-schemes on the charts."""
        return self._acted_charts

    def acted_chart(self, index):
        return self.acted_charts()[self.normalize_chart_index(index)]

    @cached_method
    def source_charts(self):
        r"""The charts ``U_i`` the actions were stated on."""
        return finite_indexed_family(
            self.chart_index_set(),
            lambda index: self.acted_charts()[index].unacted_scheme(),
            name="Affine source charts of a finite glued invariant quotient",
        )

    def source_chart(self, index):
        return self.source_charts()[self.normalize_chart_index(index)]

    def source_transitions(self):
        return self._source_transitions

    def quotient_transitions(self):
        r"""The descended isomorphisms ``U_ij/G -> U_ji/G`` on the chart pairs."""
        return self._quotient_transitions

    def source_scheme(self):
        r"""``X``, glued from the charts along the source transitions."""
        return self._source_scheme

    source = source_scheme

    def source_transition_between(self, source_index, target_index):
        indices = self.chart_index_set()
        return self._transition_at(self.source_transitions(), indices(source_index), indices(target_index))

    def quotient_transition_between(self, source_index, target_index):
        indices = self.chart_index_set()
        return self._transition_at(self.quotient_transitions(), indices(source_index), indices(target_index))

    @cached_method(key=lambda self, transitions, source_index, target_index: (id(transitions), source_index, target_index))
    def _transition_at(self, transitions, source_index, target_index):
        r"""``phi_ij`` from a family holding one direction of each chart pair."""
        pair = (source_index, target_index)
        match pair:
            case _ if pair in transitions.index_set():
                return transitions[pair]
            case _:
                return _reversed_isomorphism(transitions[(target_index, source_index)])

    @cached_method
    def local_quotients(self):
        r"""The affine quotients ``U_i/G`` indexed by the charts."""
        return finite_indexed_family(
            self.chart_index_set(),
            lambda index: self.acted_charts()[index].affine_quotient(),
            name="Affine quotient charts of a finite glued invariant quotient",
        )

    def local_quotient(self, index):
        return self.local_quotients()[self.normalize_chart_index(index)]

    @cached_method
    def quotient_scheme(self):
        r"""``X/G``, glued from the ``U_i/G`` along the descended transitions."""
        data = dict(self._quotient_scheme_data)
        data.setdefault("quotient_data", self)
        return Schemes(self.base_ring()).glue_affine_atlas(
            self.local_quotients(),
            self.quotient_transitions(),
            _object_engine=self._quotient_scheme_engine,
            **data,
        )

    def quotient(self, *args, **kwargs):
        return self.quotient_scheme(*args, **kwargs)

    def source_chart_action(self, index, group_element):
        r"""``g`` acting on the chart ``U_i``, read from the acted chart on the same algebra."""
        assert group_element in self.acting_group(), f"{group_element} is not an element of {self.acting_group()}"
        return self._source_chart_action_at(self.normalize_chart_index(index), self.acting_group()(group_element))

    @cached_method
    def _source_chart_action_at(self, index, group_element):
        chart = self.source_chart(index)
        return Schemes(self.base_ring()).Mor(chart, chart)(
            self.acted_chart(index).action_of(group_element).coordinate_algebra_morphism()
        )

    def source_overlap_action(self, source_index, target_index, group_element):
        r"""``g`` restricted to the ``G``-stable overlap ``U_ij <= U_i``.

        The overlap is an open of ``U_i``; the chart action composed with its
        inclusion factors through it exactly when the action preserves the
        overlap, and ``corestriction`` asserts that hypothesis.
        """
        overlap = self.source_scheme().gluing_datum().overlap(source_index, target_index)
        return overlap.corestriction(self.source_chart_action(source_index, group_element) * overlap.inclusion())

    def _verify_source_transition_equivariance(self) -> None:
        for source_index, target_index in self.pair_index_set():
            transition = self.source_transition_between(source_index, target_index).forward()
            for group_generator in self.acting_group().group_generators():
                source_action = self.source_overlap_action(source_index, target_index, group_generator)
                target_action = self.source_overlap_action(target_index, source_index, group_generator)
                assert transition * source_action == target_action * transition, (
                    f"the gluing map of charts {source_index} and {target_index} does not commute "
                    f"with the action of the generator {group_generator} of {self.acting_group()}"
                )

    def local_quotient_morphism(self, index):
        r"""The affine quotient map of the acted chart ``i``."""
        return self.acted_chart(index).quotient_morphism()

    def local_source_quotient_morphism(self, index):
        r"""``U_i -> U_i/G`` on the chart ``U_i`` itself."""
        return self._local_source_quotient_morphism_at(self.normalize_chart_index(index))

    @cached_method
    def _local_source_quotient_morphism_at(self, index):
        acted = self.acted_chart(index)
        return Schemes(self.base_ring()).Mor(self.source_chart(index), acted.affine_quotient())(
            acted.quotient_morphism().coordinate_algebra_morphism()
        )

    def quotient_overlap_factor(self, source_index, target_index):
        r"""``U_ij -> U_ij/G``, the local quotient map landing in the descended quotient overlap."""
        source_overlap = self.source_scheme().gluing_datum().overlap(source_index, target_index)
        quotient_overlap = self.quotient_transition_between(source_index, target_index).forward().domain()
        return quotient_overlap.corestriction(
            self.local_source_quotient_morphism(source_index) * source_overlap.inclusion()
        )

    def _verify_quotient_descent_squares(self) -> None:
        for source_index, target_index in self.pair_index_set():
            transition = self.source_transition_between(source_index, target_index).forward()
            quotient_transition = self.quotient_transition_between(source_index, target_index).forward()
            source_factor = self.quotient_overlap_factor(source_index, target_index)
            target_factor = self.quotient_overlap_factor(target_index, source_index)
            assert quotient_transition * source_factor == target_factor * transition, (
                f"the gluing map of the quotient charts {source_index} and {target_index} is not "
                "induced by the gluing map of the original charts: the square with the quotient "
                "maps does not commute"
            )

    def action_of(self, group_element):
        r"""``g: X -> X``, glued from the chart actions by the Mor out of ``X``."""
        assert group_element in self.acting_group(), f"{group_element} is not an element of {self.acting_group()}"
        return self._action_at(self.acting_group()(group_element))

    @cached_method
    def _action_at(self, group_element):
        source = self.source_scheme()
        datum = source.gluing_datum()
        return source.Mor(source)(
            {
                index: datum.chart_embedding(index) * self.source_chart_action(index, group_element)
                for index in self.chart_index_set()
            }
        )

    @cached_method
    def action(self):
        r"""The action ``G -> End(X)``, ``g |-> (g: X -> X)``."""
        source = self.source_scheme()
        return Sets().Mor(self.acting_group(), source.Mor(source))(self.action_of)

    def global_action(self, *args, **kwargs):
        return self.action(*args, **kwargs)

    def fixed_locus_is_empty(self, group_element) -> bool:
        r"""Decide emptiness of ``X^g`` on the invariant affine atlas.

        The action preserves the atlas, so the fixed locus is empty exactly
        when its intersection with every chart is empty.  Each chart computes
        the full scheme-theoretic fixed ideal; no reduction is taken here.
        """
        group_element = self.acting_group()(group_element)
        return all(
            self.acted_chart(index).fixed_subobject_of(group_element).is_empty()
            for index in self.chart_index_set()
        )

    def common_fixed_locus_is_empty(self) -> bool:
        r"""Decide whether ``X^G`` is empty by the invariant affine atlas."""
        return all(
            self.acted_chart(index).fixed_subscheme().is_empty()
            for index in self.chart_index_set()
        )

    def nontrivial_stabilizer_locus_is_empty(self) -> bool:
        r"""Decide whether every nonidentity stabilizer locus misses every chart."""
        return all(
            self.acted_chart(index).nontrivial_stabilizer_subscheme().is_empty()
            for index in self.chart_index_set()
        )

    def action_is_free(self) -> bool:
        r"""Decide freeness locally on the invariant affine cover.

        Freeness is local on the source; it is the emptiness of the union of
        the nonidentity fixed loci on every chart, not of ``X^G``.
        """
        return self.nontrivial_stabilizer_locus_is_empty()

    @cached_method
    def quotient_morphism(self):
        r"""``X -> X/G``, glued from the affine quotient maps of the charts."""
        quotient = self.quotient_scheme()
        datum = quotient.gluing_datum()
        return self.source_scheme().Mor(quotient)(
            {
                index: datum.chart_embedding(index) * self.local_source_quotient_morphism(index)
                for index in self.chart_index_set()
            }
        )

    def factor_invariant_affine_morphism(self, morphism):
        r"""The unique factor ``X/G -> Y`` of an invariant morphism ``X -> Y`` to an affine ``Y``."""
        source = self.source_scheme()
        assert morphism.domain() is source, (
            f"to factor through the quotient by {self.acting_group()}, the morphism {morphism} "
            f"must start at {source}, but it starts at {morphism.domain()}"
        )
        target = morphism.codomain()
        base = self.base_ring()
        assert target in Schemes(base).Affine(), (
            f"factoring {morphism} through the quotient by {self.acting_group()} is implemented "
            f"only for an affine target, but {target} is in {target.category()}"
        )
        represented = source.Mor(target)(morphism)
        indices = self.chart_index_set()
        for index in indices:
            for group_generator in self.acting_group().group_generators():
                assert represented.local_map(index) * self.source_chart_action(index, group_generator) == represented.local_map(index), (
                    f"{morphism} is not invariant under {self.acting_group()}: on chart {index} it "
                    f"changes under the generator {group_generator}, so it does not factor through "
                    "the quotient"
                )
        local_factors = {
            index: self.acted_chart(index).factor_through_affine_quotient(
                Schemes(base).Mor(self.acted_chart(index), target)(
                    represented.local_map(index).coordinate_algebra_morphism()
                )
            )
            for index in indices
        }
        for source_index, target_index in self.pair_index_set():
            transition = self.quotient_transition_between(source_index, target_index).forward()
            assert (
                local_factors[source_index] * transition.domain().inclusion()
                == local_factors[target_index] * transition.codomain().inclusion() * transition
            ), (
                f"the factorizations of {morphism} through the quotient charts {source_index} and "
                f"{target_index} do not agree on their overlap"
            )
        factor = self.quotient_scheme().Mor(target)(local_factors)
        for index in indices:
            assert factor.local_map(index) * self.local_source_quotient_morphism(index) == represented.local_map(index), (
                f"the factorization of {morphism} through the quotient does not recover {morphism} "
                f"on chart {index} after composing with the quotient map"
            )
        return factor

    def descend_invariant_family(self, family_morphism):
        r"""Descend an invariant family map from the glued source to an affine base.

        A family here is a morphism to an affine parameter scheme; its
        descent is the unique quotient factor, so this is the family spelling
        of the same universal property.
        """
        return self.factor_invariant_affine_morphism(family_morphism)

    def _repr_(self):
        return f"Quotient of {self.source_scheme()} by {self.acting_group()} on a stable affine atlas"


def _c2_invariant_localization_lift(
    acted_chart,
    source_overlap,
    quotient_overlap,
    element,
):
    r"""Lift one invariant of ``A[d^-1]`` to ``A^G[N(d)^-1]`` for C2.

    If ``element=n/e`` is invariant and ``g`` is the nonidentity element, then
    ``n g(e)`` and ``e g(e)`` are invariant.  The latter is a power/unit
    multiple of the norm defining the quotient principal open, so its image is
    invertible there.  This avoids choosing a semi-invariant sign for ``d``.
    """
    group = acted_chart.acting_group()
    assert int(group.order()) == 2, (
        f"invariants of a distinguished open D(d) descend to the quotient here only for a group "
        f"of order 2, but {group} has order {group.order()}"
    )
    generator = next(iter(group.group_generators()))
    overlap_ring = source_overlap.coordinate_algebra()
    numerator, denominator = overlap_ring.localization_fraction_data(element)
    source_algebra = acted_chart.coordinate_algebra()
    action_pullback = acted_chart.action_of(generator).coordinate_algebra_morphism()
    numerator = source_algebra(numerator)
    denominator = source_algebra(denominator)
    conjugate_denominator = action_pullback(denominator)
    numerator_lift = acted_chart.invariant_algebra_element(numerator * conjugate_denominator)
    denominator_lift = acted_chart.invariant_algebra_element(denominator * conjugate_denominator)
    localization = quotient_overlap.coordinate_algebra().localization_map()
    denominator_image = localization(denominator_lift)
    assert denominator_image.is_unit(), (
        f"the norm d g(d) = {denominator * conjugate_denominator} of the denominator is not "
        f"invertible on {quotient_overlap}, so {element} does not descend to it"
    )
    return localization(numerator_lift) * denominator_image.inverse_of_unit()


def _c2_quotient_overlap_transition(
    datum,
    acted_charts,
    quotient_opens,
    source_index,
    target_index,
):
    r"""``U_ij/G -> U_ji/G`` for C2, transporting invariant rational functions through ``phi_ij``."""
    source_overlap = datum.overlap(source_index, target_index)
    target_overlap = datum.overlap(target_index, source_index)
    transition_pullback = datum.transition_between(
        source_index, target_index
    ).forward().coordinate_algebra_morphism()
    source_acted = acted_charts[source_index]
    target_inclusion = acted_charts[target_index].invariant_algebra_inclusion()
    target_localization = target_overlap.coordinate_algebra().localization_map()
    source_quotient_open = quotient_opens[source_index, target_index]
    target_quotient_open = quotient_opens[target_index, source_index]
    target_quotient_ring = target_quotient_open.coordinate_algebra()

    def map_invariant(value):
        source_value = transition_pullback(target_localization(target_inclusion(value)))
        return _c2_invariant_localization_lift(
            source_acted,
            source_overlap,
            source_quotient_open,
            source_value,
        )

    def pullback(element):
        numerator, denominator = target_quotient_ring.localization_fraction_data(element)
        denominator_image = map_invariant(denominator)
        assert denominator_image.is_unit(), (
            f"the denominator {denominator} of {element} is not a unit on {source_quotient_open}, "
            "so the element does not descend to the quotient overlap"
        )
        return map_invariant(numerator) * denominator_image.inverse_of_unit()

    return source_quotient_open.Mor(target_quotient_open)(
        target_quotient_ring.Mor(source_quotient_open.coordinate_algebra())(pullback)
    )


def _c2_chartwise_glued_invariant_quotient(
    source_scheme,
    acting_group,
    local_actions,
    *,
    quotient_scheme_engine=None,
    quotient_scheme_data=None,
):
    r"""Quotient a glued scheme by a chart-preserving C2 action.

    Every source overlap is a stable distinguished open.  Its defining element
    ``d`` need only be semi-invariant: the norm ``d g(d)`` is invariant and
    defines the descended principal open in the affine quotient chart.  The
    quotient transition is obtained by transporting invariant rational
    functions through the source transition and expressing them in the source
    invariant algebra via the invariant-ring certificate.
    """
    assert int(acting_group.order()) == 2, (
        f"the quotient of {source_scheme} chart by chart is implemented only for a group of "
        f"order 2, but {acting_group} has order {acting_group.order()}"
    )
    datum = source_scheme.gluing_datum()
    indices = datum.chart_index_set()
    assert tuple(local_actions.index_set()) == tuple(indices), (
        f"the local actions must be indexed by the charts {tuple(indices)} of {source_scheme}, "
        f"but they are indexed by {tuple(local_actions.index_set())}"
    )
    base = source_scheme.scheme_base_ring()
    group_generator = next(iter(acting_group.group_generators()))
    acted_charts = finite_indexed_family(
        indices,
        lambda index: AffineGSchemes(acting_group, base)(
            datum.chart(index),
            lambda element, index=index: (
                datum.chart(index).categorical_identity_morphism()
                if acting_group(element) == acting_group.one()
                else local_actions[index]
            ),
        ),
        name="Acted affine charts of a chartwise C2 quotient",
    )
    pair_indices = finite_ordered_set(tuple(datum.transition_index_set()))
    source_transitions = finite_indexed_family(
        pair_indices,
        lambda pair: datum.transition_between(*pair),
        name="Source transitions of a chartwise C2 quotient",
    )
    quotient_opens = {}
    for source_index, target_index in datum.transition_index_set():
        for left, right in ((source_index, target_index), (target_index, source_index)):
            defining = datum.chart(left).coordinate_algebra()(datum.overlap(left, right).distinguished_open_element())
            action_pullback = acted_charts[left].action_of(group_generator).coordinate_algebra_morphism()
            invariant_norm = acted_charts[left].invariant_algebra_element(defining * action_pullback(defining))
            quotient_opens[left, right] = acted_charts[left].affine_quotient().distinguished_open(invariant_norm)
    quotient_transitions_by_pair = {}
    for left, right in pair_indices:
        forward = _c2_quotient_overlap_transition(datum, acted_charts, quotient_opens, left, right)
        inverse = _c2_quotient_overlap_transition(datum, acted_charts, quotient_opens, right, left)
        quotient_transitions_by_pair[left, right] = Schemes(base).Core().Mor(forward.domain(), forward.codomain())(forward, inverse)
    quotient_transitions = finite_indexed_family(
        pair_indices,
        lambda pair: quotient_transitions_by_pair[pair],
        name="Descended quotient transitions of a chartwise C2 quotient",
    )
    return FiniteGluedInvariantQuotient(
        base,
        acting_group,
        acted_charts,
        source_transitions,
        quotient_transitions,
        source_scheme=source_scheme,
        quotient_scheme_engine=quotient_scheme_engine,
        quotient_scheme_data=quotient_scheme_data,
    )


__all__ = [
    "FiniteGluedInvariantQuotient",
]
