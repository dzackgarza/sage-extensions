r"""The open chart images and chart changes of ``P^1`` glued from two lines along ``x -> 1/x``.

Source: Hartshorne, *Algebraic Geometry*, Example II.2.3.5: the maps ``i_k: X_k -> X``
of a gluing are isomorphisms onto open subschemes ``i_k(X_k)`` of ``X``, and the chart
change from ``U_2`` back to ``U_1`` is ``phi^{-1}``.  For ``phi: x -> 1/x`` on ``D(x)``,
``phi^{-1} = phi``.
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


def test_each_chart_is_isomorphic_to_its_open_image_in_the_projective_line() -> None:
    r"""``i_k = (image inclusion) o (X_k -> i_k(X_k))``, with ``X_k -> i_k(X_k)`` an isomorphism."""
    line, _punctured, _inversion, projective = _glued_projective_line()
    atlas = projective.gluing_datum()

    for index in (0, 1):
        embedding = atlas.chart_embedding(index)
        isomorphism = atlas.chart_isomorphism(index)
        image = atlas.chart_image(index)
        assert isomorphism.inverse() * isomorphism.forward() == line.Mor(line).identity()
        assert isomorphism.forward() * isomorphism.inverse() == image.Mor(image).identity()
        assert image.inclusion().codomain() is projective
        assert image.inclusion().is_open_immersion()
        assert embedding.open_image() is image
        assert embedding.open_inclusion() * isomorphism.forward() == embedding


def test_the_chart_change_back_is_the_inverse_of_x_to_one_over_x() -> None:
    r"""The chart change from chart 1 to chart 0 is ``phi^{-1}``, which for ``x -> 1/x`` is ``phi`` itself."""
    _line, punctured, inversion, projective = _glued_projective_line()
    atlas = projective.gluing_datum()
    back = atlas.transition_between(1, 0)

    assert atlas.left_overlap() is punctured and atlas.right_overlap() is punctured
    assert back.forward() == atlas.transition().inverse()
    assert back.inverse() == atlas.transition().forward()
    assert back.forward() == inversion
