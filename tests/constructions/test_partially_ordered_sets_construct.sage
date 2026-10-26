r"""The natural numbers are a partially ordered set under their usual order."""

from sage_extensions.all import *  # noqa: F401,F403


def test_naturals_are_partially_ordered() -> None:
    ordered = PartiallyOrderedSets().an_object()

    assert ordered is NN
    assert ordered in PartiallyOrderedSets()
    assert ordered.le(NN(2), NN(5))
    assert not ordered.le(NN(5), NN(2))
