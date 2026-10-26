r"""The ideal ((x,y)) has one first syzygy relating its two selected generators."""

from sage_extensions.all import *  # noqa: F401,F403


def test_plane_origin_ideal_syzygy_matrix_annihilates_selected_generators() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    ideal = plane.ideal(x, y)
    syzygies = ideal.syzygy_matrix()

    assert syzygies.nrows() == 1
    assert syzygies.ncols() == 2
    assert syzygies[0, 0] * x + syzygies[0, 1] * y == plane.zero()
