r"""Gluing two affine lines along the punctured line.

Source: Hartshorne, *Algebraic Geometry*, Example II.2.3.5 (the line with a doubled
origin is not separated, II.4.0.1) and Example II.2.3.6 (gluing along
`t \mapsto 1/t` gives `\mathbb{P}^1`).
"""

from sage_extensions.all import *


def _line_and_punctured_line():
    chart = AffineSpaces(QQ)(1, names=("x",))
    x = chart.coordinate_ring().algebra_generator("x")
    return chart, x, chart.distinguished_open(x)


def test_gluing_two_lines_along_the_identity_gives_the_non_separated_doubled_origin() -> None:
    chart, _x, punctured = _line_and_punctured_line()
    glued = Schemes(QQ).glue_affine_charts(chart, chart, punctured.Mor(punctured).identity())

    assert glued.relative_dimension() == 1
    assert not glued.is_separated()
    assert not glued.is_affine()


def test_the_doubled_origin_maps_to_the_line_by_the_identity_on_both_charts() -> None:
    chart, _x, punctured = _line_and_punctured_line()
    glued = Schemes(QQ).glue_affine_charts(chart, chart, punctured.Mor(punctured).identity())
    identity = chart.Mor(chart).identity()
    collapse = glued.Mor(chart)((identity, identity))

    assert collapse * glued.gluing_datum().chart_embedding(0) == identity
    assert collapse * glued.gluing_datum().chart_embedding(1) == identity
    assert glued.gluing_datum().chart_embedding(0) != glued.gluing_datum().chart_embedding(1)


def test_gluing_two_lines_along_t_to_one_over_t_gives_the_projective_line() -> None:
    chart, x, punctured = _line_and_punctured_line()
    ring = punctured.coordinate_ring()
    inversion = punctured.Mor(punctured)(ring.Mor(ring)({"x": ring(x).inverse_of_unit()}))
    glued = Schemes(QQ).glue_affine_charts(chart, chart, inversion)

    assert glued.is_separated()
    assert glued.is_proper()
    assert glued.is_isomorphic(ProjectiveSpaces(QQ)(1))
