r"""A Chow group exposes the rational-equivalence morphism presenting it."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_curve_chow_group_retains_its_presentation() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    chow = plane.chow_group(1)
    rational_equivalence = chow.rational_equivalence_morphism()

    assert rational_equivalence.codomain() is chow.cokernel_projection().domain()
