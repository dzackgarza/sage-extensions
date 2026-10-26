r"""The projective-plane fan defines a toric projective space with no torus factor."""

from sage_extensions.all import *  # noqa: F401,F403


def _toric_projective_plane():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans.projective_space_fan().toric_variety(QQ)


def test_projective_plane_from_its_fan_is_toric() -> None:
    assert _toric_projective_plane().is_toric()


def test_projective_plane_from_its_fan_is_projective_space() -> None:
    assert _toric_projective_plane().is_projective_space()


def test_projective_plane_has_no_torus_factor() -> None:
    assert not _toric_projective_plane().has_torus_factor()
