r"""The standard simplex polarization of projective space is its hyperplane class."""

from sage_extensions.all import *  # noqa: F401,F403


def _polarized_projective_plane():
    lattice = ZZ.free_module(2)
    triangle = LatticePolytopes(lattice)([(0, 0), (1, 0), (0, 1)])
    return triangle.toric_variety(QQ)


def test_standard_simplex_polarizing_divisor_is_the_hyperplane_divisor() -> None:
    plane = _polarized_projective_plane()

    assert plane.polarizing_divisor() == plane.hyperplane_divisor()


def test_projective_plane_O1_is_its_hyperplane_line_bundle() -> None:
    plane = _polarized_projective_plane()

    assert plane.O1() == plane.hyperplane_line_bundle()
