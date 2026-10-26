r"""Owned monoids construct generated and predicate-defined submonoids."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_multiplicative_submonoids_have_the_expected_members() -> None:
    powers_of_two = ZZ.generated_submonoid((ZZ(2),), description="powers of two")
    nonnegative = ZZ.predicate_submonoid(lambda n: n >= 0, "nonnegative integers")

    assert ZZ(1) in powers_of_two
    assert ZZ(8) in powers_of_two
    assert ZZ(6) not in powers_of_two
    assert ZZ(0) in nonnegative
    assert ZZ(7) in nonnegative
    assert ZZ(-1) not in nonnegative

