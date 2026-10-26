r"""The toric Picard and Cartier-class maps have their canonical endpoints."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_picard_to_class_group_map_has_canonical_endpoints() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    comparison = plane.picard_to_class_group_morphism()

    assert comparison.domain() is plane.picard_group()
    assert comparison.codomain() is plane.class_group()


def test_projective_plane_cartier_class_projection_has_canonical_endpoints() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    projection = plane.torus_invariant_cartier_class_projection()

    assert projection.domain() is plane.torus_invariant_cartier_divisor_group()
    assert projection.codomain() is plane.picard_group()


def test_projective_plane_cartier_to_weil_map_has_canonical_endpoints() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    inclusion = plane.torus_invariant_cartier_to_weil_morphism()

    assert inclusion.domain() is plane.torus_invariant_cartier_divisor_group()
    assert inclusion.codomain() is plane.torus_invariant_divisor_group()
