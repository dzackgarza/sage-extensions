r"""The projective line glued from two affine lines along ``x -> 1/x``.

Source: Hartshorne, *Algebraic Geometry*, Example II.2.3.5 (a gluing along
``phi: U_1 -> U_2`` has open immersions ``i_1, i_2`` with ``i_1 = i_2 o phi`` on
``U_1``) and Example III.4.0.3 (``P^1_k`` is covered by two affine lines with
coordinates ``x`` and ``1/x``).  ``P^1`` is separated and proper over ``k``, and it is
not affine since ``H^0(P^1, O) = k`` (Hartshorne II.4.9, III.5.1).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _glued_projective_line():
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    punctured = line.distinguished_open(x)
    functions = punctured.coordinate_algebra()
    restriction = punctured.inclusion().coordinate_algebra_morphism()
    reciprocal = functions.induced_morphism(ring.Mor(functions)({"x": restriction(x).inverse_of_unit()}))
    inversion = punctured.Mor(punctured)(reciprocal)
    gluing = Schemes(QQ).Core().Mor(punctured, punctured)(inversion, inversion)
    return line, punctured, inversion, Schemes(QQ).glue_affine_charts(line, line, gluing)


def test_x_to_one_over_x_is_an_involution_of_the_punctured_line() -> None:
    r"""On ``D(x) = Spec QQ[x, 1/x]`` the map ``x -> 1/x`` squares to the identity and is not it."""
    _line, punctured, inversion, _projective = _glued_projective_line()

    assert inversion * inversion == punctured.Mor(punctured).identity()
    assert inversion != punctured.Mor(punctured).identity()


def test_the_two_charts_of_the_projective_line_agree_through_the_gluing() -> None:
    r"""The chart at ``0`` and the chart at ``infinity`` are distinct open immersions over ``QQ``."""
    line, _punctured, _inversion, projective = _glued_projective_line()
    atlas = projective.gluing_datum()
    at_zero, at_infinity = atlas.chart_embedding(0), atlas.chart_embedding(1)

    assert at_zero.is_open_immersion() and at_infinity.is_open_immersion()
    assert at_zero != at_infinity
    assert projective.structure_morphism() * at_zero == line.structure_morphism()
    assert projective.structure_morphism() * at_infinity == line.structure_morphism()


def test_the_chart_at_infinity_is_the_chart_at_zero_through_x_to_one_over_x() -> None:
    r"""``i_1 = i_2 o phi`` on ``D(x)``, while ``i_1 != i_2`` there since ``phi`` is not the identity."""
    _line, punctured, inversion, projective = _glued_projective_line()
    atlas = projective.gluing_datum()
    at_zero, at_infinity = atlas.chart_embedding(0), atlas.chart_embedding(1)

    assert at_zero * punctured.inclusion() == at_infinity * punctured.inclusion() * inversion
    assert at_zero * punctured.inclusion() != at_infinity * punctured.inclusion()


def test_constant_maps_glue_to_a_map_from_the_projective_line_to_the_affine_line() -> None:
    r"""The constant map to ``3`` on both charts agrees on ``D(x)``, so it glues to ``P^1 -> A^1``."""
    line, _punctured, _inversion, projective = _glued_projective_line()
    ring = line.coordinate_algebra()
    constant = line.Mor(line)(ring.Mor(ring)({"x": 3 * ring.one()}))
    glued = projective.Mor(line)((constant, constant))

    assert glued * projective.gluing_datum().chart_embedding(0) == constant
    assert glued * projective.gluing_datum().chart_embedding(1) == constant


def test_the_glued_projective_line_is_proper_and_not_affine() -> None:
    r"""``P^1`` over ``QQ`` is separated and proper, and it is not affine."""
    _line, _punctured, _inversion, projective = _glued_projective_line()

    assert projective.is_separated()
    assert projective.is_proper()
    assert not projective.is_affine()


def test_the_glued_projective_line_is_the_projective_line() -> None:
    r"""The gluing is isomorphic to ``Proj QQ[x_0, x_1]``, a smooth curve."""
    _line, _punctured, _inversion, projective = _glued_projective_line()

    assert projective.is_isomorphic(ProjectiveSpaces(QQ)(1))
    assert projective.dimension() == 1
    assert projective.is_smooth()
