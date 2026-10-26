r"""The toric boundary of projective plane is its anticanonical divisor."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_toric_boundary_is_anticanonical() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.toric_boundary_divisor() == -plane.canonical_divisor()
