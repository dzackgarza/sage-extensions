r"""A toric basis section descends to a compatible section on the affine atlas."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_basis_section_descends_compatibly() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    sections = plane.divisor_section_space(divisor)
    label = next(iter(sections.module_generating_set()))
    section = sections.module_generator(label)
    compatible = plane.compatible_divisor_section(divisor, section)

    assert compatible.line_bundle() is plane.invertible_sheaf_of_divisor(divisor)
