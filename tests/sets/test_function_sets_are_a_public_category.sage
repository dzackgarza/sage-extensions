r"""The exponential of two sets is an object of the public ``FunctionSets``.

``FunctionSets`` is the essential image of the internal hom of sets, and
``FinitelySupportedFunctionSets`` names its finite-exponent part; the second was
a public name while the first, its supercategory, was not exported.  A consumer
stating ``functions in FunctionSets()`` could therefore not reach it at the
session surface even though the object was already placed there.
"""

from sage_extensions.all import FinitelySupportedFunctionSets, FunctionSets, Set, Sets


def test_the_exponential_of_two_sets_is_an_object_of_the_function_set_category() -> None:
    two = Sets.Δ[1]
    three = Set((1, 2, 3))
    functions = Sets().Mor(two, three)

    assert three.exponential(two) is functions
    assert functions in FunctionSets()
    assert functions in FinitelySupportedFunctionSets()


def test_a_finite_exponent_function_set_is_a_function_set() -> None:
    two = Sets.Δ[1]
    three = Set((1, 2, 3))

    assert FunctionSets()(three, two) in FunctionSets()
