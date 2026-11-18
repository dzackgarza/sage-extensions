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


def test_an_arrow_of_hyperbolic_spaces_is_built_from_an_integral_isometry_of_their_lattice() -> None:
    r"""The reflection in the root is an isometry of the lattice, and it is an arrow of ``Mor(HH^1, HH^1)``."""
    lattice, space, root = _hyperbolic_line()
    isometries = space.category().Mor(space, space)
    reflection = isometries(lattice.reflection(root))

    assert reflection.parent() is isometries
    assert reflection.domain() is space
    assert reflection.codomain() is space
    assert reflection.lattice_isometry() == lattice.reflection(root)


def test_a_hyperbolic_arrow_moves_a_point_by_the_isometry_that_induces_it() -> None:
    r"""The reflection negates the hyperboloid coordinate, and its square is the identity."""
    lattice, space, root = _hyperbolic_line()
    reflection = space.category().Mor(space, space)(lattice.reflection(root))
    half = RR(1) / RR(2)
    point = space((half,))

    assert reflection(point) == space((-half,))
    assert reflection(reflection(point)) == point


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
