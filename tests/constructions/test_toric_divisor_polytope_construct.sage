r"""The divisor of a toric polarization recovers its lattice polytope."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polarizing_divisor_recovers_the_selected_polytope() -> None:
    lattice = ZZ.free_module(2)
    triangle = LatticePolytopes(lattice)([(0, 0), (1, 0), (0, 1)])
    plane = triangle.toric_variety(QQ)

    assert plane.divisor_polytope(plane.polarizing_divisor()) == triangle
