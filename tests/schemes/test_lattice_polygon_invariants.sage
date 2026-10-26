r"""Lattice polygons: Pick's theorem, Ehrhart polynomials, ``h^*``-vectors, reflexivity,
polar duals, halfspace presentations and normal fans.

For a lattice polygon with ``I`` interior and ``B`` boundary lattice points, Pick's formula
gives area ``I + B/2 - 1``, the Ehrhart polynomial is ``L(t) = A t^2 + (B/2) t + 1``, and
``h^* = (1, L(1) - 3, I)``; these relations are checked on each specimen.  There are exactly
16 equivalence classes of reflexive polygons (Cox--Little--Schenck, *Toric Varieties*,
Thm. 8.3.7).
"""

from sage_extensions.all import *


def test_the_triangle_0_0_0_3_6_0_has_the_ehrhart_data_pick_predicts() -> None:
    r"""Area 9, 12 boundary and 4 interior lattice points (so 16 in all) give
    ``L(t) = 9 t^2 + 6 t + 1`` and ``h^* = (1, 16 - 3, 4) = (1, 13, 4)``, summing to the normalized
    volume ``2 * 9 = 18``."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (0, 3), (6, 0)))
    polynomial = triangle.ehrhart_polynomial()
    t = polynomial.parent().algebra_generator("t")

    assert polynomial == 9 * t**2 + 6 * t + 1
    assert tuple(triangle.h_star_vector()) == (1, 13, 4)
    assert triangle.volume() == 9
    assert triangle.normalized_volume() == 18
    assert triangle.is_lattice_polytope()
    assert triangle.is_compact()
    assert not triangle.is_reflexive()


def test_the_triangle_0_0_0_3_6_0_counts_its_lattice_points_by_pick() -> None:
    r"""Pick: ``9 = I + 12/2 - 1`` gives ``I = 4``, and ``16`` lattice points in all."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (0, 3), (6, 0)))

    assert triangle.n_integral_points() == 16
    assert triangle.n_interior_points() == 4
    assert triangle.n_boundary_points() == 12
    assert triangle.n_vertices() == 3


def test_the_integral_point_sets_of_the_triangle_split_into_interior_and_boundary() -> None:
    r"""The 16 lattice points of the triangle are the disjoint union of its 4 interior and 12
    boundary points; ``(1, 1)`` is interior, ``(0, 1)`` is on the boundary."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (0, 3), (6, 0)))
    inner = lattice((1, 1))
    edge = lattice((0, 1))

    assert inner in triangle.interior_integral_points()
    assert edge in triangle.boundary_integral_points()
    assert edge not in triangle.interior_integral_points()
    assert triangle.contains_point(edge)
    assert triangle.interior_contains_point(inner)
    assert not triangle.interior_contains_point(edge)
    assert triangle.integral_points().cardinality() == 16


def test_the_centred_square_is_reflexive_with_the_diamond_as_polar_dual() -> None:
    r"""``[-1, 1]^2`` has ``L(t) = (2t + 1)^2`` and ``h^* = (1, 6, 1)``; it contains the origin as
    its only interior point and is reflexive, its polar dual is the diamond
    ``conv(±e_1, ±e_2)`` (four vertices, reflexive again), and its normal fan is the fan of
    ``P^1 x P^1``, a smooth toric surface."""
    lattice = ZZ.free_module(2)
    square = ConvexPolytopes(lattice)(((-1, -1), (-1, 1), (1, 1), (1, -1)))
    polynomial = square.ehrhart_polynomial()
    t = polynomial.parent().algebra_generator("t")
    diamond = square.polar_dual()

    assert polynomial == (2 * t + 1) ** 2
    assert tuple(square.h_star_vector()) == (1, 6, 1)
    assert square.is_reflexive()
    assert diamond.is_reflexive()
    assert diamond.volume() == 2
    assert square.toric_variety(QQ).is_smooth()
    assert square.normal_fan().is_isomorphic(
        RationalPolyhedralFans(ZZ.free_module(2)).hirzebruch_surface_fan(0)
    )
    assert diamond.polar_dual() == square


def test_the_standard_simplex_from_its_halfspaces() -> None:
    r"""``{x >= 0, y >= 0, x + y <= 1}`` is the unimodular triangle ``conv(0, e_1, e_2)``: three
    vertices, area ``1/2``, three lattice points, none interior, and ``L(t) = (t+1)(t+2)/2``."""
    lattice = ZZ.free_module(2)
    simplex = ConvexPolytopes(lattice).from_halfspaces(((0, (1, 0)), (0, (0, 1)), (1, (-1, -1))))
    polynomial = simplex.ehrhart_polynomial()
    t = polynomial.parent().algebra_generator("t")

    assert simplex.volume() == 1 / 2
    assert polynomial == (t + 1) * (t + 2) / 2
    assert simplex.n_vertices() == 3
    assert simplex.is_smooth()
    assert simplex == ConvexPolytopes(lattice)(((0, 0), (1, 0), (0, 1)))


def test_there_are_sixteen_reflexive_polygons() -> None:
    r"""Up to lattice isomorphism there are exactly 16 reflexive polygons (CLS Thm. 8.3.7)."""
    lattice = ZZ.free_module(2)

    assert ConvexPolytopes(lattice).Integral().reflexive_polytopes(2).cardinality() == 16


def test_the_normal_fan_of_a_triangle_has_one_ray_per_edge() -> None:
    r"""The normal fan of a polygon has one ray per edge and one maximal cone per vertex, and is
    complete."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (0, 3), (6, 0)))
    fan = triangle.normal_fan()

    assert fan.is_complete()
    assert fan.rays().cardinality() == 3
    assert triangle.facets().cardinality() == 3
