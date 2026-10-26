r"""The standard order on the rationals is compatible with addition and multiplication."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rationals_are_an_ordered_ring() -> None:
    a, b, c = QQ(1), QQ(2), QQ(3)

    assert QQ in OrderedRings()
    assert a < b
    assert a + c < b + c
    assert QQ.zero() <= a
    assert QQ.zero() <= b
    assert QQ.zero() <= a * b

