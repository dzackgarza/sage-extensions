r"""Lattice-point invariants of an ADE polygon."""

from sage_extensions.all import *


def test_the_d4_polygon_has_nine_lattice_points_one_interior_and_area_four() -> None:
    r"""The \(D_4\) polygon is the square \([0,2]^2\): \(9\) lattice points, \(1\) interior,
    \(8\) on the boundary, area \(4\) and normalized area \(8\), as Pick's theorem
    \(A = I + B/2 - 1 = 1 + 4 - 1\) requires.

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, Table 1; Pick's theorem.
    """
    polygon = LogPairs(QQ)("D", 4).polygon()

    assert polygon.integral_points().cardinality() == 9
    assert polygon.interior_integral_points().cardinality() == 1
    assert polygon.boundary_integral_points().cardinality() == 8
    assert polygon.volume() == 4
    assert polygon.normalized_volume() == 8
