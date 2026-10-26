r"""The integral middle-cohomology generator of projective plane has square one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_middle_cohomology_generator_has_square_one() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    hyperplane_class = plane.torus_invariant_cartier_class_projection()(
        plane.hyperplane_divisor()
    )
    chow_class = plane.picard_to_chow_isomorphism()(hyperplane_class)
    cohomology_class = plane.cycle_class_isomorphism(1)(chow_class)
    cup_product = plane.middle_cohomology_form()

    assert cup_product(cohomology_class, cohomology_class) == 1
