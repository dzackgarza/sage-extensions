r"""A hyperbolic arrow is the projective map of an integral isometry of its lattice.

``HH(C^+)`` is the hyperboloid ``{x in C^+ : q(x) = 1}`` of a positive-cone
component of a lattice ``L`` of signature ``(1, n)``, with the metric ``-b`` on
each tangent space (Helgason, *Differential Geometry, Lie Groups, and Symmetric
Spaces*, Ch. X, §6, Table V, type BDI with ``q = 1``).  An isometry ``g`` of
``L`` preserves ``b``, hence ``q`` and the positive cone and its two components,
and it commutes with the projection to rays, so it induces a map of the
hyperboloid models that preserves ``-b``: an arrow of ``HyperbolicSpaces(n)``.

These tests are the arrow's own mathematics at the smallest specimen that shows
it, the Lorentz plane ``<2> + <-2>`` whose hyperboloid is the hyperbolic line.
In the chart ``hyperboloid`` a point is written ``x = s t + y`` with ``t`` the
component's timelike vector and ``y`` the coordinate in a basis of
``t^perp``: for the line and ``t = e_0`` that coordinate is ``b(x, e_1) / 2``,
so the reflection in the root ``e_1`` -- which fixes ``e_0`` and negates
``e_1`` -- sends the point of coordinate ``y`` to the point of coordinate
``-y``.
"""

from sage_extensions.all import *


def _hyperbolic_line():
    r"""Return the Lorentz plane, its hyperboloid ``HH^1``, and the root of its reflection."""
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    timelike, root = lattice.module_generators()
    component = PositiveConeComponents(lattice).component_through(timelike)
    return lattice, HyperbolicSpaces(1)(component), root


def _hyperbolic_plane():
    r"""Return ``I_{1,2}``, its hyperboloid ``HH^2`` through ``e_0``, and the root ``e_1``."""
    lattice = Lattices.IPQ(1, 2)
    timelike, root, _second = lattice.module_generators()
    component = PositiveConeComponents(lattice).component_through(timelike)
    return lattice, HyperbolicSpaces(2)(component), root


def test_an_arrow_of_hyperbolic_spaces_is_built_from_an_integral_isometry_of_their_lattice() -> None:
    r"""The reflection in the root is an isometry of the lattice, and it is an arrow of ``Mor(HH^1, HH^1)``."""
    lattice, space, root = _hyperbolic_line()
    isometries = space.category().Mor(space, space)
    reflection = isometries(lattice.reflection(root))

    assert reflection.parent() is isometries
    assert reflection.domain() is space
    assert reflection.codomain() is space
    assert reflection.lattice_isometry() == lattice.reflection(root)


def test_a_hyperbolic_arrow_is_an_arrow_of_the_manifolds_it_is_between() -> None:
    r"""The arrow is also an arrow of the Riemannian, smooth and topological Mors.

    An isometry of hyperbolic spaces preserves ``-b``, so it is a Riemannian
    local isometry, a smooth map and a continuous map of the spaces it is
    between.  The categories state exactly that, the hyperbolic category being a
    subcategory of the Riemannian one, which declares the smooth one: so the
    arrow the hyperbolic owner builds is admitted by each of those Mors at the
    same endpoints, and is not an arrow of its own Mor only.
    """
    lattice, space, root = _hyperbolic_line()
    reflection = space.category().Mor(space, space)(lattice.reflection(root))

    assert reflection in RiemannianManifolds().Mor(space, space)
    assert reflection in SmoothManifolds().Mor(space, space)
    assert reflection in TopologicalManifolds().Mor(space, space)


def test_a_hyperbolic_arrow_states_its_coordinate_sections() -> None:
    r"""The arrow is a smooth morphism of the two models, on their one pair of charts.

    A hyperboloid model has the one chart ``hyperboloid``, so the arrow's
    representation is one tuple of sections on the pair
    ``(hyperboloid, hyperboloid)``, one section per chart coordinate of the
    codomain, and the value of the ``i``-th at a point is the ``i``-th
    coordinate of the arrow's image there.  The smooth owner's own evaluation of
    that tuple is the arrow's value, so the arrow's action is its coordinate
    representation and not a computation beside it.
    """
    lattice, space, root = _hyperbolic_line()
    reflection = space.category().Mor(space, space)(lattice.reflection(root))
    label = tuple(space.chart_labels())[0]
    half = RR(1) / RR(2)
    point = space((half,))
    image = reflection(point)
    sections = reflection.chart_maps()[label, label]

    assert tuple(reflection.chart_maps().keys()) == ((label, label),)
    assert sections[0](point) == image.coordinates()[0]
    assert reflection.underlying_smooth_morphism()(point) == image


def test_a_hyperbolic_arrow_moves_a_point_by_the_isometry_that_induces_it() -> None:
    r"""The reflection negates the hyperboloid coordinate, and its square is the identity."""
    lattice, space, root = _hyperbolic_line()
    reflection = space.category().Mor(space, space)(lattice.reflection(root))
    half = RR(1) / RR(2)
    point = space((half,))

    assert reflection(point) == space((-half,))
    assert reflection(reflection(point)) == point


def test_a_hyperbolic_arrow_of_a_higher_dimensional_space_negates_one_coordinate() -> None:
    r"""On ``HH^2`` of ``I_{1,2}``, the reflection in ``e_1`` sends ``(y_1, y_2)`` to ``(-y_1, y_2)``.

    The chart ``hyperboloid`` writes a point of ``HH^2`` as ``x = s e_0 + y_1 e_1
    + y_2 e_2`` with ``s = sqrt(1 + y_1^2 + y_2^2)``, since ``e_0`` is the
    timelike vector of the component and ``e_1, e_2`` an orthogonal basis of its
    perpendicular.  The reflection in the root ``e_1`` fixes ``e_0`` and ``e_2``
    and negates ``e_1``, so it leaves ``s`` and ``y_2`` alone and negates
    ``y_1`` -- and because the vector it produces still pairs positively with
    ``e_0``, no sign is taken.
    """
    lattice, space, root = _hyperbolic_plane()
    reflection = space.category().Mor(space, space)(lattice.reflection(root))
    third = RR(1) / RR(3)
    fifth = RR(1) / RR(5)
    point = space((third, fifth))

    assert reflection(point) == space((-third, fifth))
    assert reflection(reflection(point)) == point
    assert space.dimension() == 2


def test_an_arrow_of_hyperbolic_spaces_may_have_a_different_codomain() -> None:
    r"""An arrow ``HH(C^+) -> HH(-C^+)`` is read in the codomain's own frame.

    The two components of ``{q > 0}`` are different hyperbolic spaces, and the
    chart of the second is written from its own timelike vector ``-t``: the same
    hyperboloid vector has the coordinate ``y`` in the first and ``-y`` in the
    second.  So the reflection, which is an isometry of the lattice and fixes
    ``e_0``, is an arrow between the two spaces whose image of the point of
    coordinate ``1/2`` is the point of the codomain of coordinate ``-1/2``.
    """
    lattice, space, root = _hyperbolic_line()
    opposite = HyperbolicSpaces(1)(
        PositiveConeComponents(lattice).component_through(
            -space.positive_cone_component().timelike_vector()
        )
    )
    reflection = space.category().Mor(space, opposite)(lattice.reflection(root))
    half = RR(1) / RR(2)

    assert reflection.domain() is space
    assert reflection.codomain() is opposite
    assert reflection(space((half,))) == opposite((-half,))


def test_the_identity_arrow_of_hyperbolic_spaces_is_the_identity_isometry() -> None:
    r"""The identity arrow fixes every point and is induced by the identity of ``O(L)``."""
    lattice, space, _root = _hyperbolic_line()
    isometries = space.category().Mor(space, space)
    identity = isometries.identity()
    point = space((RR(1) / RR(3),))

    assert identity.lattice_isometry() == lattice.Aut().one()
    assert identity(point) == point
