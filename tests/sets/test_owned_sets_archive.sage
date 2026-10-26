r"""Cantor: the power set of the natural numbers is uncountable."""

from sage_extensions.all import *


def test_archived_uncountable_sets_are_infinite_and_not_countable() -> None:
    continuum_set = NN.power_set()

    assert continuum_set in UncountableSets()
    assert continuum_set in InfiniteSets()
    assert continuum_set not in CountableSets()
    assert continuum_set not in CountablyInfiniteSets()
