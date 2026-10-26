r"""A convex polytope retains its ambient lattice and vertex set."""

from sage_extensions.all import *  # noqa: F401,F403


def test_unimodular_triangle_retains_lattice_and_vertices() -> None:
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (1, 0), (0, 1)))

    assert triangle.ambient_lattice() is lattice
    assert triangle.vertices().cardinality() == cardinal(3)
    assert all(vertex in lattice for vertex in triangle.vertices())
