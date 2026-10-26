r"""The projective plane has its standard toric orbifold and dense-torus structure."""

from sage_extensions.all import *  # noqa: F401,F403


def _toric_projective_plane():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans.projective_space_fan().toric_variety(QQ)


def test_projective_plane_is_a_toric_orbifold() -> None:
    assert _toric_projective_plane().is_orbifold()


def test_projective_plane_is_weighted_projective_space_with_unit_weights() -> None:
    assert _toric_projective_plane().is_weighted_projective_space((1, 1, 1))


def test_projective_plane_dense_torus_has_dimension_two() -> None:
    assert _toric_projective_plane().torus().dimension() == 2
