r"""The codimension-one toric cycle class map is CH^1 to integral H^2."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_cycle_class_isomorphism_has_canonical_endpoints() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cycle_class = plane.cycle_class_isomorphism(1)

    assert cycle_class.domain() is plane.chow_group(1)
    assert cycle_class.codomain() is plane.integral_singular_cohomology(2)
