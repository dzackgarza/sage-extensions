r"""A toric line-bundle weight is computed by its owned cochain complex."""

from sage_extensions.all import *  # noqa: F401,F403


def test_zero_weight_complex_for_a_line_on_projective_plane() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    weight = plane.character_lattice().zero()
    complex_ = plane.weight_cohomology_complex(divisor, weight)

    assert complex_ in ToricWeightCohomologyComplexes(QQ)
    assert complex_.cohomology_scheme() is plane
    assert complex_.cohomology_divisor() == divisor
    assert complex_.cohomology_weight() == weight
    assert complex_.cohomology(0).dimension() == 1
