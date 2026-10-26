r"""The integers satisfy the unital ring laws represented by Rings()."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integers_are_a_unital_ring() -> None:
    a, b, c = ZZ(2), ZZ(3), ZZ(5)

    assert ZZ in Rings()
    assert ZZ.one() * a == a
    assert a * ZZ.one() == a
    assert a * (b + c) == a * b + a * c
    assert (a + b) * c == a * c + b * c

