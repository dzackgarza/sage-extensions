r"""An integral-affine atlas morphism is a smooth map with chartwise affine maps.

A map of integral-affine structures is a smooth map together with, for each pair of charts
it is written in, an affine map of the common model (Alexeev--Engel, *Compactifications of
moduli spaces of K3 surfaces with a nonsymplectic involution*, arXiv:2208.10383v2, Definition
6.11, p. 30: an integral-affine structure is a family of charts with transitions in
``SL(2,Z) <ltimes> R^2``, and a map of two of them is affine chartwise).  The retained data
are the smooth map and those chartwise maps, indexed by the pair of charts they are affine
in -- which is what :meth:`integral_affine_morphism` reads, taking that pair as its two
arguments.

The specimen is the plane with its one-chart structure, mapped to itself.  There the
identity arrow's chartwise datum is the identity of the affine model, its composite with
itself is again an arrow between the same two atlases, and a smooth map of a different pair
of manifolds is refused rather than re-homed.
"""

from sage_extensions.all import *

import pytest


def _the_plane_and_its_atlas():
    r"""The plane's one-chart integral-affine atlas and its chart."""
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
    return plane, model, atlas


def test_the_identity_arrow_of_an_atlas_is_affine_in_each_of_its_charts() -> None:
    r"""The identity's chartwise map is the model's identity, at each chart's own pair.

    The arrows of the atlas are the smooth maps of the plane, so the identity's smooth map
    is the plane's identity, and its chartwise datum at the pair ``(chart, chart)`` is the
    identity of the model the chart lands in.
    """
    plane, model, atlas = _the_plane_and_its_atlas()
    arrows = IntegralAffineAtlases().Mor(atlas, atlas)

    identity = arrows.identity()

    assert identity is not None
    assert identity.domain() is atlas
    assert identity.codomain() is atlas
    assert identity.underlying_smooth_morphism().domain() is plane
    assert identity.smooth_atlas_morphism() is identity.underlying_smooth_morphism()
    affine = identity.integral_affine_morphism(plane, plane)
    assert affine.domain() is model
    assert affine.codomain() is model


def test_the_composite_of_an_atlas_arrow_with_itself_is_an_arrow_of_the_same_pair() -> None:
    r"""Composition keeps the endpoints and composes the chartwise maps.

    Two identity arrows compose to an arrow between the same two atlases whose chartwise
    datum at ``(chart, chart)`` is again the model's identity.
    """
    plane, model, atlas = _the_plane_and_its_atlas()
    arrows = IntegralAffineAtlases().Mor(atlas, atlas)
    identity = arrows.identity()

    composite = identity * identity

    assert composite.domain() is atlas
    assert composite.codomain() is atlas
    affine = composite.integral_affine_morphism(plane, plane)
    assert affine.domain() is model
    assert affine.codomain() is model


def test_an_atlas_arrow_of_a_smooth_map_between_other_manifolds_is_refused() -> None:
    r"""A smooth map that is not between the atlases' manifolds is not an atlas arrow.

    The plane's atlas is an atlas of the plane; a map of the plane into the real line has a
    codomain that is not that manifold, so it is refused instead of being re-homed.
    """
    plane, model, atlas = _the_plane_and_its_atlas()
    line = SmoothManifolds()(1, "R")

    with pytest.raises(AssertionError):
        IntegralAffineAtlases().Mor(atlas, atlas)(
            Sets().Mor(plane, line)(lambda point: line((0,))), {}
        )
