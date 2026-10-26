r"""The represented toric Weil divisor group is the invariant divisor group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_weil_divisor_group_is_the_invariant_divisor_group() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.weil_divisor_group() is plane.torus_invariant_divisor_group()
