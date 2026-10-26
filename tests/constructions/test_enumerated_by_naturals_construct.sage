r"""Hermite polynomials are indexed by the natural numbers."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hermite_polynomials_are_enumerated_by_naturals() -> None:
    functions = EnumeratedByNaturals().an_object()

    assert functions in EnumeratedByNaturals()
    assert functions.index_set() is NN
    assert functions.function(3) == functions[3]
    assert functions.cardinality() == aleph0
