r"""The natural numbers lie in the infinite refinement of Sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_naturals_are_infinite() -> None:
    assert NN in Sets().Infinite()
    assert NN not in Sets().Finite()
    assert NN.cardinality() == aleph0
