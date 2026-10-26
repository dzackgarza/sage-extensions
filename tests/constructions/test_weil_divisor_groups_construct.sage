r"""The three torus-invariant prime divisors freely generate a Weil divisor group on P^2."""

from sage_extensions.all import *  # noqa: F401,F403


def test_torus_invariant_weil_divisors_of_projective_plane() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisors = plane.weil_divisor_group()

    assert divisors in WeilDivisorGroups()
    assert divisors.divisor_scheme() is plane
    assert divisors.module_rank() == 3
    assert divisors.prime_divisor_locus().cardinality() == cardinal(3)
