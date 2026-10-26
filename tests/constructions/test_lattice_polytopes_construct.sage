r"""The unit cube is a smooth three-dimensional lattice polytope."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_unit_cube() -> None:
    lattice = ZZ.free_module(3)
    cube = LatticePolytopes(lattice)(
        [[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    )

    assert cube in LatticePolytopes(lattice)
    assert cube.dimension() == 3
    assert cube.n_vertices() == 8
    assert cube.facets().cardinality() == cardinal(6)
    assert cube.volume() == QQ(1)
    assert cube.n_integral_points() == cardinal(8)
    assert cube.is_smooth()
