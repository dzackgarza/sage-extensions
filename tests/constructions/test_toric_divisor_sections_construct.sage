r"""Sections of the hyperplane divisor are indexed by its lattice characters."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_has_three_section_characters() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    characters = plane.divisor_section_characters(plane.hyperplane_divisor())

    assert characters.cardinality() == cardinal(3)
    assert plane.character_lattice().zero() in characters
