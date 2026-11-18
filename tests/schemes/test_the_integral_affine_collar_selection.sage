r"""An integral-affine collar is the selection of a face, its neighbourhood and a chart.

Glueing two integral-affine pieces along a common face is an affine operation only when
each piece is presented with a collar along that face: the face, a neighbourhood of it, and
an affine chart of the neighbourhood in which the gluing is written (Alexeev--Engel,
*Compactifications of moduli spaces of K3 surfaces with a nonsymplectic involution*,
arXiv:2208.10383v2, Construction 6.16, pp. 31--32).  The object is that selection and
nothing else.

The specimen is the plane with its one-chart integral-affine structure.  Its face and its
neighbourhood are selected by the identity of the plane -- the degenerate collar, since a
face of a surface is an edge or a vertex and neither is a point set that can be built in
this tree -- and the chart is the one chart of the atlas.  What is asserted is that the four
data are retained object for object, and that three selections are refused: a piece that is
not an integral-affine manifold, a face selected into another manifold, and a chart stated
on a manifold that is not the neighbourhood.
"""

from sage_extensions.all import *

import pytest


def _the_plane_and_its_affine_manifold():
    r"""The plane's one-chart integral-affine structure, its manifold and its chart."""
    lattice = ZZ.free_module(2)
    plane = SmoothManifolds()(2, "R^2")
    model = RR.free_module(lattice.module_generating_set())
    chart = Sets().Mor(plane, model)(lambda point: model(tuple(point.coordinates())))
    atlas = IntegralAffineAtlases().on(
        plane,
        model,
        {plane: plane},
        {plane: Sets().Mor(plane, plane).identity()},
        {plane: chart},
        {},
        {},
    )
    return plane, IntegralAffineManifolds().on(plane, atlas), chart


def test_the_collar_retains_its_face_its_neighbourhood_and_its_chart() -> None:
    r"""The four selected data are the four the collar answers, object for object.

    The face and the neighbourhood are the plane's identity, so the collar's face is the
    plane and its piece is the integral-affine manifold the chart is added to.
    """
    plane, piece, chart = _the_plane_and_its_affine_manifold()
    identity = Sets().Mor(plane, plane).identity()

    collar = IntegralAffineCollars().on(piece, identity, identity, chart)

    assert collar in IntegralAffineCollars()
    assert collar.affine_piece() is piece
    assert collar.face_inclusion() is identity
    assert collar.neighborhood_inclusion() is identity
    assert collar.collar_chart() is chart
    assert collar.face() is plane
    assert collar.face_inclusion().codomain() is plane
    assert collar.neighborhood_inclusion().codomain() is plane
    assert collar.underlying_affine_manifold() is piece


def test_a_collar_selected_on_the_wrong_piece_or_with_the_wrong_chart_is_refused() -> None:
    r"""Three selections that are not collar data are refused rather than re-homed.

    A collar is selected on an integral-affine piece, so the smooth manifold the piece adds
    its structure to is not one; a face and a neighbourhood are selected in that piece, so
    a map into a space that is not the piece's manifold is not one; and the chart is stated
    on the neighbourhood, so a chart of another manifold is not one.
    """
    plane, piece, chart = _the_plane_and_its_affine_manifold()
    identity = Sets().Mor(plane, plane).identity()
    model = chart.codomain()

    with pytest.raises(AssertionError):
        IntegralAffineCollars().on(plane, identity, identity, chart)
    with pytest.raises(AssertionError):
        IntegralAffineCollars().on(
            piece, identity, identity, Sets().Mor(model, model).identity()
        )
