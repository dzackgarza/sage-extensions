r"""The affine line with its origin doubled, glued from two copies of ``Spec QQ[x]``.

Source: Hartshorne, *Algebraic Geometry*, Example II.2.3.5 (gluing two schemes along
an isomorphism of opens, with the open immersions ``i_1, i_2``), Example II.2.3.6
(gluing two affine lines along ``A^1 - {0}`` by the identity gives the line with the
origin doubled) and Example II.4.0.1 (that scheme is not separated over ``k``).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _doubled_origin():
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(x)
    identity = punctured.Mor(punctured).identity()
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(identity, identity)
    return line, punctured, Schemes(QQ).glue_affine_charts(line, line, gluing)


def test_the_two_origins_are_two_open_immersions_that_agree_off_the_origin() -> None:
    r"""``i_1, i_2: A^1 -> X`` are open immersions, distinct, and ``i_1 = i_2`` on ``A^1 - {0}``.

    The gluing identifies ``U_1 = A^1 - {0}`` with ``U_2`` by the identity, so the two
    open immersions restrict to one map on the punctured line (Example II.2.3.5); they
    differ at the origin, which is why the origin is doubled.
    """
    line, punctured, doubled = _doubled_origin()
    atlas = doubled.gluing_datum()
    first, second = atlas.chart_embedding(0), atlas.chart_embedding(1)

    assert atlas.chart(0) is line and atlas.chart(1) is line
    assert atlas.overlap(0, 1) is punctured
    assert first.is_open_immersion() and second.is_open_immersion()
    assert first != second
    assert first * punctured.inclusion() == second * punctured.inclusion()


def test_the_doubled_origin_is_glued_from_two_charts() -> None:
    r"""The gluing datum of Example II.2.3.6 has exactly two charts."""
    _line, _punctured, doubled = _doubled_origin()

    assert doubled.gluing_datum().number_of_charts() == 2


def test_the_doubled_origin_folds_onto_the_line() -> None:
    r"""The identity on both charts agrees on the overlap, so it glues to ``X -> A^1``.

    A morphism out of a gluing is a family of chart morphisms agreeing on the
    overlaps; its restriction along each ``i_k`` is the chart morphism.  Over
    ``Spec QQ`` both charts restrict the structure morphism of ``X`` to that of ``A^1``.
    """
    line, _punctured, doubled = _doubled_origin()
    atlas = doubled.gluing_datum()
    identity = line.Mor(line).identity()
    fold = doubled.Mor(line)((identity, identity))

    assert fold * atlas.chart_embedding(0) == identity
    assert fold * atlas.chart_embedding(1) == identity
    assert doubled.structure_morphism() * atlas.chart_embedding(1) == line.structure_morphism()
    assert line.structure_morphism() * fold == doubled.structure_morphism()


def test_the_line_with_doubled_origin_is_not_separated() -> None:
    r"""Example II.4.0.1: the diagonal of ``X`` is not closed, so ``X`` is not separated."""
    _line, _punctured, doubled = _doubled_origin()

    assert not doubled.is_separated()


def test_the_line_with_doubled_origin_is_a_curve_that_is_not_affine() -> None:
    r"""``X`` has dimension 1, and it is not affine: an affine scheme is separated."""
    _line, _punctured, doubled = _doubled_origin()

    assert doubled.dimension() == 1
    assert not doubled.is_affine()
