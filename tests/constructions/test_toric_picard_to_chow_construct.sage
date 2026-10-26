r"""For smooth toric projective plane, Picard and codimension-one Chow agree."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_picard_to_chow_map_has_canonical_endpoints() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    comparison = plane.picard_to_chow_isomorphism()

    assert comparison.domain() is plane.picard_group()
    assert comparison.codomain() is plane.chow_group(1)
