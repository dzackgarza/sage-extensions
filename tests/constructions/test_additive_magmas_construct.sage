r"""The integers carry the additive magma structure inherited by their stronger categories."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_addition_is_an_owned_binary_operation() -> None:
    two = ZZ(2)
    three = ZZ(3)

    assert two + three == ZZ(5)
    assert isinstance(two + three, ZZ.ElementType)

