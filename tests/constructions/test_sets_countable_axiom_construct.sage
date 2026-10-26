r"""The natural numbers lie in the countable refinement of Sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_naturals_are_countable() -> None:
    assert NN in Sets().Countable()
    assert NN in CountableSets()
    assert NN.cardinality() == aleph0
