r"""The integers carry the multiplicative magma structure inherited by rings."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_multiplication_is_an_owned_binary_operation() -> None:
    two = ZZ(2)
    three = ZZ(3)

    assert two * three == ZZ(6)
    assert isinstance(two * three, ZZ.ElementType)

