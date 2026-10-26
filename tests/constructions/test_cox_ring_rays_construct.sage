r"""Cox-ring generators are indexed by the rays of the toric fan."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_cox_generators_match_fan_rays() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cox = plane.cox_ring()

    assert cox.cox_rays().cardinality() == cardinal(3)
    for label in cox.algebra_generating_set():
        ray = cox.cox_rays()[label]
        assert cox.generator_degree(label) == plane.divisor_class(
            plane.torus_invariant_prime_divisor(ray)
        )
