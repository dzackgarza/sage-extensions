r"""The natural numbers are totally ordered."""

from sage_extensions.all import *  # noqa: F401,F403


def test_naturals_are_totally_ordered() -> None:
    ordered = TotallyOrderedSets().an_object()

    assert ordered is NN
    assert ordered in TotallyOrderedSets()
    assert ordered in PartiallyOrderedSets()
    assert ordered.le(NN(1), NN(3))
