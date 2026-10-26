r"""Lattice-point counts, Ehrhart data and polar duality of small lattice polygons,
and the symmetry of the regular dodecahedron."""

from sage_extensions.all import *


def test_triangle_with_vertices_0_0_0_3_6_0_satisfies_pick() -> None:
    r"""Area 9; boundary points `\gcd(0,3) + \gcd(6,3) + \gcd(6,0) = 3 + 3 + 6 = 12`;
    Pick's theorem `9 = I + 12/2 - 1` gives 4 interior points, 16 in all."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (0, 3), (6, 0)))

    assert triangle.dimension() == 2
    assert triangle.volume() == 9
    assert triangle.normalized_volume() == 18
    assert triangle.n_integral_points() == 16
    assert triangle.n_interior_points() == 4
    assert triangle.n_boundary_points() == 12
    assert triangle.interior_contains_point((1, 1))
    assert not triangle.interior_contains_point((0, 1))


def test_square_has_ehrhart_polynomial_2t_plus_1_squared_and_h_star_1_6_1() -> None:
    r"""`t[-1,1]^2` has `(2t+1)^2` lattice points; `h^* = (1, L(1) - 3, I) = (1, 6, 1)`,
    summing to the normalized volume 8.  It is reflexive; its polar dual is the
    reflexive diamond `\operatorname{conv}\{\pm e_1, \pm e_2\}`, whose polar dual is
    the square again."""
    lattice = ZZ.free_module(2)
    square = ConvexPolytopes(lattice)(((-1, -1), (-1, 1), (1, 1), (1, -1)))
    polynomial = square.ehrhart_polynomial()
    t = polynomial.parent().algebra_generator("t")
    polar = square.polar_dual()

    assert polynomial == 4 * t**2 + 4 * t + 1
    assert tuple(square.h_star_vector()) == (1, 6, 1)
    assert square.is_reflexive()
    assert polar.is_reflexive()
    assert polar.n_integral_points() == 5
    assert polar.volume() == 2
    assert polar.polar_dual() == square


def test_dodecahedron_has_coxeter_diagram_h3_and_symmetry_group_of_order_120() -> None:
    r"""The dodecahedron `\{5, 3\}` has 20 vertices, 30 edges, 12 faces, and full
    symmetry group the Coxeter group `H_3` of order 120 (Coxeter, *Regular
    Polytopes*, Table I)."""
    dodecahedron = RegularPolytopes().from_schlafli_symbol("{5,3}")
    diagram = dodecahedron.symmetry_coxeter_diagram()
    first, second, third = diagram.vertices()

    assert dodecahedron.dimension() == 3
    assert tuple(dodecahedron.f_vector()) == (1, 20, 30, 12, 1)
    assert diagram.coxeter_entry(first, second) == 5
    assert diagram.coxeter_entry(second, third) == 3
    assert diagram.coxeter_entry(first, third) == 2
    assert dodecahedron.symmetry_group().order() == 120
