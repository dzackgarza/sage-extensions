r"""Closed and open subschemes of ``A^2_Q``: intersections, complements, corestrictions.

Each claim is a computation in the coordinate rings: ``V(I) cap V(J) = V(I + J)``;
the complement of ``V(f)`` is ``D(f) = Spec R_f``; a morphism ``Spec S -> Spec R`` lands in
``D(f)`` exactly when the pullback of ``f`` is a unit in ``S``, and in ``V(I)`` exactly when the
pullback kills ``I``.  The intersection multiplicity of ``y = x^2`` and ``y = 0`` at the origin is
``dim_Q Q[x, y]_{(x, y)}/(y - x^2, y) = dim_Q Q[x]/(x^2) = 2``.
"""

from sage_extensions.all import *


def _plane():
    ring = QQ["x,y"]
    return ring, ring.algebra_generator("x"), ring.algebra_generator("y"), AffineSchemes(QQ)(ring)


def test_the_tangent_line_meets_the_parabola_in_a_double_point() -> None:
    r"""``V(y - x^2) cap V(y) = Spec Q[x]/(x^2)``: zero-dimensional, ``x^2 = 0`` and ``x != 0``."""
    ring, x, y, plane = _plane()
    parabola = plane.closed_subscheme(y - x**2)
    tangent = plane.closed_subscheme(y)

    meet = parabola.intersection(tangent)
    restrict = meet.inclusion().coordinate_algebra_morphism()
    zero = meet.coordinate_algebra().zero()

    assert meet.dimension() == 0
    assert restrict(x) ** 2 == zero
    assert restrict(x) != zero
    assert restrict(y) == zero


def test_the_complement_of_the_x_axis_is_the_distinguished_open_of_y() -> None:
    r"""``A^2 \ V(y) = D(y)``, two-dimensional, on which ``y`` is a unit."""
    ring, x, y, plane = _plane()
    complement = plane.closed_subscheme(y).open_complement()

    assert complement.dimension() == 2
    assert complement.inclusion().coordinate_algebra_morphism()(y).is_unit()


def test_a_distinguished_open_knows_its_element_and_which_maps_land_in_it() -> None:
    r"""``D(x)`` is the distinguished open of ``x``; the line ``t -> (1, t)`` lies in it, the
    parabola ``t -> (t, t^2)`` does not (it meets ``x = 0``)."""
    ring, x, y, plane = _plane()
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    d_x = plane.distinguished_open(x)
    vertical = line.Mor(plane)(ring.Mor(line_ring)({"x": line_ring.one(), "y": t}))
    parabola = line.Mor(plane)(ring.Mor(line_ring)({"x": t, "y": t**2}))

    assert d_x.is_distinguished_open()
    assert d_x.distinguished_open_element() == x
    assert d_x.contains_image_of(vertical)
    assert not d_x.contains_image_of(parabola)


def test_a_map_into_a_distinguished_open_corestricts_to_it() -> None:
    r"""The line ``t -> (1, t)`` factors through ``D(x) -> A^2``."""
    ring, x, y, plane = _plane()
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    d_x = plane.distinguished_open(x)
    vertical = line.Mor(plane)(ring.Mor(line_ring)({"x": line_ring.one(), "y": t}))

    assert d_x.inclusion() * d_x.corestriction(vertical) == vertical


def test_a_map_into_the_parabola_corestricts_to_it() -> None:
    r"""``t -> (t, t^2)`` kills ``y - x^2``, so it factors through ``V(y - x^2)``."""
    ring, x, y, plane = _plane()
    line_ring = QQ["t"]
    t = line_ring.algebra_generator("t")
    line = AffineSchemes(QQ)(line_ring)
    parabola = plane.closed_subscheme(y - x**2)
    graph = line.Mor(plane)(ring.Mor(line_ring)({"x": t, "y": t**2}))

    assert parabola.inclusion() * parabola.corestriction(graph) == graph


def test_the_inclusion_of_d_xy_into_d_x_composes_to_its_inclusion_into_the_plane() -> None:
    r"""``D(xy) <= D(x) <= A^2``."""
    ring, x, y, plane = _plane()
    d_x = plane.distinguished_open(x)
    d_xy = plane.distinguished_open(x * y)

    assert d_x.inclusion() * d_xy.inclusion_into(d_x) == d_xy.inclusion()


def test_a_curve_in_the_plane_has_codimension_one_and_the_unit_ideal_cuts_out_nothing() -> None:
    r"""``codim V(y - x^2) = 1``; ``V(1)`` is empty while ``V(y)`` is not."""
    ring, x, y, plane = _plane()

    assert plane.closed_subscheme(y - x**2).codimension() == 1
    assert plane.closed_subscheme(ring.one()).is_empty()
    assert not plane.closed_subscheme(y).is_empty()


def test_the_parabola_and_its_tangent_meet_with_multiplicity_two() -> None:
    r"""``i_0(y - x^2, y) = dim_Q Q[x]/(x^2) = 2``."""
    ring, x, y, plane = _plane()
    parabola = plane.closed_subscheme(y - x**2)
    tangent = plane.closed_subscheme(y)

    assert parabola.intersection_multiplicity(tangent, ring.ideal(x, y)) == 2
