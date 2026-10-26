r"""Integer multiplication exhibits the associative law of the semigroup layer."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_multiplication_is_associative() -> None:
    a, b, c = ZZ(2), ZZ(3), ZZ(5)

    assert (a * b) * c == a * (b * c)

