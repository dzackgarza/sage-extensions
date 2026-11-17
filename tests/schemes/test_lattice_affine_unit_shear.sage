r"""The unit shear of a real affine space on a selected integral lattice.

An integral-affine structure on a real oriented surface is a family of charts
into one real affine model whose transition maps lie in ``GL(2,Z) ⋉ R^2``
(Alexeev--Engel, *Compactifications of moduli spaces of K3 surfaces with a
nonsymplectic involution*, arXiv:2208.10383v2, Definition 6.11, p. 30); the
determinant-one transitions are the oriented ones.  The elementary unit shear
``s(x, y) = (x + y, y)`` is such a transition: it preserves the lattice ``ZZ^2``
and its determinant is one.

The model is the real vector space on the integral basis of ``ZZ^2``, the affine
space is that vector space as a torsor over itself, and the lattice is selected
by its own inclusion ``ZZ^2 -> model`` -- the tangent lattice, whose points are
the lattice points of the model, which is what the shear acts on.

The two charts of the specimen are the identity chart and the sheared one;
their transition is the shear itself, so its linear part is the shear's action
on the lattice.
"""

from sage_extensions.all import *


def _plane_on_a_lattice():
    r"""The model space on the integral basis of ``ZZ^2``, the affine space it is, and that space with the lattice selected by the lattice's own inclusion."""
    lattice = ZZ.free_module(2)
    labels = tuple(lattice.module_generating_set())
    model = RR.free_module(labels)
    basis = tuple(model.module_generator(label) for label in labels)
    lattice_basis = tuple(lattice.module_generator(label) for label in labels)
    ring_inclusion = ZZ.Mor(RR)(lambda number: RR(number))
    semilinear = ModulesOverCommutativeRings().Mor(lattice, model)
    inclusion = semilinear(
        ring_inclusion,
        semilinear.compatible_mor(ring_inclusion)(
            {label: model.module_generator(label) for label in labels}
        ),
    )
    affine = RealAffineSpaces().on(
        model,
        model,
        lambda translation, point: translation + point,
        lambda left, right: left - right,
        model.zero(),
    )
    return lattice, lattice_basis, model, basis, inclusion, affine, AffineSpacesWithLattice().on(affine, inclusion)


def _shears(lattice, lattice_basis, model, basis, affine, space):
    r"""The unit shear and its inverse, as affine maps of the selected lattice and of the model."""
    linear = model.hom([basis[0], basis[0] + basis[1]], codomain=model)
    inverse_linear = model.hom([basis[0], basis[1] - basis[0]], codomain=model)
    lattice_map = lattice.hom(
        [lattice_basis[0], lattice_basis[0] + lattice_basis[1]], codomain=lattice
    )
    inverse_lattice_map = lattice.hom(
        [lattice_basis[0], lattice_basis[1] - lattice_basis[0]], codomain=lattice
    )
    affine_morphisms = RealAffineSpaces().Mor(affine, affine)
    shear = AffineSpacesWithLattice().Mor(space, space)(
        affine_morphisms(linear, Sets().Mor(model, model)(lambda point: linear(point))),
        lattice_map,
    )
    inverse = AffineSpacesWithLattice().Mor(space, space)(
        affine_morphisms(
            inverse_linear, Sets().Mor(model, model)(lambda point: inverse_linear(point))
        ),
        inverse_lattice_map,
    )
    return shear, inverse


def test_the_unit_shear_and_its_inverse_move_a_point_and_a_lattice_point() -> None:
    r"""``s(3, -3) = (0, -3)`` and ``s^{-1}(0, -3) = (3, -3)``; the lattice map takes the first integral basis vector to itself and the second to the sum of the two."""
    lattice, lattice_basis, model, basis, inclusion, affine, space = _plane_on_a_lattice()
    shear, inverse = _shears(lattice, lattice_basis, model, basis, affine, space)
    point = space(model((3, -3)))

    assert shear(point) == model((0, -3))
    assert inverse(shear(point)) == point
    assert (inverse * shear)(point) == point
    assert shear.lattice_map()(lattice_basis[0]) == lattice_basis[0]
    assert shear.lattice_map()(lattice_basis[1]) == lattice_basis[0] + lattice_basis[1]
    assert (inverse * shear).lattice_map()(lattice_basis[1]) == lattice_basis[1]


def test_the_shear_linear_part_fixes_the_invariant_integral_direction() -> None:
    r"""The invariant tangent direction of the shear is ``(1, 0)``: its linear part fixes the first integral basis vector and carries the second to the sum."""
    lattice, lattice_basis, model, basis, inclusion, affine, space = _plane_on_a_lattice()
    shear, inverse = _shears(lattice, lattice_basis, model, basis, affine, space)
    linear = shear.linear_part()

    assert linear(basis[0]) == basis[0]
    assert linear(basis[1]) == basis[0] + basis[1]
    assert inverse.linear_part()(basis[0] + basis[1]) == basis[1]


def test_the_shear_is_the_linear_part_of_the_transition_of_a_two_chart_atlas() -> None:
    r"""Two charts of the plane whose affine charts differ by the shear: the transition's linear part is the shear on the model, and the double overlap's gluing equation is the inverse."""
    lattice, lattice_basis, model, basis, inclusion, affine, space = _plane_on_a_lattice()
    shear, inverse = _shears(lattice, lattice_basis, model, basis, affine, space)
    plane = SmoothManifolds()(2, "R^2")
    identity_chart = plane.chart("U", "x y")
    sheared_chart = plane.chart("V", "u v")
    identity_points = Sets().Mor(plane, plane).identity()
    sheared_points = Sets().Mor(model, model)(lambda point: shear(point))
    atlas = IntegralAffineAtlases().on(
        plane,
        model,
        {identity_chart: plane, sheared_chart: plane},
        {identity_chart: identity_points, sheared_chart: identity_points},
        {
            identity_chart: Sets().Mor(plane, model)(
                lambda point: model(tuple(point.coordinates()))
            ),
            sheared_chart: Sets().Mor(plane, model)(
                lambda point: sheared_points(model(tuple(point.coordinates())))
            ),
        },
        {
            (identity_chart, sheared_chart): Sets().Mor(model, model).identity(),
            (sheared_chart, identity_chart): Sets().Mor(model, model).identity(),
        },
        {
            (identity_chart, sheared_chart): shear,
            (sheared_chart, identity_chart): inverse,
        },
    )

    transition = atlas.transition_map(identity_chart, sheared_chart)
    linear = atlas.transition_linear_part(identity_chart, sheared_chart)

    assert transition(space(model((3, -3)))) == model((0, -3))
    assert linear(basis[0]) == basis[0]
    assert linear(basis[1]) == basis[0] + basis[1]
    assert atlas.overlap_inclusion(identity_chart, sheared_chart).domain() is model
    assert (atlas.transition_map(sheared_chart, identity_chart) * transition)(
        space(model((3, -3)))
    ) == model((3, -3))


def test_the_polygons_vertices_are_placed_in_the_model_by_the_lattices_inclusion() -> None:
    r"""The moment polygon's four vertices, read in the integral basis and carried into the model by the lattice's own inclusion, are the printed ones: the polygon is placed in the model the affine space is on, by the arrow that lattice is selected by."""
    lattice, lattice_basis, model, basis, inclusion, affine, space = _plane_on_a_lattice()
    polygon = ConvexPolytopes(lattice)(((0, 0), (3, -3), (5, -1), (2, 2)))
    placed = tuple(inclusion(vertex.to_vector()) for vertex in polygon.vertices())

    assert space.affine_lattice() is lattice
    assert space.lattice_inclusion() is inclusion
    assert polygon.n_vertices() == 4
    for vector in ((0, 0), (3, -3), (5, -1), (2, 2)):
        assert model(vector) in placed
