r"""Morphisms of affine schemes: images, inverse images, graphs, fixed loci, composition.

A morphism ``Spec A -> Spec B`` over ``k`` is the same datum as a ``k``-algebra map
``B -> A`` (Hartshorne, *Algebraic Geometry*, II.2.3), so every claim below is a
statement about coordinate algebras that holds by that equivalence.
"""

from sage_extensions.all import *


def test_the_image_of_the_cuspidal_parametrization_is_the_cusp() -> None:
    r"""The scheme-theoretic image of ``t -> (t^2, t^3)`` is ``V(y^2 - x^3)``.  The morphism factors
    through ``V(I)`` exactly when ``I`` lies in the kernel of ``x -> t^2, y -> t^3``, so the smallest
    such closed subscheme (Stacks, Tag 01R7) is ``V`` of that kernel, which is ``(y^2 - x^3)``.  On
    the image ``y^2 = x^3`` while ``x``, ``y`` and ``y - x`` stay nonzero, and the parametrization is not a
    closed immersion since ``t`` is not in the image of the pullback."""
    plane_ring = QQ["x,y"]
    line_ring = QQ["t"]
    x = plane_ring.algebra_generator("x")
    y = plane_ring.algebra_generator("y")
    t = line_ring.algebra_generator("t")
    plane = AffineSchemes(QQ)(plane_ring)
    line = AffineSchemes(QQ)(line_ring)
    parametrization = line.Mor(plane)(plane_ring.Mor(line_ring)({"x": t**2, "y": t**3}))

    image = parametrization.scheme_theoretic_image()
    restrict = image.inclusion().coordinate_algebra_morphism()
    zero = image.coordinate_algebra().zero()

    assert image.inclusion().codomain() is plane
    assert restrict(y) ** 2 == restrict(x) ** 3
    assert restrict(x) != zero
    assert restrict(y) != zero
    assert restrict(y - x) != zero
    assert image.dimension() == 1
    assert not parametrization.is_closed_immersion()


def test_the_x_axis_embedding_is_a_closed_immersion() -> None:
    r"""``t -> (t, 0)`` has surjective pullback ``x -> t, y -> 0``, so it is ``Spec`` of a quotient
    map and a closed immersion."""
    plane_ring = QQ["x,y"]
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    plane = AffineSchemes(QQ)(plane_ring)
    line = AffineSchemes(QQ)(line_ring)
    axis = line.Mor(plane)(plane_ring.Mor(line_ring)({"x": t, "y": line_ring.zero()}))

    assert axis.is_closed_immersion()


def test_the_fibre_of_the_cusp_parametrization_over_the_origin_is_a_double_point() -> None:
    r"""The inverse image of ``V(x, y)`` under ``t -> (t^2, t^3)`` is ``V(t^2, t^3) = V(t^2)``:
    ``t^2 = 0`` there while ``t != 0``, a nonreduced point."""
    plane_ring = QQ["x,y"]
    line_ring = QQ["t"]
    x = plane_ring.algebra_generator("x")
    y = plane_ring.algebra_generator("y")
    t = line_ring.algebra_generator("t")
    plane = AffineSchemes(QQ)(plane_ring)
    line = AffineSchemes(QQ)(line_ring)
    parametrization = line.Mor(plane)(plane_ring.Mor(line_ring)({"x": t**2, "y": t**3}))

    fibre = parametrization.inverse_image(plane.closed_subscheme(x, y))
    restrict = fibre.inclusion().coordinate_algebra_morphism()
    zero = fibre.coordinate_algebra().zero()

    assert fibre.inclusion().codomain() is line
    assert restrict(t) ** 2 == zero
    assert restrict(t) != zero
    assert fibre.dimension() == 0


def test_composition_of_affine_morphisms_is_composition_of_pullbacks_in_reverse() -> None:
    r"""``(g f)^# = f^# g^#``: squaring twice pulls ``t`` back to ``t^4``, and the cusp
    parametrization after squaring pulls ``x`` back to ``t^4``.  Negation is an involution."""
    plane_ring = QQ["x,y"]
    line_ring = QQ["t"]
    x = plane_ring.algebra_generator("x")
    y = plane_ring.algebra_generator("y")
    t = line_ring.algebra_generator("t")
    plane = AffineSchemes(QQ)(plane_ring)
    line = AffineSchemes(QQ)(line_ring)
    square = line.Mor(line)(line_ring.Mor(line_ring)({"t": t**2}))
    negate = line.Mor(line)(line_ring.Mor(line_ring)({"t": -t}))
    parametrization = line.Mor(plane)(plane_ring.Mor(line_ring)({"x": t**2, "y": t**3}))

    assert (square * square).coordinate_algebra_morphism()(t) == t**4
    assert (parametrization * square).coordinate_algebra_morphism()(y) == t**6
    assert parametrization.compose(square) == parametrization * square
    assert square.then(parametrization) == parametrization * square
    assert negate * negate == line.categorical_identity_morphism()
    assert negate != line.categorical_identity_morphism()


def test_a_rational_point_evaluates_under_a_morphism() -> None:
    r"""The point ``t = 3`` of ``A^1`` maps under ``t -> t^2`` to the point ``t = 9``."""
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    square = line.Mor(line)(line_ring.Mor(line_ring)({"t": t**2}))
    point = line.point_morphism((3,))

    assert point.coordinate_algebra_morphism()(t) == 3
    assert square.evaluate_at(point).coordinate_algebra_morphism()(t) == 9


def test_the_fixed_locus_of_negation_on_the_line_is_the_reduced_origin() -> None:
    r"""The fixed subscheme of ``t -> -t`` over ``Q`` is the equalizer ``V(t - (-t)) = V(2t) = V(t)``:
    a point, on which ``t = 0``."""
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    negate = line.Mor(line)(line_ring.Mor(line_ring)({"t": -t}))

    fixed = negate.fixed_subscheme()

    assert fixed.dimension() == 0
    assert fixed.inclusion().coordinate_algebra_morphism()(t) == fixed.coordinate_algebra().zero()


def test_the_graph_of_squaring_is_the_parabola_in_the_plane() -> None:
    r"""The graph of ``f: t -> t^2`` is the closed subscheme of ``A^1 x A^1`` on which the second
    coordinate is the square of the first; it is isomorphic to ``A^1`` by the first projection, so it
    has dimension one, and the graph morphism lands in ``A^1 x A^1``."""
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    square = line.Mor(line)(line_ring.Mor(line_ring)({"t": t**2}))

    graph = square.graph_subscheme()
    product = graph.inclusion().codomain()
    first, second = product.projections()
    restrict = graph.inclusion().coordinate_algebra_morphism()
    u = first.coordinate_algebra_morphism()(t)
    v = second.coordinate_algebra_morphism()(t)

    assert graph.dimension() == 1
    assert restrict(v) == restrict(u) ** 2
    assert restrict(v) != restrict(u)
    assert square.graph_morphism().codomain().dimension() == 2
