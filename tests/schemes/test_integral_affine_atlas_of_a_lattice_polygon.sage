r"""The integral-affine atlas of a lattice polygon's plane, and the integral-affine
manifold it presents.

An integral-affine structure on a real surface is a family of charts into one affine model
whose transition maps lie in ``SL(2,Z) ⋉ R^2`` (Alexeev--Engel, *The birational geometry of
moduli of Enriques surfaces*, arXiv:2208.10383v2, Definition 6.11, p. 30).  The Symington
polytopes that carry the integral-affine spheres of the cusps are cut from the moment
polygon of such a plane and reglued along its edges (Construction 6.16, pp. 31--32).  On a
lattice polygon the chart into the model preserves the lattice, so the polygon's lattice is
the model's lattice.

The specimen is the moment polygon of Alexeev--Engel--Garza--Schaffler, *Compact moduli of
Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025), Example 4.13 (p. 606): the
vectors ``(3,-3), (2,2), (-3,3), (-2,-2)`` put successively end-to-end, which close up into
the parallelogram with the vertices ``(0,0), (3,-3), (5,-1), (2,2)``.

The charts' values at points of the manifold are not asserted: a point of a real smooth
manifold cannot be built in this tree, because ``manifolds._manifold_expression_ring``
raises the engine's symbolic ring through an owned ring constructor, which has no route for
it.  That is the manifold layer's own defect, and it leaves the atlas' maps asserted at
their endpoints, which is what the construction establishes.
"""

from sage_extensions.all import *


def test_the_plane_of_a_lattice_polygon_is_an_integral_affine_atlas_in_the_model() -> None:
    r"""``R^2`` carries one chart, whose domain is the whole plane, whose inclusion into the
    plane is its identity, and whose affine map into the model ``R^2`` is the identity on
    coordinates.  The atlas retains those maps -- the exact ones, not reconstructions of
    them (``OWN-15``) -- and the model is the plane on the polygon's own lattice, which the
    printed vertices are read in."""
    lattice = ZZ.free_module(2)
    polygon = ConvexPolytopes(lattice)(((0, 0), (3, -3), (5, -1), (2, 2)))
    plane = SmoothManifolds()(2, "R^2")
    labels = tuple(lattice.module_generating_set())
    model = RR.free_module(lattice.module_generating_set())
    printed_vertices = ((0, 0), (3, -3), (5, -1), (2, 2))

    def coordinates_of(vertex):
        return tuple(int(vertex.to_vector()(label)) for label in labels)

    inclusion = Sets().Mor(plane, plane).identity()
    chart_map = Sets().Mor(plane, model)(lambda point: model(tuple(point.coordinates())))

    assert polygon.n_vertices() == 4
    assert sorted(coordinates_of(vertex) for vertex in polygon.vertices()) == sorted(
        printed_vertices
    )
    assert model.module_generating_set() is lattice.module_generating_set()

    atlas = IntegralAffineAtlases().on(
        plane,
        model,
        {plane: plane},
        {plane: inclusion},
        {plane: chart_map},
        {},
        {},
    )

    assert atlas in IntegralAffineAtlases()
    assert atlas.underlying_smooth_manifold() is plane
    assert atlas.affine_model() is model
    assert atlas.chart_domains()[plane] is plane
    assert atlas.chart_domain_inclusion(plane) is inclusion
    assert atlas.affine_chart(plane) is chart_map
    assert atlas.chart_domain_inclusion(plane).domain() is plane
    assert atlas.chart_domain_inclusion(plane).codomain() is plane
    assert atlas.affine_chart(plane).codomain() is model


def test_the_manifold_presented_by_an_atlas_is_the_manifold_it_is_selected_on() -> None:
    r"""The integral-affine structure is added to the exact plane the atlas is selected on
    (``OWN-15``), so the presented manifold reports that plane, that atlas and the plane's
    dimension, and the atlas presents itself as that same manifold."""
    lattice = ZZ.free_module(2)
    plane = SmoothManifolds()(2, "R^2")
    model = RR.free_module(lattice.module_generating_set())
    atlas = IntegralAffineAtlases().on(
        plane,
        model,
        {plane: plane},
        {plane: Sets().Mor(plane, plane).identity()},
        {plane: Sets().Mor(plane, model)(lambda point: model(tuple(point.coordinates())))},
        {},
        {},
    )

    manifold = IntegralAffineManifolds().on(plane, atlas)
    presented = atlas.integral_affine_manifold()

    assert manifold in IntegralAffineManifolds()
    assert manifold.underlying_smooth_manifold() is plane
    assert manifold.affine_atlas() is atlas
    assert manifold.affine_charts() is atlas.affine_charts()
    assert manifold.dimension() == 2
    assert presented.underlying_smooth_manifold() is plane
    assert presented.affine_atlas() is atlas
    assert presented.dimension() == manifold.dimension()
