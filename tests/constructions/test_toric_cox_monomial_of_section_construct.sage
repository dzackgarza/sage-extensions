r"""A toric character section determines a homogeneous element of the Cox ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_character_section_has_a_cox_monomial() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    character = next(iter(plane.divisor_section_characters(divisor)))
    monomial = plane.cox_monomial_of_section(divisor, character)

    assert monomial in plane.cox_ring()
