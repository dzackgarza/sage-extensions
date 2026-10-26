r"""The Chow groups of projective plane are rank one in every geometric degree."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_chow_groups_have_rank_one() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.chow_group(2).module_rank() == 1
    assert plane.chow_group(1).module_rank() == 1
    assert plane.chow_group(0).module_rank() == 1
