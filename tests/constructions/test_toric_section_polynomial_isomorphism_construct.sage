r"""Toric character sections identify linearly with homogeneous Cox-polynomial sections."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_section_polynomial_isomorphism_has_canonical_endpoints() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    comparison = plane.section_homogeneous_polynomial_isomorphism(divisor)

    assert comparison.domain() is plane.divisor_section_space(divisor)
    assert comparison.codomain() is plane.homogeneous_polynomial_section_space(divisor)
