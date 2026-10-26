r"""The distinguished boundary points of the ADE polygon of type \(A_1\)."""

from sage_extensions.all import *


def test_the_distinguished_boundary_points_of_the_a1_polygon_are_the_points_of_its_two_blue_sides() -> None:
    r"""For \(A_1\), the integral points on the blue sides of \(Q\) are \((0,0),(0,1),(0,2),(1,1),(2,0)\), and \(p^*\) is among them.

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, §4 (the \(A_1\) polygon).
    """
    pair = LogPairs(QQ)("A", 1)
    polygon = pair.polygon()
    points = pair.distinguished_boundary_points()

    expected = {(0, 0), (0, 1), (0, 2), (1, 1), (2, 0)}
    assert points.cardinality() == 5
    assert all(point in polygon.boundary_integral_points() for point in points)
    assert {tuple(int(coordinate) for coordinate in point) for point in points} == expected
    assert tuple(int(coordinate) for coordinate in pair.p_star()) in expected
