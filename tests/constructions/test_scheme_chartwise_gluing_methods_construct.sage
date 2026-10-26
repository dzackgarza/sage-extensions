r"""Glued schemes construct chartwise closed/fixed subschemes and invariant quotients."""

from sage_extensions.all import *  # noqa: F401,F403


def _doubled_origin():
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(x)
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    doubled = Schemes(QQ).glue_affine_charts(line, line, gluing)
    return ring, x, line, doubled


def test_chartwise_closed_and_fixed_subschemes_of_doubled_origin() -> None:
    ring, x, line, doubled = _doubled_origin()
    origin = line.closed_subscheme(x)
    origins = doubled.chartwise_closed_subscheme((origin, origin))
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    fixed = doubled.chartwise_fixed_subscheme((negation, negation))

    assert origins.inclusion().codomain() is doubled
    assert origins.dimension() == 0
    assert origins.degree() == 2
    assert fixed.dimension() == 0
    assert fixed.degree() == 2


def test_chartwise_c2_quotient_of_doubled_origin() -> None:
    _ring, _x, line, doubled = _doubled_origin()
    ring = line.coordinate_algebra()
    x = ring.algebra_generator("x")
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    group = Groups.C(2)
    actions = doubled.gluing_datum().charts().map(lambda _chart: negation)
    quotient = doubled.c2_chartwise_invariant_quotient(group, actions)
    generator = quotient.acting_group().an_element()

    assert quotient.source_scheme() is doubled
    assert quotient.chart_index_set().cardinality() == cardinal(2)
    assert quotient.quotient_morphism() * quotient.action_of(generator) == quotient.quotient_morphism()
