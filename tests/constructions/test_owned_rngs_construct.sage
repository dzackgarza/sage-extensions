r"""The integers lie on the owned rng spine before adjoining the unit structure."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integers_are_an_owned_rng() -> None:
    a, b, c = ZZ(2), ZZ(3), ZZ(5)

    assert ZZ in OwnedRngs()
    assert a + (-a) == ZZ.zero()
    assert (a * b) * c == a * (b * c)
    assert a * (b + c) == a * b + a * c

