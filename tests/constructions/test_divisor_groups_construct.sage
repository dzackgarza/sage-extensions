r"""Divisors on three named prime points form the free abelian group of rank three."""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_divisor_group_on_three_points() -> None:
    points = Set(("p", "q", "r"))
    free = ZZ.free_module(points)
    divisors = DivisorGroups()(free)

    assert divisors in DivisorGroups()
    assert divisors.module_rank() == 3
    assert divisors.module_generating_set().cardinality() == cardinal(3)
