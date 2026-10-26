r"""A nonzero hyperplane section on projective plane vanishes along a curve."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_section_zero_locus_has_dimension_one() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    sections = plane.divisor_section_space(divisor)
    label = next(iter(sections.module_generating_set()))
    section = sections.module_generator(label)
    zero_locus = plane.zero_subscheme_of_divisor_section(divisor, section)

    assert zero_locus.relative_dimension() == 1
