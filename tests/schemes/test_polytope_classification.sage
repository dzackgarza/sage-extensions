r"""The Kreuzer--Skarke reflexive-polytope classification, as owned polytopes.

There are exactly sixteen reflexive polygons up to lattice equivalence, and
by Batyrev's theorem the toric variety of the normal fan of a reflexive
polytope is Gorenstein Fano; the projective plane is among them.
"""

from sage_extensions.all import *


def test_there_are_sixteen_reflexive_polygons() -> None:
    lattice = ZZ.free_module(2)
    reflexive = LatticePolytopes(lattice).reflexive_polytopes(2)

    assert reflexive.cardinality() == 16
    for polygon in reflexive:
        assert polygon in LatticePolygons(lattice)
        assert polygon.is_reflexive()
        assert polygon.n_interior_points() == 1


def test_one_reflexive_polygon_has_the_projective_plane_as_its_toric_variety() -> None:
    lattice = ZZ.free_module(2)
    reflexive = LatticePolytopes(lattice).reflexive_polytopes(2)
    varieties = tuple(polygon.toric_variety(QQ) for polygon in reflexive)

    assert any(variety.is_projective_space() for variety in varieties)
    assert any(variety.is_hirzebruch_surface(0) for variety in varieties)
    assert not all(variety.is_projective_space() for variety in varieties)




def test_twice_the_standard_triangle_has_no_interior_point_and_is_not_reflexive() -> None:
    r"""`\operatorname{conv}\{(0,0),(2,0),(0,2)\}` has no lattice point `(x, y)` with
    `x, y > 0` and `x + y < 2`, so it is not reflexive."""
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 2)))

    assert triangle.n_interior_points() == 0
    assert not triangle.is_reflexive()
