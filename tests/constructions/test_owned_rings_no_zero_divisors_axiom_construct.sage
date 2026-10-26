r"""The integers have no zero divisors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integers_are_a_domain() -> None:
    assert ZZ in IntegralDomains()
    assert ZZ(6) * ZZ(7) != ZZ.zero()

