r"""The integers lie in the commutative no-zero-divisors refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integers_are_an_integral_domain() -> None:
    assert ZZ in IntegralDomains()
    assert ZZ.fraction_field() is QQ
    assert ZZ(6) * ZZ(7) != ZZ.zero()

