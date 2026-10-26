from sage_extensions.all import *


def points():
    return Set(("p", "q", "r"))


def free():
    r"""$\mathbb Z^{\{p, q, r\}}$: a divisor on three points is a formal sum $a p + b q + c r$."""
    return ZZ.free_module(points())


def test_the_divisor_group_on_three_points() -> None:
    divisors = DivisorGroups()(free())
    assert divisors in DivisorGroups()
    assert divisors in Modules(ZZ)
    assert divisors.module_rank() == 3


def test_the_weil_divisor_group_on_three_points() -> None:
    divisors = WeilDivisorGroups()(free())
    assert divisors in WeilDivisorGroups()
    assert divisors.module_rank() == 3


def test_the_cartier_divisor_group_on_three_points() -> None:
    divisors = CartierDivisorGroups()(free())
    assert divisors in CartierDivisorGroups()
    assert divisors.module_rank() == 3


def test_the_class_group_on_three_points() -> None:
    classes = ClassGroups()(free())
    assert classes in ClassGroups()
    assert classes.module_rank() == 3


def test_the_divisor_group_has_one_endomorphism_category() -> None:
    divisors = DivisorGroups()(free())
    endomorphisms = divisors.Mor(divisors)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert divisors.Mor(divisors) is endomorphisms
    assert identity * identity == identity
