r"""A formal divisor is a finite-support integral combination of prime labels."""

from sage_extensions.all import *  # noqa: F401,F403


def test_formal_divisor_from_terms() -> None:
    divisors = FormalDivisorGroups(ZZ)
    divisor = divisors.from_terms({"p": 2, "q": -1})

    assert divisor.parent() in FormalDivisorGroups(ZZ)
    assert divisor.parent().terms(divisor).cardinality() == cardinal(2)
    assert divisor + divisor == divisors.from_terms({"p": 4, "q": -2})
