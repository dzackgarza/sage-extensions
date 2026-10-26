r"""Finite glued invariant quotients retain source and quotient transition data."""

from sage_extensions.all import *  # noqa: F401,F403


def _doubled_origin_quotient():
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(x)
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    doubled = Schemes(QQ).glue_affine_charts(line, line, gluing)
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    group = Groups.C(2)
    actions = doubled.gluing_datum().charts().map(lambda _chart: negation)
    return doubled.c2_chartwise_invariant_quotient(group, actions)


def test_glued_quotient_transition_lookup_agrees_with_retained_families() -> None:
    quotient = _doubled_origin_quotient()
    pair = next(iter(quotient.pair_index_set()))
    source_index, target_index = pair

    assert quotient.source_transition_between(
        source_index, target_index
    ) is quotient.source_transitions()[pair]
    assert quotient.quotient_transition_between(
        source_index, target_index
    ) is quotient.quotient_transitions()[pair]


def test_overlap_action_and_quotient_factor_have_the_expected_endpoints() -> None:
    quotient = _doubled_origin_quotient()
    source_index, target_index = next(iter(quotient.pair_index_set()))
    source_transition = quotient.source_transition_between(source_index, target_index)
    quotient_transition = quotient.quotient_transition_between(source_index, target_index)
    identity = quotient.acting_group().one()
    overlap_action = quotient.source_overlap_action(
        source_index, target_index, identity
    )
    overlap_quotient = quotient.quotient_overlap_factor(source_index, target_index)

    assert overlap_action.domain() is source_transition.domain()
    assert overlap_action.codomain() is source_transition.domain()
    assert overlap_quotient.domain() is source_transition.domain()
    assert overlap_quotient.codomain() is quotient_transition.domain()
