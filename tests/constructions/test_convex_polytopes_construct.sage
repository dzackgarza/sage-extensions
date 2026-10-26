r"""A unimodular tetrahedron realizes the basic rational convex-polytope invariants."""

from sage_extensions.all import *  # noqa: F401,F403


def test_unimodular_tetrahedron() -> None:
    lattice = ZZ.free_module(3)
    tetrahedron = ConvexPolytopes(lattice)(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    )

    assert tetrahedron in ConvexPolytopes(lattice)
    assert tetrahedron.dimension() == 3
    assert tetrahedron.n_vertices() == 4
    assert tetrahedron.volume() == QQ(1) / QQ(6)
    assert tetrahedron.normalized_volume() == 1
    assert tetrahedron.n_integral_points() == cardinal(4)
