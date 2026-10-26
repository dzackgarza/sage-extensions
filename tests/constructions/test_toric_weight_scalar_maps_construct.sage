r"""Scalar multiplication acts endomorphically on a toric weight complex and its cohomology."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_weight_scalar_cochain_map_is_an_endomorphism() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    weight = plane.character_lattice().zero()
    complex_ = plane.weight_cohomology_complex(divisor, weight)
    scalar_map = plane.weight_scalar_cochain_map(divisor, weight, QQ(2))

    assert scalar_map.domain() is complex_
    assert scalar_map.codomain() is complex_


def test_projective_plane_weight_scalar_cohomology_map_is_an_endomorphism() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    weight = plane.character_lattice().zero()
    cohomology = plane.weight_cohomology(divisor, weight, 0)
    scalar_map = plane.weight_scalar_cohomology_map(divisor, weight, 0, QQ(2))

    assert scalar_map.domain() is cohomology
    assert scalar_map.codomain() is cohomology
