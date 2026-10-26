r"""Finite subsets of NN form a countable finite-power-set object."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_subsets_of_naturals() -> None:
    finite = NN.finite_subsets()

    assert finite in FinitePowerSets()
    assert finite.source() is NN
    assert finite.cardinality() == aleph0
