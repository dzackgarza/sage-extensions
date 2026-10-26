r"""The natural numbers are an owned semiring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_natural_numbers_are_an_owned_semiring() -> None:
    a, b, c = NN(2), NN(3), NN(5)

    assert NN in OwnedSemirings()
    assert NN.zero() + a == a
    assert NN.one() * a == a
    assert a * (b + c) == a * b + a * c

