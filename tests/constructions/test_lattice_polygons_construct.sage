r"""Standard lattice polygons expose their lattice-point and Ehrhart invariants."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_standard_simplex_and_the_reflexive_square() -> None:
    lattice = ZZ.free_module(2)
    simplex = LatticePolygons(lattice)([[0, 0], [1, 0], [0, 1]])
    square = LatticePolygons(lattice)([[-1, -1], [1, -1], [1, 1], [-1, 1]])

    assert simplex in ConvexPolygons(lattice)
    assert simplex in LatticePolytopes(lattice)
    assert simplex.dimension() == 2
    assert simplex.n_vertices() == 3
    assert simplex.volume() == QQ(1) / QQ(2)
    assert simplex.normalized_volume() == 1
    assert simplex.n_integral_points() == cardinal(3)
    assert simplex.n_interior_points() == cardinal(0)
    assert simplex.n_boundary_points() == cardinal(3)
    assert simplex.is_lattice_polytope()
    assert not simplex.is_reflexive()
    assert square.volume() == QQ(4)
    assert square.n_interior_points() == cardinal(1)
    assert square.n_boundary_points() == cardinal(8)
    assert square.is_reflexive()
    assert square.polar_dual().n_vertices() == 4
    assert square.polar_dual().volume() == QQ(2)


def test_ehrhart_polynomial_of_the_unit_square() -> None:
    lattice = ZZ.free_module(2)
    square = LatticePolygons(lattice)([[0, 0], [1, 0], [1, 1], [0, 1]])
    ehrhart = square.ehrhart_polynomial()
    t = ehrhart.parent().algebra_generator("t")

    assert ehrhart == (t + ehrhart.parent().one()) ** 2
    assert ehrhart(2) == 9
    assert square.h_star_vector().cardinality() == cardinal(3)
