r"""The toric divisor-class sequence exposes its two canonical maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _toric_projective_plane():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans.projective_space_fan().toric_variety(QQ)


def test_projective_plane_character_divisor_map_has_the_standard_endpoints() -> None:
    plane = _toric_projective_plane()
    principal = plane.character_divisor_morphism()

    assert principal.domain() is plane.character_lattice()
    assert principal.codomain() is plane.torus_invariant_divisor_group()


def test_projective_plane_class_group_projection_has_the_standard_endpoints() -> None:
    plane = _toric_projective_plane()
    projection = plane.class_group_projection()

    assert projection.domain() is plane.torus_invariant_divisor_group()
    assert projection.codomain() is plane.class_group()
