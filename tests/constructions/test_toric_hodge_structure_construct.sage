r"""Projective plane has the standard pure Hodge diamond."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hodge_numbers_are_standard() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    hodge = plane.hodge_structure()

    assert hodge.hodge_number(0, 0) == 1
    assert hodge.hodge_number(1, 1) == 1
    assert hodge.hodge_number(2, 2) == 1
    assert hodge.hodge_number(2, 0) == 0
    assert hodge.hodge_number(0, 2) == 0
