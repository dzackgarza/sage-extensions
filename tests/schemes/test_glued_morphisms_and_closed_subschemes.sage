r"""Morphisms out of, and closed subschemes of, the line with a doubled origin.

Source: Stacks Project, Tag 01JA and Hartshorne, *Algebraic Geometry*, Example II.2.3.5:
a morphism out of a gluing is a family of chart morphisms agreeing on the overlaps,
and a closed subscheme is a family of closed subschemes of the charts agreeing on the
overlaps (closed immersions are local on the target).  On the line ``X`` with a doubled
origin (Example II.2.3.6), ``V(x)`` taken on both charts is the two origins, two rational
points; ``V(x - 1)`` on both charts is one point, since ``x = 1`` lies in the overlap
where the charts are identified; and the fixed locus of ``x -> -x`` is the two origins.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _doubled_origin():
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(x)
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    return ring, x, line, Schemes(QQ).glue_affine_charts(line, line, gluing)


def test_the_identity_of_the_doubled_line_is_the_identity_on_each_chart() -> None:
    r"""``id_X o i_k = i_k`` and ``f o id_X = f`` for the fold ``f: X -> A^1``."""
    _ring, _x, line, doubled = _doubled_origin()
    identity = doubled.Mor(doubled).identity()
    line_identity = line.Mor(line).identity()
    fold = doubled.Mor(line)((line_identity, line_identity))

    assert identity == doubled.categorical_identity_morphism()
    assert identity * doubled.gluing_datum().chart_embedding(0) == doubled.gluing_datum().chart_embedding(0)
    assert identity * doubled.gluing_datum().chart_embedding(1) == doubled.gluing_datum().chart_embedding(1)
    assert fold * identity == fold


def test_composing_the_fold_with_negation_restricts_to_negation_on_each_chart() -> None:
    r"""``(n o f) o i_k = n`` for the fold ``f`` and ``n: x -> -x``: composition is chartwise."""
    ring, x, line, doubled = _doubled_origin()
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    line_identity = line.Mor(line).identity()
    fold = doubled.Mor(line)((line_identity, line_identity))

    assert negation * fold * doubled.gluing_datum().chart_embedding(0) == negation
    assert negation * fold * doubled.gluing_datum().chart_embedding(1) == negation


def test_the_origin_on_both_charts_is_two_rational_points() -> None:
    r"""``V(x)`` on both charts glues to the two origins: a closed subscheme of ``X`` of dimension 0 and degree 2."""
    _ring, x, line, doubled = _doubled_origin()
    origin = line.closed_subscheme(x)
    origins = doubled.chartwise_closed_subscheme((origin, origin))

    assert origins.inclusion().codomain() is doubled
    assert origins.dimension() == 0
    assert origins.degree() == 2


def test_a_point_away_from_the_origin_is_not_doubled() -> None:
    r"""``V(x - 1)`` on both charts is one rational point: ``x = 1`` lies in the identified overlap."""
    ring, x, line, doubled = _doubled_origin()
    one = line.closed_subscheme(x - ring.one())
    point = doubled.chartwise_closed_subscheme((one, one))

    assert point.dimension() == 0
    assert point.degree() == 1


def test_the_fixed_locus_of_negation_on_the_doubled_line_is_the_two_origins() -> None:
    r"""``x -> -x`` on both charts fixes exactly ``V(x)`` on each: the two origins, of degree 2."""
    ring, x, line, doubled = _doubled_origin()
    negation = line.Mor(line)(ring.Mor(ring)({"x": -x}))
    fixed = doubled.chartwise_fixed_subscheme((negation, negation))

    assert fixed.dimension() == 0
    assert fixed.degree() == 2
