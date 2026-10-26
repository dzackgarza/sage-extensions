r"""The hyperplane divisor on toric projective space is Cartier and defines O(1)."""

from sage_extensions.all import *  # noqa: F401,F403


def _toric_projective_plane():
    fan = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan()
    return fan.toric_variety(QQ)


def test_projective_plane_hyperplane_divisor_is_cartier() -> None:
    plane = _toric_projective_plane()

    assert plane.is_cartier(plane.hyperplane_divisor())


def test_hyperplane_divisor_invertible_sheaf_is_O1() -> None:
    plane = _toric_projective_plane()

    assert (
        plane.invertible_sheaf_of_divisor(plane.hyperplane_divisor())
        == plane.hyperplane_line_bundle()
    )
