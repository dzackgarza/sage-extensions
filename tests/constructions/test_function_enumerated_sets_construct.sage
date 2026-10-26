r"""Hermite-polynomial symbols form an enumerated function set."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hermite_polynomials_are_function_enumerated() -> None:
    functions = FunctionEnumeratedSets().an_object()

    assert functions in FunctionEnumeratedSets()
    assert functions in EnumeratedSets()
    assert functions.ranking_map()(functions[4]) == NN(4)
