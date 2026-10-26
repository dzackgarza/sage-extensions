r"""The doubled-origin sign quotient retains its local actions and stabilizer loci."""

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


def test_doubled_origin_sign_action_has_nonempty_fixed_and_stabilizer_loci() -> None:
    quotient = _doubled_origin_quotient()
    generator = quotient.acting_group().an_element()

    assert not quotient.fixed_locus_is_empty(generator)
    assert not quotient.common_fixed_locus_is_empty()
    assert not quotient.nontrivial_stabilizer_locus_is_empty()


def test_glued_source_chart_action_is_the_acted_chart_action() -> None:
    quotient = _doubled_origin_quotient()
    generator = quotient.acting_group().an_element()
    index = next(iter(quotient.chart_indices()))

    assert quotient.source_chart_action(index, generator) == quotient.acted_chart(
        index
    ).action_of(generator)
