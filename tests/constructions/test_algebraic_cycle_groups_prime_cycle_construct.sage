r"""A prime cycle is the corresponding basis generator of the cycle group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_toric_prime_cycle_is_cycle_group_generator() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cycles = plane.torus_invariant_cycle_group(1)
    prime = next(iter(cycles.module_generating_set()))

    assert cycles.prime_cycle(prime) == cycles.module_generator(prime)
