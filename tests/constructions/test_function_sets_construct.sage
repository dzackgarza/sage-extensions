r"""Functions from a two-point set to a three-point set form a nine-element exponential."""

from sage_extensions.all import *  # noqa: F401,F403


def test_functions_from_two_points_to_three_points() -> None:
    two = Sets.Δ[1]
    three = Set((1, 2, 3))
    functions = Sets().Mor(two, three)

    assert functions in FunctionSets()
    assert functions.base() is three
    assert functions.exponent() is two
    assert functions.cardinality() == cardinal(9)
