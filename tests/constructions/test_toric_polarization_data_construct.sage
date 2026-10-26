r"""The standard lattice simplex gives polarized projective space."""

from sage_extensions.all import *  # noqa: F401,F403


def _standard_triangle():
    lattice = ZZ.free_module(2)
    return LatticePolytopes(lattice)([(0, 0), (1, 0), (0, 1)])


def test_standard_triangle_toric_variety_is_polarized() -> None:
    triangle = _standard_triangle()
    plane = triangle.toric_variety(QQ)

    assert plane.is_polarized()
    assert plane.is_projective_space()


def test_standard_triangle_is_retained_as_polarizing_polytope() -> None:
    triangle = _standard_triangle()
    plane = triangle.toric_variety(QQ)

    assert plane.polarizing_polytope() is triangle
