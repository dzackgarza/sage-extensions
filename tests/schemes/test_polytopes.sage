r"""Lattice-point counts, Ehrhart data, polar duality and containment of small lattice
polygons, and the symmetry of the regular dodecahedron."""

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


def test_containment_of_a_triangle_is_decided_by_its_vertices() -> None:
    r"""`A \subseteq B` exactly when every vertex of `A` satisfies the halfspaces of `B`.

    `2\Delta = \operatorname{conv}\{(0,0),(2,0),(0,2)\}` is cut out by
    `x \ge 0`, `y \ge 0` and `x + y \le 2`.  The triangle on `(0,0), (1,0), (0,1)`
    lies in it, and so does `\operatorname{conv}\{(1,0),(2,0),(1,1)\}`, whose two
    last vertices lie on the facet `x + y = 2`.
    `\operatorname{conv}\{(0,0),(3,0),(0,1)\}` does not: its vertex `(3,0)` has
    `x + y = 3`.  Nor does `2\Delta` lie in the first triangle, whose hyperplane
    `x + y = 1` leaves the vertex `(2,0)` of `2\Delta` outside.  The halfspaces
    give `2\Delta` its vertices, and the same two answers hold against that
    presentation of it.
    """
    lattice = ZZ.free_module(2)
    doubled = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 2)))
    cut = ConvexPolytopes(lattice).from_halfspaces(
        ((0, (1, 0)), (0, (0, 1)), (2, (-1, -1)))
    )
    inner = ConvexPolytopes(lattice)(((0, 0), (1, 0), (0, 1)))
    touching = ConvexPolytopes(lattice)(((1, 0), (2, 0), (1, 1)))
    reaching_out = ConvexPolytopes(lattice)(((0, 0), (3, 0), (0, 1)))

    assert inner.is_contained_in(doubled)
    assert touching.is_contained_in(doubled)
    assert not reaching_out.is_contained_in(doubled)
    assert not doubled.is_contained_in(inner)
    assert inner.is_contained_in(inner)

    assert inner.is_contained_in(cut)
    assert touching.is_contained_in(cut)
    assert not reaching_out.is_contained_in(cut)
    assert not cut.is_contained_in(inner)


def test_triangles_with_one_vertex_set_are_one_polytope_with_one_hash() -> None:
    r"""A polytope is its vertex set: one triangle is one set, five are five hashes.

    A polytope is the convex hull of its vertices, so two polytopes of one
    lattice are equal exactly when they have the same vertices.  The triangle
    on ``(0, 0), (1, 0), (0, 1)`` listed from another corner is the same
    polytope, and so is the polytope of the halfspaces ``x >= 0``, ``y >= 0``
    and ``x + y <= 1``, whose vertices the private exact polyhedron computes
    instead of reading.  Five triangles with different vertices are five sets,
    so their hashes take five values.  An equal triangle is one factor, so the
    interned products of ``SET-05`` find one product for its three
    presentations, and a triangle with other vertices gives another product.
    """
    lattice = ZZ ^ 2
    category = ConvexPolytopes(lattice)
    triangle = category(((0, 0), (1, 0), (0, 1)))
    relocated = category(((1, 0), (0, 1), (0, 0)))
    cut = category.from_halfspaces(((0, (1, 0)), (0, (0, 1)), (1, (-1, -1))))

    assert triangle == relocated
    assert triangle == cut
    assert hash(triangle) == hash(relocated)
    assert hash(triangle) == hash(cut)
    assert cut.n_vertices() == 3

    product = Sets().product((triangle, Sets.Δ[1]))
    assert product.factor(0) is triangle
    assert Sets().product((triangle, Sets.Δ[1])) is product
    assert Sets().product((relocated, Sets.Δ[1])) is product
    assert Sets().product((cut, Sets.Δ[1])) is product

    other = category(((0, 0), (2, 0), (0, 1)))
    other_product = Sets().product((other, Sets.Δ[1]))
    assert other_product is not product
    assert other_product.factor(0) is other

    triangles = [
        category(vertices)
        for vertices in (
            ((0, 0), (1, 0), (0, 1)),
            ((0, 0), (2, 0), (0, 1)),
            ((0, 0), (1, 0), (0, 2)),
            ((0, 0), (1, 1), (0, 1)),
            ((0, 0), (1, 0), (1, 1)),
        )
    ]
    assert triangles[0] != triangles[1]
    assert cardinal(sum(1 for _ in {hash(each) for each in triangles})) == cardinal(5)
