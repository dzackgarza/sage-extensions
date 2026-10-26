r"""The (A_1) ADE pair retains its blue boundary points, divisor, pyramid, and toric threefold."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_distinguished_boundary_points_are_exactly_the_two_blue_sides() -> None:
    pair = ADELogPairs(QQ)("A", 1)
    points = pair.distinguished_boundary_points()
    expected = {(0, 0), (0, 1), (0, 2), (1, 1), (2, 0)}

    assert points.cardinality() == cardinal(5)
    assert {tuple(int(c) for c in point) for point in points} == expected
    assert tuple(int(c) for c in pair.p_star()) in expected
    assert pair.blue_line_divisor() == pair.blue_divisor()


def test_a1_pyramid_and_cover_toric_threefold_have_expected_dimensions() -> None:
    pair = ADELogPairs(QQ)("A", 1)
    pyramid = pair.pyramid()
    threefold = pair.cover_toric_threefold()

    assert pyramid.dimension() == 3
    assert pyramid.n_vertices() == pair.polygon().n_vertices() + 1
    assert pyramid.is_lattice_polytope()
    assert threefold.relative_dimension() == 3
