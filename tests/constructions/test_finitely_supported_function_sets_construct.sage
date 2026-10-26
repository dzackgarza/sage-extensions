r"""Every function on a finite exponent has finite support."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_exponent_function_set_is_finitely_supported() -> None:
    two = Sets.Δ[1]
    three = Set((1, 2, 3))
    functions = Sets().Mor(two, three)

    assert functions in FinitelySupportedFunctionSets()
    assert functions in FunctionSets()
    assert functions.cardinality() == cardinal(9)
