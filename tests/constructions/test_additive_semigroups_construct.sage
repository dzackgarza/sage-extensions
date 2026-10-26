r"""Integer addition exhibits the associative law of the additive-semigroup layer."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_addition_is_associative() -> None:
    a, b, c = ZZ(2), ZZ(3), ZZ(5)

    assert (a + b) + c == a + (b + c)

