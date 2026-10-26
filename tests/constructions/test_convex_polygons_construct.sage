r"""A rational triangle need not be a lattice polygon."""

from sage_extensions.all import *  # noqa: F401,F403


def test_half_unit_triangle_is_not_a_lattice_polygon() -> None:
    lattice = ZZ.free_module(2)
    triangle = ConvexPolygons(lattice)(
        [[0, 0], [QQ(1) / 2, 0], [0, QQ(1) / 2]]
    )

    assert triangle in ConvexPolygons(lattice)
    assert triangle in ConvexPolytopes(lattice)
    assert triangle.is_lattice_polytope() is False
