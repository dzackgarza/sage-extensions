r"""Finite glued invariant quotients retain their local and global quotient data."""

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


def test_glued_quotient_retains_source_and_quotient_aliases() -> None:
    quotient = _doubled_origin_quotient()

    assert quotient.source() is quotient.source_scheme()
    assert quotient.quotient() is quotient.quotient_scheme()
    assert quotient.global_action() is quotient.action()


def test_glued_quotient_retains_acted_source_and_quotient_charts() -> None:
    quotient = _doubled_origin_quotient()
    index = next(iter(quotient.chart_indices()))

    assert quotient.normalize_chart_index(index) == index
    assert quotient.acted_chart(index) is quotient.acted_charts()[index]
    assert quotient.source_chart(index) is quotient.source_charts()[index]
    assert quotient.local_quotient(index) is quotient.local_quotients()[index]


def test_local_quotient_morphisms_have_the_canonical_chart_endpoints() -> None:
    quotient = _doubled_origin_quotient()
    index = next(iter(quotient.chart_indices()))
    local = quotient.local_quotient_morphism(index)
    source_local = quotient.local_source_quotient_morphism(index)

    assert local.domain() is quotient.acted_chart(index)
    assert local.codomain() is quotient.local_quotient(index)
    assert source_local.domain() is quotient.source_chart(index)
    assert source_local.codomain() is quotient.local_quotient(index)
