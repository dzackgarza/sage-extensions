r"""A toric weight complex states the simplicial-cohomology comparison it represents."""

from sage_extensions.all import *  # noqa: F401,F403


def test_zero_weight_complex_retains_shifted_reduced_comparison() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    weight = plane.character_lattice().zero()
    complex_ = plane.weight_cohomology_complex(divisor, weight)

    assert "shifted reduced simplicial cohomology" in complex_.comparison_description()
