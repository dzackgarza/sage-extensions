r"""A toric weight cohomology piece agrees with its summand in total cohomology."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_zero_weight_cohomology_is_the_total_zero_weight_piece() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    weight = plane.character_lattice().zero()

    assert plane.weight_cohomology(divisor, weight, 0) is plane.line_bundle_cohomology(
        divisor, 0
    ).cohomology_weight_piece(weight)
